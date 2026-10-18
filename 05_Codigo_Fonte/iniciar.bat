@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "PY="
where py >nul 2>nul && set "PY=py"
if not defined PY where python >nul 2>nul && set "PY=python"
if defined PY goto rodar

echo O Python nao foi encontrado neste computador.
choice /C SN /M "Deseja instalar o Python agora (precisa de internet)"
if errorlevel 2 goto fim
where winget >nul 2>nul
if errorlevel 1 (
  echo O instalador automatico nao esta disponivel. Abrindo a pagina de download...
  start https://www.python.org/downloads/
  echo Instale marcando "Add Python to PATH" e depois de dois cliques neste arquivo de novo.
  goto fim
)
winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
echo.
echo Instalacao concluida. FECHE esta janela e de dois cliques em iniciar.bat novamente.
goto fim

:rodar
%PY% run.py

:fim
pause
