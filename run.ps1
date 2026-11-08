# ================================================================
# مهندس تحليل الأعمال والمنافسين (Market & Competitor Intelligence)
# منظومة أساس للذكاء الاصطناعي (ASAAS AI)
# ================================================================

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "   مهندس تحليل الأعمال والمنافسين (Market & Competitor Intelligence)" -ForegroundColor Yellow
Write-Host "   منظومة أساس للذكاء الاصطناعي (ASAAS AI)" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "[1/3] جاري إنشاء البيئة الافتراضية وتثبيت المتطلبات..." -ForegroundColor Yellow
    python -m venv venv
    .\venv\Scripts\pip install -r requirements.txt
} else {
    Write-Host "[1/3] البيئة الافتراضية متوفرة وجاهزة." -ForegroundColor Green
}

Write-Host "[2/3] بناء الواجهة الأمامية بهوية أساس..." -ForegroundColor Yellow
Set-Location -LiteralPath "frontend"
node ./node_modules/vite/bin/vite.js build
Set-Location -LiteralPath ".."

Write-Host ""
Write-Host "[3/3] تشغيل الخادم على الرابط: http://localhost:8008" -ForegroundColor Green
Write-Host "توثيق Swagger API متاح على: http://localhost:8008/docs" -ForegroundColor Cyan
Write-Host ""

Start-Process "http://localhost:8008"
.\venv\Scripts\python main.py
