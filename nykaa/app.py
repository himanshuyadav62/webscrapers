import csv
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import threading

class NykaaScraper:
    def __init__(self, max_workers=5):
        """
        Initialize the Nykaa scraper with a shared browser and thread-safe mechanisms.
        
        :param max_workers: Number of concurrent threads for scraping
        """
        # Shared browser configuration
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("window-size=1920,1080")
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_argument("--ignore-certificate-errors")
        self.chrome_options.add_argument("--allow-running-insecure-content")
        self.chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
        )
        
        # Browser and synchronization
        self.browser = None
        self.browser_lock = threading.Lock()
        self.max_workers = max_workers
        
        # Initialization of output file
        with open("nykaa_categories.csv", "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(["Category", "Subcategory", "Product Type", "Product Name", "Brand", "Price", "Discount", "Rating", "Number of Ratings", "Description"])

    def _get_shared_browser(self):
        """
        Get a shared browser instance, creating it if not exists.
        Uses threading lock to ensure thread-safety.
        
        :return: Configured Chrome WebDriver
        """
        with self.browser_lock:
            if self.browser is None:
                self.browser = webdriver.Chrome(options=self.chrome_options)
            return self.browser

    def _safe_browser_get(self, url):
        """
        Safely navigate to a URL with error handling.
        
        :param url: URL to navigate to
        :return: BeautifulSoup parsed page source
        """
        browser = self._get_shared_browser()
        try:
            browser.get(url)
            WebDriverWait(browser, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "body"))
            )
            return BeautifulSoup(browser.page_source, "html.parser")
        except Exception as e:
            print(f"Error navigating to {url}: {e}")
            return None

    def scrape_product_details(self, product_link):
        """
        Scrape detailed information for a single product.
        
        :param product_link: Product page URL
        :return: Product details dictionary
        """
        if not product_link:
            return {}
        
        product_detail_page = self._safe_browser_get("https://nykaa.com" + product_link)
        if not product_detail_page:
            return {}
        
        rating = product_detail_page.select_one(".css-m6n3ou").text.strip().replace("/5", "") \
            if product_detail_page.select_one(".css-m6n3ou") else ""
        
        num_ratings = product_detail_page.select_one(".css-1hvvm95").text.strip().split(" ")[0] \
            if product_detail_page.select_one(".css-1hvvm95") else ""
        
        desc_section = product_detail_page.select_one("#content-details")
        description = desc_section.get_text(separator=" ").strip() if desc_section else ""
        
        return {
            "rating": rating,
            "num_ratings": num_ratings,
            "description": description
        }

    def scrape_products(self, category_name, subcategory_name, product_type_name, product_type_link):
        """
        Scrape products for a specific product type.
        
        :param category_name: Main category name
        :param subcategory_name: Subcategory name
        :param product_type_name: Product type name
        :param product_type_link: Product type page URL
        """
        product_page = self._safe_browser_get("https://nykaa.com" + product_type_link)
        if not product_page:
            return
        
        with open("nykaa_categories.csv", "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            
            for product in product_page.select(".productWrapper a"):
                # Extract basic product information
                product_name = product.select_one(".css-xrzmfa").text.strip() if product.select_one(".css-xrzmfa") else ""
                price = product.select_one(".css-111z9ua").text.strip() if product.select_one(".css-111z9ua") else ""
                discount = product.select_one(".css-cjd9an").text.strip() if product.select_one(".css-cjd9an") else ""
                brand = product_name.split()[0] if product_name else ""
                product_link = product.get("href", "")
                
                # Get detailed product information
                product_details = self.scrape_product_details(product_link)
                
                writer.writerow([
                    category_name, 
                    subcategory_name, 
                    product_type_name, 
                    product_name, 
                    brand, 
                    price, 
                    discount, 
                    product_details.get("rating", ""),
                    product_details.get("num_ratings", ""),
                    product_details.get("description", "")
                ])

    def main(self):
        """
        Main scraping method to navigate and extract category, subcategory, and product information.
        """
        # Initial page navigation
        home_page = self._safe_browser_get("https://www.nykaa.com")
        if not home_page:
            print("Failed to load home page")
            return
        
        # Concurrent scraping of product types
        product_tasks = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for category_section in home_page.select(".MegaDropdownHeadingbox"):
                category_link_tag = category_section.find("a")
                if not category_link_tag:
                    continue
                category_name = category_link_tag.text.strip()
                
                for subcategory in category_section.select(".MegaDropdown-ContentInner .MegaDropdown-ContentHeading"):
                    subcategory_link_tag = subcategory.find("a")
                    if not subcategory_link_tag:
                        continue
                    subcategory_name = subcategory_link_tag.text.strip()
                    
                    product_list = subcategory.find_next_sibling("ul")
                    if not product_list:
                        continue
                    
                    for product_type in product_list.select("li a"):
                        product_type_name = product_type.text.strip()
                        product_type_link = product_type.get("href", "")
                        
                        product_tasks.append(
                            executor.submit(
                                self.scrape_products, 
                                category_name, 
                                subcategory_name, 
                                product_type_name, 
                                product_type_link
                            )
                        )
            
            # Wait for all tasks to complete
            concurrent.futures.wait(product_tasks)
        
        # Close the browser at the end
        with self.browser_lock:
            if self.browser:
                self.browser.quit()
        
        print("CSV file 'nykaa_categories.csv' created successfully.")

# Script entry point
if __name__ == "__main__":
    scraper = NykaaScraper()
    scraper.main()