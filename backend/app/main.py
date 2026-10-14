from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.api import auth, students, jobs, courses, matching, recommendations
from app.db_seeder import seed_database_if_empty

# Create tables automatically for database
Base.metadata.create_all(bind=engine)

# Auto-seed initial benchmark data if database is empty
with SessionLocal() as db_session:
    seed_database_if_empty(db_session)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="NEXUS - Next-generation Employability, eXpertise & Upskilling System API"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(students.router, prefix=settings.API_V1_STR)
app.include_router(jobs.router, prefix=settings.API_V1_STR)
app.include_router(courses.router, prefix=settings.API_V1_STR)
app.include_router(matching.router, prefix=settings.API_V1_STR)
app.include_router(recommendations.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "ONLINE",
        "docs_url": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "HEALTHY"}
