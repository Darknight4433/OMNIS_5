@echo off
echo ========================================
echo Force Fix GitHub Push
echo ========================================
echo.

echo 1. Stopping git from tracking sensitive files...
git rm --cached run_omnis.bat
git rm --cached run_omnis.sh

echo.
echo 2. Resetting recent commits (soft reset)...
REM Go back 2 commits to be safe, keeping file changes
git reset --soft HEAD~2

echo.
echo 3. Adding files (ignoring sensitive ones)...
git add .

echo.
echo 4. Committing clean version...
git commit -m "Fix: Setup files and conversation mode (clean)"

echo.
echo 5. Pushing to GitHub...
git push -u origin HEAD:main

echo.
echo ========================================
echo SUCCESS! 
echo ========================================
echo NOTE: run_omnis.bat and run_omnis.sh are now ignored by git.
echo You can safely edit them with your API key, they won't be uploaded.
echo.
pause
