from dotenv import load_dotenv
load_dotenv()  # STEP 1: Load environment variables

from fastapi import FastAPI
from backend.app.db.database import Base, engine
from backend.app.models.user import User
from backend.app.models.resume import Resume

from fastapi.openapi.utils import get_openapi
from backend.app.student.routes import router as student_router
from backend.app.recruiter.routes import router as recruiter_router
from backend.app.models.analysis import AnalysisResult
from backend.app.auth.routes import router as auth_router

app = FastAPI(
    title="Mimini Backend",
    description="JWT Authentication Backend",
    version="1.0.0",
)
Base.metadata.create_all(bind=engine)

# STEP 2: Register routers
app.include_router(auth_router)
app.include_router(student_router)

app.include_router(recruiter_router)

# STEP 3: Add Bearer token support to Swagger UI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # 🔐 Add Bearer Auth definition
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    # 🔒 Apply BearerAuth globally
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# STEP 4: Health check route
@app.get("/")
def root():
    return {"status": "Backend is running"}
