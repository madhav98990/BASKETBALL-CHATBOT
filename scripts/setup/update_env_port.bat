@echo off
REM Update .env file to use port 5433
if exist .env (
    powershell -Command "(Get-Content .env) -replace 'DB_PORT=5432', 'DB_PORT=5433' | Set-Content .env"
    echo ✅ Updated .env file to use port 5433
) else (
    echo ❌ .env file not found. Run setup_docker.bat first.
)

