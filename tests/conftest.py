import asyncio

import pytest
import graphene
from graphene_file_upload.scalars import Upload
from starlette.applications import Starlette
from starlette.testclient import TestClient

from starlette_graphene3 import GraphQLApp


class User(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()


class Query(graphene.ObjectType):
    me = graphene.Field(User)
    user = graphene.Field(User, id=graphene.ID(required=True))
    user_async = graphene.Field(User, id=graphene.ID(required=True))

    def resolve_me(root, info):
        return {"id": "john", "name": "John"}

    def resolve_user(root, info, id):
        return {"id": id, "name": id.capitalize()}

    async def resolve_user_async(root, info, id):
        return {"id": id, "name": id.capitalize()}


class FileUploadMutation(graphene.Mutation):
    class Arguments:
        file = Upload(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, file, **kwargs):
        return FileUploadMutation(ok=True)


class Mutation(graphene.ObjectType):
    upload_file = FileUploadMutation.Field()


class Subscription(graphene.ObjectType):
    count = graphene.Int(upto=graphene.Int())
    raiseError = graphene.Int()

    async def subscribe_count(root, info, upto=3):
        for i in range(upto):
            yield {'count': i}
            await asyncio.sleep(0.01)

    async def subscribe_raiseError(root, info):
        raise ValueError
        yield None


@pytest.fixture
def schema():
    return graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription)


@pytest.fixture
def client(schema):
    app = Starlette()
    app.mount("/", GraphQLApp(schema))
    return TestClient(app)


app = Starlette()
app.mount("/", GraphQLApp(graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription)))
