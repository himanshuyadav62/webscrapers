from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import visibility_of_element_located
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Configure Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless=new")  # Run in headless mode
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.100 Safari/537.36")
chrome_options.add_argument("window-size=1920,1080")

# Start the browser with the configured options
browser = webdriver.Chrome(options=chrome_options)
browser.get("https://www.nykaa.com")  # Navigate to URL

# Wait for the page to load by waiting for <h1> element to appear on the page
title = (
    WebDriverWait(driver=browser, timeout=10)
    .until(visibility_of_element_located((By.CSS_SELECTOR, "h1")))
    .text
)

# Retrieve fully rendered HTML content
content = browser.page_source
browser.close()

# Parse it with BeautifulSoup
from bs4 import BeautifulSoup
soup = BeautifulSoup(content, "html.parser")
print(soup.find("h1").text)