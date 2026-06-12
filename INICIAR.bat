@echo off
title Controle de Embarque
color 0A
cls

echo.
echo  ============================================
echo   CONTROLE DE EMBARQUE - GranServices
echo  ============================================
echo.

REM ── Tenta encontrar Python em varios lugares ──
set PYTHON=

REM Testa comando direto
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON=python
    goto :found
)

REM Testa py launcher (Windows Store / instalador oficial)
py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON=py
    goto :found
)

REM Testa caminhos comuns de instalacao
for %%P in (
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python39\python.exe"
    "C:\Python313\python.exe"
    "C:\Python312\python.exe"
    "C:\Python311\python.exe"
    "C:\Python310\python.exe"
    "C:\Python39\python.exe"
    "%ProgramFiles%\Python313\python.exe"
    "%ProgramFiles%\Python312\python.exe"
    "%ProgramFiles%\Python311\python.exe"
    "%ProgramFiles%\Python310\python.exe"
    "%APPDATA%\Python\Python313\python.exe"
) do (
    if exist %%P (
        set PYTHON=%%P
        goto :found
    )
)

REM Python nao encontrado
color 0C
echo  [ERRO] Python nao foi encontrado no seu computador!
echo.
echo  Para instalar o Python:
echo.
echo  1. Acesse: https://www.python.org/downloads/
echo  2. Clique em "Download Python"
echo  3. Execute o instalador
echo  4. IMPORTANTE: marque "Add Python to PATH"
echo  5. Clique em "Install Now"
echo  6. Feche e abra o INICIAR.bat novamente
echo.
echo  OU abra esta pagina no navegador agora:
start https://www.python.org/downloads/
echo.
pause
exit /b 1

:found
echo  [OK] Python encontrado: %PYTHON%
echo.

REM ── Instala Flask se necessario ──
echo  Verificando Flask...
%PYTHON% -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo  Instalando Flask, aguarde...
    echo.
    %PYTHON% -m pip install flask --quiet --disable-pip-version-check
    if errorlevel 1 (
        color 0C
        echo.
        echo  [ERRO] Nao foi possivel instalar o Flask.
        echo  Tente abrir o Prompt de Comando como Administrador
        echo  e execute: pip install flask
        echo.
        pause
        exit /b 1
    )
    echo  [OK] Flask instalado!
) else (
    echo  [OK] Flask ja instalado
)
echo.

REM ── Abre navegador apos 3 segundos ──
echo  Iniciando servidor...
echo.
start "" cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:5000"

color 0B
echo  ============================================
echo   Acesse: http://localhost:5000
echo.
echo   Deixe esta janela aberta enquanto usar.
echo   Para encerrar: feche esta janela ou Ctrl+C
echo  ============================================
echo.

REM ── Inicia Flask ──
%PYTHON% app.py

echo.
color 07
echo  Servidor encerrado. Pressione qualquer tecla para fechar.
pause >nul
