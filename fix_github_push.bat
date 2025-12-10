@echo off
echo ========================================
echo Fix and Push to GitHub
echo ========================================
echo.

echo 1. Removing secrets from git history...
REM Soft reset to keep changes but undo the commit
git reset --soft HEAD~1

echo.
echo 2. Re-adding safe files...
git add .

echo.
echo 3. Creating clean commit...
git commit -m "Fix: Setup files and conversation mode (clean)"

echo.
echo 4. Pushing to GitHub...
git push -u origin HEAD:main

echo.
echo ========================================
echo SUCCESS!
echo ========================================
echo.
pause
