@echo off
echo ==========================================
echo Pushing Code to GitHub
echo ==========================================

echo Initializing Git repository...
git init

echo Adding all files...
git add .

echo Committing files...
git commit -m "Deployment ready app with auto-PDF generation"

echo Setting branch to main...
git branch -M main

echo Adding remote repository...
git remote remove origin 2>nul
git remote add origin https://github.com/kuldeeppanwar02/invitation-guest-name-pdf.git

echo Pushing to GitHub...
git push -u origin main --force

echo.
echo Process complete!
pause
