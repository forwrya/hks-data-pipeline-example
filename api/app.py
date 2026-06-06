from fastapi import FastAPI

from routes import readings_route

app = FastAPI()
app.include_router(readings_route.router)