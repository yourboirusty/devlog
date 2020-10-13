from graphene_django import DjangoObjectType
import graphene

from django.contrib.auth import get_user_model
from devlog.models import Project, Log

User = get_user_model()


class ProjectObj(DjangoObjectType):
    class Meta:
        model = Project
        fields = ("id", "name", "admin", "contributors", "description")


class LogObj(DjangoObjectType):
    class Meta:
        model = Log
        fields = ("id", "author", "project", "date", "content", "important")


class Query(graphene.ObjectType):
    logs = graphene.List(LogObj)
    projects = graphene.List(ProjectObj)

    def resolve_logs(self, info):
        return Log.objects.all()

    def resolve_projects(self, info):
        return Project.objects.all()


schema = graphene.Schema(query=Query)
