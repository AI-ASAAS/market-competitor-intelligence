@echo off
chcp 65001 > nul
echo ================================================================
echo    مهندس تحليل الأعمال والمنافسين (Market & Competitor Intelligence)
echo    منظومة أساس للذكاء الاصطناعي (ASAAS AI)
echo ================================================================
echo.

if not exist "venv\Scripts\python.exe" (
    echo [1/3] جاري إنشاء البيئة الافتراضية وتثبيت المتطلبات...
    python -m venv venv
    call venv\Scripts\pip install -r requirements.txt
) else (
    echo [1/3] البيئة الافتراضية جاهزة.
)

echo [2/3] بناء الواجهة الأمامية بهوية أساس البصرية...
cd frontend
node ./node_modules/vite/bin/vite.js build
cd ..

echo.
echo [3/3] جاري تشغيل الخادم على الرابط: http://localhost:8008
echo.
echo يمكنك فتح الرابط في متصفحك: http://localhost:8008
echo للوصول إلى توثيق الـ API المباشر: http://localhost:8008/docs
echo.
start http://localhost:8008
.\venv\Scripts\python main.py
pause
