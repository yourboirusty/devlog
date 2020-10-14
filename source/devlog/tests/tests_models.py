from django.test import TestCase
from django.core.exceptions import ValidationError

from devlog.factories import UserFactory, ProjectFactory, LogFactory
from django.utils.text import slugify



BATCH_SIZE = 15


class ProjectTestCase(TestCase):
    def setUp(self):
        self.project = ProjectFactory()

    def testSlugs(self):
        self.assertEqual(self.project.slug, slugify(self.project.name))


class LogTestCase(TestCase):
    def setUp(self):
        self.log = LogFactory()

    def testSlugs(self):
        self.assertIsNotNone(self.log.slug)

    def testProjectChangeValidation(self):
        new_project = ProjectFactory()
        self.log.project = new_project
        self.assertRaisesMessage(ValidationError,
                                 "Project cannot be changed.",
                                 self.log.save, update_fields=["project"]
                                 )

    def testAuthorChangeValidation(self):
        project = self.log.project
        other_project_member = UserFactory(project=project)
        self.log.author = other_project_member
        self.assertRaisesMessage(ValidationError,
                                 "Author cannot be changed.",
                                 self.log.save, update_fields=["author"])

    def testAuthorInProjectValidation(self):
        new_user = UserFactory()
        old_project = self.log.project
        with self.assertRaisesMessage(ValidationError,
                                      "Author not in the project."):
            LogFactory(project=old_project,
                       author=new_user,
                       content="test")

    def testUpdateWarning(self):
        self.log.content = ""
        with self.assertWarns(UserWarning):
            self.log.save(update_fields=["content"])
