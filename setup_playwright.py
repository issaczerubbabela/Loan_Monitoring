# Setup script for Playwright
# Run this script to install Playwright and its browser dependencies

import subprocess
import sys

def install_playwright():
    """Install Playwright and its browser dependencies"""
    try:
        print("Installing Playwright...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
        
        print("Installing Playwright browsers...")
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
        
        print("Playwright setup completed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"Error installing Playwright: {e}")
        print("Please run the following commands manually:")
        print("pip install playwright")
        print("playwright install chromium")

if __name__ == "__main__":
    install_playwright()
