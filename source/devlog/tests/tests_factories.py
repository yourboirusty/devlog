from devlog.factories import UserFactory, ProjectFactory, LogFactory
from django.test import TestCase
from collections import defaultdict
from django.contrib.auth import get_user_model
User = get_user_model()


BATCH_SIZE = 15


class UserFactoryTestCase(TestCase):
    def setUp(self):
        self.users = UserFactory.create_batch(BATCH_SIZE)

    def testUserCreation(self):
        for user in self.users:
            self.assertIsNotNone(user.id)
            # Username is built from name and surname
            self.assertIsNotNone(user.username)

    def testRandomUserNames(self):
        names = defaultdict(int)
        for user in self.users:
            names[user.username] += 1
        for username_count in names.values():
            self.assertEqual(username_count, 1)


class ProjectFactoryTestCase(TestCase):
    def setUp(self):
        self.projects = ProjectFactory.create_batch(BATCH_SIZE)

    def testProjectCreation(self):
        for project in self.projects:
            self.assertIsNotNone(project.id)
            self.assertIsNotNone(project.admin.id)

    def testProjectNames(self):
        names = defaultdict(int)
        for project in self.projects:
            names[project.name] += 1
        for name_count in names.values():
            self.assertEqual(name_count, 1)


class ProjectFactoryContributorsTestCase(TestCase):
    def setUp(self):
        self.users = UserFactory.create_batch(BATCH_SIZE)
        self.project = ProjectFactory.create(contributors=self.users)

    def testCreatingProjectWithContributors(self):
        self.assertIsNotNone(self.project.id)

    def testAddingContributors(self):
        project_contributors = self.project.contributors.all()
        self.assertEqual(list(project_contributors), self.users)


class LogFactoryTestCase(TestCase):
    def setUp(self):
        self.log = LogFactory()

    def testLogCreation(self):
        self.assertIsNotNone(self.log.project.id)
        self.assertIsNotNone(self.log.project.admin.id)

        self.assertIsNotNone(self.log.author.id)
        self.assertIsNotNone(self.log.content)

    def testLogAuthor(self):
        self.assertEqual(self.log.project.admin, self.log.author)
