from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from warnings import warn

if not settings.AUTH_USER_MODEL:
    warn("AUTH_USER_MODEL not set! Devlog may not function correctly.")


class ContentChange(models.Model):
    """
    Abstract class to track changes to a field on an object.
    Needs to have field "model" implemented before usage.
    Default field track: CharField.
    """
    model = NotImplemented
    previous = models.CharField(_("Field before the change."),
                                max_length=500,
                                help_text="Field before the change." +
                                "Defaults to max 500 CharField." +
                                "Can be overriten."
                                )
    date = models.DateTimeField(_("Date of modification"),
                                auto_now_add=True,
                                help_text="Date of change."
                                )
    last_change = models.ForeignKey('self',
                                    blank=True,
                                    null=True,
                                    on_delete=models.CASCADE
                                    )

    class Meta:
        abstract = True
        ordering = ['date']

    def __str__(self):
        return "{0} - {1}".format(self.date, self.model)

    @staticmethod
    def change(cls, model, change):
        """
        Track a change on an object.
        model: object to track,
        change: original value,
        """
        last = cls.objects.filter(model=model).first()
        if not last:
            tracked = cls(model=model, previous=change)
        else:
            tracked = cls(model=model, previous=change, last_change=last)
        tracked.save()
        return tracked


class Project(models.Model):
    """
    Project is used to store important information about devlog projects.
    """
    slug = models.SlugField(_("URL slugfield"),
                            help_text="Short label, generated based on " +
                            "project name. Uses default django.utils.slugify",
                            )
    name = models.CharField(max_length=64,
                            verbose_name=_("Project name"),
                            help_text="Project name, max length 64"
                            )
    admin = models.ForeignKey(settings.AUTH_USER_MODEL,
                              verbose_name=_("Project administrator"),
                              on_delete=models.CASCADE,
                              help_text="Project admin, has the ability to " +
                              "add and remove logs, contributors, change " +
                              "project description and delete the project. " +
                              "Uses settings.AUTH_USER_MODEL to determine " +
                              "correct user model to utilize.",
                              )
    contributors = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                          verbose_name=(
                                              "Project contributors"
                                              ),
                                          related_name="devlog_contribs",
                                          help_text="Contributors can add " +
                                          "logs to the projects. They can " +
                                          "delete their own logs. Uses " +
                                          "settings.AUTH_USER_MODEL."
                                          )
    description = models.CharField(_("Project description"),
                                   max_length=500,
                                   help_text="Project description, can be " +
                                   "changed only by admin"
                                   )

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")

    def __str__(self):
        return "{0} by {1}".format(self.name, self.admin)


@receiver(post_save, sender=Project)
def project_saved(sender, instance, created, **kwargs):
    """
    Adds random slug to :model:`devlog.Log` upon creation.
    """
    if created:
        instance.slug = slugify(instance.name)
        instance.save()


class Log(models.Model):
    """
    Log is used to store short text correlated to a :model:`devlog.Project`.
    """
    slug = models.SlugField(_("URL slugfield"),
                            help_text="Short label, generated randomly")
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               verbose_name=_("Author"),
                               on_delete=models.CASCADE,
                               help_text="Author of the log." +
                               "Uses settings.AUTH_USER_MODEL"
                               )
    project = models.ForeignKey("devlog.Project",
                                verbose_name=_("Project"),
                                related_name="logs",
                                on_delete=models.CASCADE,
                                help_text="Project the log is related to."
                                )
    date = models.DateTimeField(_("Date"),
                                auto_now_add=True,
                                help_text="Date the log was created."
                                )
    content = models.CharField(_("Log"),
                               max_length=256,
                               help_text="Log content."
                               )
    important = models.BooleanField(_("Important"),
                                    default=False,
                                    help_text="Marks Log as important.")

    class Meta:
        verbose_name = _("Log")
        verbose_name = _("Logs")
        ordering = ['date']

    def __str__(self):
        return "{0}: {1} on {2}".format(self.date, self.author, self.project)


@receiver(pre_save, sender=Log)
def log_validation(sender, instance, update_fields, **kwargs):
    """
    Validates :model:`devlog.Log` before saving to check if
    author wasn't modified and author is set as project
    contributors or is an admin. Logs changes to content.
    """
    if update_fields:
        if "project" in update_fields:
            raise ValidationError("Project cannot be changed.")
        if "author" in update_fields:
            try:
                previous = Log.objects.get(id=instance.id)
                if instance.author != previous.author:
                    raise ValidationError("Author cannot be changed.")
            except Log.DoesNotExist:
                if (instance.author not in instance.project.contributors.all()
                   or instance.author not in instance.project.admin):
                    raise ValidationError("Author not in the project.")
        if "content" in update_fields:
            warn("Content of {0} has been modified!".format(instance))


@receiver(post_save, sender=Log)
def log_saved(sender, instance, created, **kwargs):
    """
    Adds random slug to :model:`devlog.Log` upon creation.
    """
    if created:
        instance.slug = get_random_string(6)
