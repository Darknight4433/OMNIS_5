@echo off
echo ========================================
echo Git Commit - OMNIS Updates
echo ========================================
echo.

REM Check if git is initialized
if not exist ".git" (
    echo Initializing Git repository...
    git init
    git branch -M main
    git remote add origin https://github.com/Kavexa/OMNIS_ROBOT.git
) else (
    echo Updating remote URL...
    git remote set-url origin https://github.com/Kavexa/OMNIS_ROBOT.git
)

echo Adding all changes...
git add .

echo.
echo Creating commit...
REM Use simple one-line message to avoid batch errors
git commit -m "Fix: Conversation mode, greeting bug, API update, and documentation"

echo.
echo Pushing to GitHub...
REM Push HEAD to main branch (works even if local branch is master)
git push -u origin HEAD:main

echo.
echo ========================================
echo SUCCESS! Changes committed and pushed
echo ========================================
echo.
echo View at: https://github.com/Kavexa/OMNIS_ROBOT
echo.
pause
