from graphene_django import DjangoObjectType
import graphene

from django.contrib.auth import get_user_model
from devlog.models import Project, Log

User = get_user_model()


class ProjectObj(DjangoObjectType):
    class Meta:
        model = Project


class LogObj(DjangoObjectType):
    class Meta:
        model = Log


class Query(graphene.ObjectType):
    logs = graphene.List(LogObj)
    projects = graphene.List(LogObj)

    def resolve_logs(self, info):
        return Log.objects.all()

    def resolve_project(self, info):
        return Project.objects.all()
