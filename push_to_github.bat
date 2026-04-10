@echo off
echo ==========================================
echo Pushing Code to GitHub
echo ==========================================

echo Adding all files...
git add .

echo Committing files...
git commit -m "Fixed Missing Font Error for Render Deployment"

echo Pushing to GitHub...
git push origin main

echo.
echo Process complete!
pause
