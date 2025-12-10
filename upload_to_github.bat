@echo off
echo ========================================
echo OMNIS GitHub Upload Script
echo ========================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed!
    echo Please install Git from: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo Step 1: Initializing Git repository...
git init

echo.
echo Step 2: Adding all files...
git add .

echo.
echo Step 3: Creating first commit...
git commit -m "Initial commit: OMNIS Robot v1.0 - Face recognition and voice assistant"

echo.
echo Step 4: Setting main branch...
git branch -M main

echo.
echo Step 5: Configuring remote repository...
git remote add origin https://github.com/Kavexa/OMNIS_ROBOT.git >nul 2>&1
git remote set-url origin https://github.com/Kavexa/OMNIS_ROBOT.git

echo.
echo Step 6: Pushing to GitHub...
echo NOTE: You may be asked to login to GitHub
git push -u origin main

echo.
echo ========================================
echo SUCCESS! Code uploaded to GitHub
echo ========================================
echo.
echo View your repository at:
echo https://github.com/Kavexa/OMNIS_ROBOT
echo.
pause
