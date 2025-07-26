@echo off
echo ============================================
echo 🚀 AMA MESSAGE - Sistema de SMS
echo ============================================
echo 📱 Iniciando servidor...
echo 🌐 Acesse: http://127.0.0.1:8000
echo 📚 API Docs: http://127.0.0.1:8000/docs
echo ============================================
echo.

cd /d "w:\projects\AMAMESSAGE"
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

pause
