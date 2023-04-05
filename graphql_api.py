import graphene
import psutil
from fastapi import FastAPI
from starlette_graphene3 import GraphQLApp

class SystemMetrics(graphene.ObjectType):
    cpu_percent = graphene.Float()
    memory_usage = graphene.Float()
    disk_usage = graphene.Float()

class Query(graphene.ObjectType):
    system_metrics = graphene.Field(SystemMetrics)

    def resolve_system_metrics(self, info):
        return SystemMetrics(
            cpu_percent=psutil.cpu_percent(),
            memory_usage=psutil.virtual_memory().percent,
            disk_usage=psutil.disk_usage('/').percent
        )

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

app.add_route("/graphql", GraphQLApp(schema=graphene.Schema(query=Query)))

# uvicorn graphql_api:app