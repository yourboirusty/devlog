import factory
from devlog.models import Project, Log
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """
    Simple randomized user factory. Assumes model has `first_name`,
    `last_name` and `username` fields.
    """
    class Meta:
        model = User

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    # Without LazyAttribute username will be generated once
    username = factory.LazyAttribute(
        lambda x: (x.first_name + '.' + x.last_name).lower()
        )
    is_staff = False
    is_superuser = False


class SuperUserFactory(UserFactory):
    """
    Simple randomized superuser factory. Assumes model has `first_name`,
    `last_name` and `username` fields. Sets `is_superuser` and `is_staff`
    to `True`.
    """
    is_staff = True
    is_superuser = True


class ProjectFactory(factory.django.DjangoModelFactory):
    """
    Factory for :model:`devlog.Project` objects.
    Can be called with additional "contributors" argument to add
    users to contributor list upon creation.
    Example:
        ProjectFactory() or ProjectFactory.build()-> returns a Project
            object without contributors.
        ProjectFactory().create(contributors=(contributor1, contributor2) ->
            returns a project with defined contributors.)
    """
    class Meta:
        model = Project

    name = factory.Sequence(lambda n: "Project " + str(n))
    description = factory.Faker('text', max_nb_chars=200)
    admin = factory.SubFactory(UserFactory)

    @factory.post_generation
    def contributors(self, create, extracted, **kwargs):
        """
        Adds contributors passed in arguments after model creation.
        """
        if not create:
            return

        if extracted:
            for contributor in extracted:
                self.contributors.add(contributor)


class LogFactory(factory.django.DjangoModelFactory):
    """
    Factory for :model:`devlog.Log` objects.
    Default values:
        author - project admin
        project - randomly generated project
        content - random 256 char lorem ipsum
        important - false
    """
    class Meta:
        model = Log

    project = factory.SubFactory(ProjectFactory)
    author = factory.LazyAttribute(
        lambda x: (x.project.admin)
    )
    content = factory.Faker('text', max_nb_chars=256)
