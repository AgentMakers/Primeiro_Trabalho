@echo off
REM Script para iniciar Qdrant no Docker (Windows)

echo =====================================
echo   Iniciando Qdrant no Docker
echo =====================================
echo.

REM Verificar se Docker está instalado
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Docker nao esta instalado!
    echo.
    echo Instale o Docker Desktop:
    echo https://docs.docker.com/desktop/install/windows-install/
    echo.
    pause
    exit /b 1
)

echo [OK] Docker encontrado
echo.

REM Verificar se container já existe
docker ps -a | findstr qdrant-rag >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Container 'qdrant-rag' ja existe.
    echo.

    REM Verificar se está rodando
    docker ps | findstr qdrant-rag >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo [INFO] Qdrant ja esta rodando!
        echo.
    ) else (
        echo [INFO] Iniciando container existente...
        docker start qdrant-rag
        if %ERRORLEVEL% EQU 0 (
            echo [OK] Qdrant iniciado com sucesso!
            echo.
        ) else (
            echo [ERRO] Falha ao iniciar Qdrant
            pause
            exit /b 1
        )
    )
) else (
    echo [INFO] Criando novo container Qdrant...
    echo.

    REM Criar diretório de storage se não existir
    if not exist "rag\qdrant_storage" (
        echo [INFO] Criando diretorio rag\qdrant_storage...
        mkdir rag\qdrant_storage
    )

    REM Rodar container
    docker run -d ^
      --name qdrant-rag ^
      -p 6333:6333 ^
      -p 6334:6334 ^
      -v "%cd%\rag\qdrant_storage:/qdrant/storage" ^
      --restart unless-stopped ^
      qdrant/qdrant:latest

    if %ERRORLEVEL% EQU 0 (
        echo [OK] Qdrant criado e iniciado com sucesso!
        echo.
    ) else (
        echo [ERRO] Falha ao criar container Qdrant
        pause
        exit /b 1
    )
)

REM Aguardar Qdrant iniciar (max 30 segundos)
echo [INFO] Aguardando Qdrant inicializar...
set /a contador=0
:loop
timeout /t 1 /nobreak >nul
curl -s http://localhost:6333/ >nul 2>nul
if %ERRORLEVEL% EQU 0 goto ready
set /a contador+=1
if %contador% LSS 30 goto loop

echo [AVISO] Timeout aguardando Qdrant. Verifique os logs.
echo.
goto show_info

:ready
echo [OK] Qdrant esta pronto!
echo.

:show_info
echo =====================================
echo   Qdrant Rodando!
echo =====================================
echo.
echo  Dashboard:  http://localhost:6333/dashboard
echo  API:        http://localhost:6333
echo.
echo Comandos uteis:
echo   Ver logs:       docker logs -f qdrant-rag
echo   Parar:          docker stop qdrant-rag
echo   Reiniciar:      docker restart qdrant-rag
echo   Remover:        docker rm -f qdrant-rag
echo.
echo Para iniciar a aplicacao:
echo   streamlit run app_01.py
echo.
echo =====================================

REM Perguntar se deseja abrir o dashboard
set /p ABRIR="Abrir dashboard no navegador? (S/N): "
if /i "%ABRIR%"=="S" (
    start http://localhost:6333/dashboard
)

pause
