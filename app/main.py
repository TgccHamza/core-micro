from fastapi import FastAPI
from .database import engine, Base
from .routers import project
from .routers import arena

#Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(project.router, tags=["projects"])
app.include_router(arena.router, tags=["arenas"])
