from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from settings import Settings

from routes.readings_route import ReadingsRoute
from views.readings_view import ReadingsView
from models.readings_model import ReadingsModel

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

app = FastAPI()
settings = Settings()

# Database connection
db_engine = create_async_engine(settings.db_connection_string)
session_maker = async_sessionmaker(db_engine, expire_on_commit=False)

print("Ready to make database connections")

# Models
readings_model = ReadingsModel(session_maker)

print("Created models")

# Views
readings_view = ReadingsView(readings_model)

print("Created views")

# Routes
readings_route = ReadingsRoute(readings_view)
app.include_router(readings_route.router)

print("Created routes")

# Middleware
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Misc. routes
@app.get("/ping")
def ping():
    return "pong"