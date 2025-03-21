from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import visibility_of_element_located
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# Configure Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")  # Use standard headless flag
chrome_options.add_argument("window-size=1920,1080")  # Set window size
chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Mimic normal behavior
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36")

# Start the browser with the configured options
browser = webdriver.Chrome(options=chrome_options)
browser.get("https://www.nykaa.com")  # Navigate to URL

# Wait for the page to load by waiting for the <h1> element to appear on the page
try:
    title = WebDriverWait(browser, 10).until(
        visibility_of_element_located((By.CSS_SELECTOR, "h1"))
    ).text
    # Retrieve fully rendered HTML content
    content = browser.page_source
    browser.quit()

    # Parse it with BeautifulSoup
    soup = BeautifulSoup(content, "html.parser")
    print(soup.find("h1").text)
except Exception as e:
    print("An error occurred:", e)
    browser.quit()
