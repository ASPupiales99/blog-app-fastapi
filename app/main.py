from dotenv import load_dotenv
from fastapi import FastAPI

from app.core.db import Base, engine

load_dotenv()


# dev


def create_app() -> FastAPI:
    app = FastAPI(title="Mini Blog")
    Base.metadata.create_all(bind=engine)
