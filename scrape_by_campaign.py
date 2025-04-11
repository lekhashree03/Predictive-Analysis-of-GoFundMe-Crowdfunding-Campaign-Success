#!/usr/bin/env python3
import re
import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

# Storage lists
URL_INDEX = []
TITLE     = []
RAISED    = []
TARGET    = []
STORY     = []
M_CAMPAIGN= []
CREATED_DATE = []
DONORS    = []
SHARES    = []
FOLLOWERS = []
SCRAPE_DATE = []

def scraped_log(url):
    with open('scraped_log.txt','a',encoding='utf-8') as f:
        f.write(url + "\n")
    print(f"Scraped: {url}")

def scrape_campaign(driver, url):
    driver.get(url)
    wait = WebDriverWait(driver, 20)
    # time.sleep(5)
    # Make sure the page is fully loaded
    wait = WebDriverWait(driver, 20) 
    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'h1')))
   
    # wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'raised')] | //*[contains(@class, 'progress-meter_progressBarHeading')]")))
    # 1. Title
    try:
        title_el = wait.until(EC.visibility_of_element_located((By.TAG_NAME, 'h1')))
        title = title_el.text
    except Exception as e:
        print(f"Error getting title: {e}")
        title = ""

    # 2. Raised amount - Extract only the dollar amount
    try:
        raised_text = driver.find_element(By.XPATH, "//span[contains(@class, 'progress-meter_progressBarHeading') or contains(text(), '$')]").text
        if not raised_text:
            raised_text = driver.find_element(By.XPATH, "//*[contains(text(), 'raised')]").text
        
        raised_match = re.search(r'\$([0-9,.]+)', raised_text)
        raised = f"${raised_match.group(1)}" if raised_match else ""
    except Exception as e:
        print(f"Error getting raised amount: {e}")
        raised = ""

    # 3. Target amount
    try:
        target_text = driver.find_element(By.XPATH, "//*[contains(text(), 'goal')]").text
        target_match = re.search(r'\$([0-9,.]+K?)\s+goal', target_text)
        target = f"${target_match.group(1)}" if target_match else ""
    except Exception as e:
        print(f"Error getting target: {e}")
        target = ""

    # 4. Donors count
    try:
        # Try to locate the donations text based on the exact HTML structure in your screenshot
        donations_text = driver.find_element(By.CSS_SELECTOR, "div.hrt-text-body-sm.hrt-text-supporting").text.strip()
        donors_match = re.search(r'([\d,\.]+K?)\s+donations', donations_text)
        donors = donors_match.group(1) if donors_match else ""
        
    except:
        print(f"Error getting donors count")
        donors = 0

    # 5. m_campaign = category + "-fundraiser"
    try:
        cat_el = driver.find_element(
            By.CSS_SELECTOR,
            "ul.date-and-category_dateAndCategory__m56MT li.hrt-meta-list-item:nth-child(2) a"
        )
        cat = cat_el.text
        m_campaign = f"{cat.lower().replace(' ', '-')}-fundraiser"
    except Exception as e:
        print(f"Error getting category for m_campaign: {e}")
        m_campaign = ""

    # 6. Story
    story = ""
    elements = driver.find_elements(By.CSS_SELECTOR, "div[class*='campaign-description_content']")
    if elements:
        story = elements[0].text

    # 7. Created Date
    created_date = ""
    try:
        created_date_el = driver.find_element(
            By.CSS_SELECTOR,
            "span.m-campaign-byline-created.a-created-date"
        )
        created_date = created_date_el.text
    except Exception as e:
        print(f"Error getting created date: {e}")
        created_date = ""

    # 8. Shares and Followers - Not visible in the screenshot
    shares = ""
    followers = ""

    # Collect information in lists
    slug = url.rstrip("/").split("/")[-1]
    URL_INDEX.append(slug)
    TITLE.append(title)
    RAISED.append(raised)
    TARGET.append(target)
    DONORS.append(donors)
    CREATED_DATE.append(created_date)
    M_CAMPAIGN.append(m_campaign)
    STORY.append(story)
    SCRAPE_DATE.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    scraped_log(url)

def create_df():
    df = pd.DataFrame({
        'url_index': URL_INDEX,
        'title': TITLE,
        'raised': RAISED,
        'target': TARGET,
        'story': STORY,
        'm_campaign': M_CAMPAIGN,
        'created_date': CREATED_DATE,
        'donors': DONORS,
        'scrape_date': SCRAPE_DATE
    })
    i = 0
    while os.path.exists(f"gofund_data{i}.csv"):
        i += 1
    fn = f"gofund_data{i}.csv"
    df.to_csv(fn, index=False, encoding="utf-8")
    print(f"Wrote {fn}")

def main():
    # Read URLs from urllist_master.txt
    try:
        with open("urllist_master.txt", "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error reading urllist_master.txt: {e}")
        return

    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager

    opts = Options()
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    # Enable headless mode so the browser runs in the background without a GUI
    opts.add_argument("--headless")
    
    # Set user agent to mimic a regular browser
    opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)

    try:
        for url in urls:
            scrape_campaign(driver, url)
        create_df()
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
