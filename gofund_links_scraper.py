#! /usr/bin/env python3

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

import pandas as pd
import time
import os
import csv

# Initialize variables
CATEGORIES = []
CAMPAIGNS = []
M_CAMPAIGN = []
TITLE = []
PROGRESS = []
STORY = []
STATS = []
CREATED_DATE = []

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-dev-shm-usage")
# Uncomment the line below if you want to run headless
chrome_options.add_argument("--headless=new")

# Initialize webdriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Base URL
url = 'https://www.gofundme.com/discover'

def init_browser():
    """Initialize browser and navigate to base URL"""
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    print("Browser initialized and navigated to", url)

def show_all_categories():
    """Make sure all categories are loaded on page"""
    try:
        show_all = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Show all categories')]"))
        )
        show_all.click()
        print("All categories loaded.")
    except (TimeoutException, NoSuchElementException):
        print("Could not find 'Show all categories' or already showing all categories.")

def get_category_links():
    """Create function to get all CATEGORY links from url"""
    # Hardcoded category URLs since the site structure has changed
    category_urls = [
        "/discover/medical-fundraiser",
        "/discover/memorial-fundraiser", 
        "/discover/emergency-fundraiser",
        "/discover/education-fundraiser",
        "/discover/nonprofit-fundraiser",
        "/discover/animal-fundraiser",
        "/discover/environment-fundraiser",
        "/discover/business-fundraiser",
        "/discover/community-fundraiser",
        "/discover/competition-fundraiser",
        "/discover/creative-fundraiser",
        "/discover/event-fundraiser",
        "/discover/faith-fundraiser",
        "/discover/family-fundraiser",
        "/discover/sports-fundraiser",
        "/discover/travel-fundraiser",
        "/discover/volunteer-fundraiser",
        "/discover/wishes-fundraiser"
    ]
    
    # Clear existing categories and add the hardcoded ones
    CATEGORIES.clear()
    base_url = "https://www.gofundme.com"
    
    for cat_url in category_urls:
        CATEGORIES.append(base_url + cat_url)
        print(f"Added category: {cat_url}")
    
    print(f"\nTotal {len(CATEGORIES)} CATEGORIES\n")

def click_show_more():
    """Attempt to click 'Show more' button using multiple strategies"""
    try:
        # First try: Look for button by text content
        buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Show more')]")
        if buttons:
            # Scroll to button
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", buttons[0])
            time.sleep(1)
            buttons[0].click()
            #print("Clicked 'Show more' button (text content match)")
            return True
            
        # Second try: Look for any button with 'more' in text
        buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'more')]")
        if buttons:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", buttons[0])
            time.sleep(1)
            buttons[0].click()
            #print("Clicked button containing 'more'")
            return True
            
        # Third try: Look for specific div/span that might contain the button
        show_more_containers = driver.find_elements(By.XPATH, "//div[contains(@class, 'show-more') or contains(@class, 'load-more')]")
        if show_more_containers:
            for container in show_more_containers:
                try:
                    button = container.find_element(By.TAG_NAME, "button")
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                    time.sleep(1)
                    button.click()
                   # print("Clicked button in show-more container")
                    return True
                except (NoSuchElementException, StaleElementReferenceException):
                    continue
                    
        #print("No 'Show more' button found using standard methods")
        return False
        
    except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
        print(f"Error clicking 'Show more': {e}")
        return False

def extract_campaign_links():
    """Extract all campaign links from the current page"""
    initial_count = len(CAMPAIGNS)
    
    try:
        # Wait for the page to load campaigns
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/f/')]"))
        )
        
        # Direct selenium approach
        campaign_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/f/')]")
        for link in campaign_links:
            href = link.get_attribute('href')
            if href and '/f/' in href and href not in CAMPAIGNS:
                CAMPAIGNS.append(href)
                
        # BeautifulSoup approach as backup
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for campaign cards
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '/f/' in href:
                full_url = href if href.startswith('http') else f"https://www.gofundme.com{href}"
                if full_url not in CAMPAIGNS:
                    CAMPAIGNS.append(full_url)
        
        new_links = len(CAMPAIGNS) - initial_count
        #print(f"Found {new_links} new campaign links (total: {len(CAMPAIGNS)})")
                
        return new_links > 0
        
    except TimeoutException:
        print("Timed out waiting for campaign links to load")
        return False

def save_links():
    """Save links to text file."""
    with open("campaign_links.txt", "w") as file:
        for i in CAMPAIGNS:
            file.write(i)
            file.write("\n")
    print(f"\nSaved {len(CAMPAIGNS)} links to campaign_links.txt\n")

def load_campaigns_for_category(category_url):
    """Load all campaigns for a specific category"""
    #print(f"\nLoading: {category_url}")
    driver.get(category_url)
    time.sleep(5)  # Initial page load wait
    
    # Extract initial links
    extract_campaign_links()
    
    # Scroll and click "Show more" multiple times
    for attempt in range(10):
        try:
            # Scroll to bottom to trigger lazy loading
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 300);")
            time.sleep(2)
            
            # Try to click "Show more" button
            if not click_show_more():
                #print("No more 'Show more' button found")
                break
                
            time.sleep(3)  # Wait for new content
            
            # Extract links from newly loaded content
            if not extract_campaign_links():
                #print("No new links found after loading more")
                break
                
        except Exception as e:
            print(f"Error during loading attempt {attempt+1}: {e}")
            break

def main():
    try:
        # Initialize browser and navigate to GoFundMe
        init_browser()
        
        # Show all categories
        show_all_categories()
        
        # Get category links
        get_category_links()
        
        # Process each category
        for category_url in CATEGORIES: 
            load_campaigns_for_category(category_url)
            
        # Save all discovered campaign links
        save_links()
        
        print("Script completed successfully!")
        
    except Exception as e:
        print(f"Error in main execution: {e}")
    finally:
        print("Keeping browser open for 10 seconds for inspection...")
        time.sleep(10)
        driver.quit()

if __name__ == "__main__":
    main()
