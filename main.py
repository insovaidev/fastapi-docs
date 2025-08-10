from fastapi import FastAPI
from database import Base, engine
from routes import user as user_routes
from routes import test as test_routes

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(user_routes.router)
app.include_router(test_routes.router)

@app.get("/")
def root():
    return {"message": "FastAPI CRUD with MySQL is running"}
