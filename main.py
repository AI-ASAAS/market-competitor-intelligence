import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
from core.config import settings
from core.database import init_db
from modules.analysis.router import router as analysis_router

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # بدء تشغيل التطبيق
    logger.info("Initializing %s v%s...", settings.APP_NAME, settings.APP_VERSION)
    os.makedirs(os.path.dirname(settings.DATABASE_PATH), exist_ok=True)
    await init_db()
    yield
    # إيقاف التطبيق
    logger.info("Shutting down %s...", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="نظام ذكاء تنافسي متقدم لوكلاء الذكاء الاصطناعي — منظومة أساس",
    lifespan=lifespan
)

# إعداد CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# تسجيل الروابط
app.include_router(analysis_router)

# التحقق من وجود مجلد الواجهة الأمامية المبني
dist_path = os.path.join(os.path.dirname(__file__), "frontend", "dist")
if os.path.exists(dist_path):
    app.mount("/", StaticFiles(directory=dist_path, html=True), name="frontend")
else:
    @app.get("/")
    async def root_info():
        return {
            "message": "مرحباً بك في نظام مهندس تحليل الأعمال والمنافسين (Market & Competitor Intelligence Specialist)",
            "status": "online",
            "docs": "/docs",
            "api": "/api/status",
            "frontend_dev": "http://localhost:5173"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
