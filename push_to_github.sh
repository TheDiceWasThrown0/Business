#!/bin/bash
if [ -z "$1" ]; then
    echo "Usage: ./push_to_github.sh <YOUR_GITHUB_REPO_URL>"
    echo "Example: ./push_to_github.sh https://github.com/username/horror_reels.git"
    exit 1
fi

echo "Adding remote origin..."
git remote add origin $1

echo "Pushing to main..."
git branch -M main
git push -u origin main

echo "Done! Now go to Render/Railway and connect this repo."
