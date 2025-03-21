import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import visibility_of_element_located
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# Configure Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")  # Use standard headless flag
chrome_options.add_argument("window-size=1920,1080")  # Set window size
chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Mimic normal behavior
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36")

# Start the browser with the configured options
browser = webdriver.Chrome(options=chrome_options)
browser.get("https://www.nykaa.com")  # Navigate to URL

try:
    # Wait for page to load
    WebDriverWait(browser, 10).until(
        visibility_of_element_located((By.CSS_SELECTOR, "h1"))
    )
    
    # Retrieve fully rendered HTML content
    content = browser.page_source
    browser.quit()
    
    # Save the content into an HTML file
    with open("nykaa.html", "w", encoding="utf-8") as file:
        file.write(content)
    
    # Parse it with BeautifulSoup
    soup = BeautifulSoup(content, "html.parser")
    
    # Extract category, subcategory, and product type information
    data = []
    for category_section in soup.select(".MegaDropdownHeadingbox"):
        category_link_tag = category_section.find("a")
        if category_link_tag:
            category_name = category_link_tag.text.strip()
            category_link = category_link_tag.get("href", "")
        else:
            print("Skipping category section: No <a> tag found")
            continue  # Skip if no category link found

        subcategory_section = category_section.select(".MegaDropdown-ContentInner .MegaDropdown-ContentHeading")
        if not subcategory_section:
            print(f"Skipping category '{category_name}': No subcategories found")
            continue

        for subcategory in subcategory_section:
            subcategory_link_tag = subcategory.find("a")
            if subcategory_link_tag:
                subcategory_name = subcategory_link_tag.text.strip()
                subcategory_link = subcategory_link_tag.get("href", "")
            else:
                print(f"Skipping subcategory: No <a> tag found in {subcategory}")
                continue

            product_list = subcategory.find_next_sibling("ul")
            if not product_list:
                print(f"Skipping subcategory '{subcategory_name}': No products found")
                continue

            for product_type in product_list.select("li a"):
                product_type_name = product_type.text.strip()
                product_type_link = product_type.get("href", "")
                # data.append([category_name, category_link, subcategory_name, subcategory_link, product_type_name, product_type_link])
                data.append([category_name, subcategory_name, product_type_name])
    
    # Save to CSV
    with open("nykaa_categories.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(["Category", "Category Link", "Subcategory", "Subcategory Link", "Product Type", "Product Type Link"])
        writer.writerows(data)
    
    print("CSV file 'nykaa_categories.csv' created successfully.")
    
except Exception as e:
    print("An error occurred:", e)
    browser.quit()