import csv
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import visibility_of_element_located
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def configure_browser():
    """Configures and returns a Selenium WebDriver instance."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--ignore-certificate-errors")  # Ignore SSL errors
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
    )
    return webdriver.Chrome(options=chrome_options)

def scrape_products(category_name, category_link, subcategory_name, subcategory_link, product_type_name, product_type_link):
    """Scrapes product details from a given product type link and writes to CSV."""
    browser = configure_browser()
    try:
        browser.get("https://nykaa.com" + product_type_link)
        WebDriverWait(browser, 10).until(
            visibility_of_element_located((By.CSS_SELECTOR, ".product-listing"))
        )
        product_page = BeautifulSoup(browser.page_source, "html.parser")
        browser.quit()
        
        with open("nykaa_categories.csv", "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            for product in product_page.select(".productWrapper a"):
                product_name = product.select_one(".css-xrzmfa").text.strip() if product.select_one(".css-xrzmfa") else ""
                price = product.select_one(".css-111z9ua").text.strip() if product.select_one(".css-111z9ua") else ""
                discount = product.select_one(".css-cjd9an").text.strip() if product.select_one(".css-cjd9an") else ""
                # writer.writerow([category_name, category_link, subcategory_name, subcategory_link, product_type_name, product_type_link, product_name, price, discount])
                writer.writerow([category_name, subcategory_name, product_type_name, product_name, price, discount])
    except Exception as e:
        print(f"Error scraping {product_type_link}: {e}")
        browser.quit()

def main():
    browser = configure_browser()
    browser.get("https://www.nykaa.com")
    
    try:
        WebDriverWait(browser, 10).until(visibility_of_element_located((By.CSS_SELECTOR, "h1")))
        soup = BeautifulSoup(browser.page_source, "html.parser")
        browser.quit()
        
        with open("nykaa_categories.csv", "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            # writer.writerow(["Category", "Category Link", "Subcategory", "Subcategory Link", "Product Type", "Product Type Link", "Product Name", "Price", "Discount"])
            writer.writerow(["Category",  "Subcategory",  "Product Type",  "Product Name", "Price", "Discount"])
        
        product_tasks = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            for category_section in soup.select(".MegaDropdownHeadingbox"):
                category_link_tag = category_section.find("a")
                if category_link_tag:
                    category_name = category_link_tag.text.strip()
                    category_link = category_link_tag.get("href", "")
                else:
                    continue
                
                for subcategory in category_section.select(".MegaDropdown-ContentInner .MegaDropdown-ContentHeading"):
                    subcategory_link_tag = subcategory.find("a")
                    if subcategory_link_tag:
                        subcategory_name = subcategory_link_tag.text.strip()
                        subcategory_link = subcategory_link_tag.get("href", "")
                    else:
                        continue
                    
                    product_list = subcategory.find_next_sibling("ul")
                    if not product_list:
                        continue
                    
                    for product_type in product_list.select("li a"):
                        product_type_name = product_type.text.strip()
                        product_type_link = product_type.get("href", "")
                        product_tasks.append(
                            executor.submit(scrape_products, category_name, category_link, subcategory_name, subcategory_link, product_type_name, product_type_link)
                        )
            concurrent.futures.wait(product_tasks)
        print("CSV file 'nykaa_categories.csv' created successfully.")
    
    except Exception as e:
        print("An error occurred:", e)
        browser.quit()

if __name__ == "__main__":
    main()
