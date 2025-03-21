import requests
from bs4 import BeautifulSoup
import csv
import time
from urllib.parse import urljoin

# Update with your actual base URL
BASE_URL = 'https://zeptonow.com'
# Update with the relative URL where categories are listed
categories_page_url = urljoin(BASE_URL, '')

# Step 1: Scrape the categories page
response = requests.get(categories_page_url)
if response.status_code != 200:
    raise Exception(f"Failed to load categories page: {categories_page_url}")

soup = BeautifulSoup(response.content, 'html.parser')

# Locate the "Categories" header and then the associated <ul> list.
categories_header = soup.find('h3', text="Categories")
if not categories_header:
    raise Exception("Categories header not found on the page.")

categories_list = categories_header.find_next('ul')
if not categories_list:
    raise Exception("Categories list not found after the header.")

# Extract each category and its relative link
categories = []
for li in categories_list.find_all('li'):
    a_tag = li.find('a')
    if a_tag:
        # The category name is in the nested <p> tag
        name_tag = a_tag.find('p')
        category_name = name_tag.get_text(strip=True) if name_tag else "N/A"
        category_link = a_tag.get('href')
        # Ensure we have a full URL
        full_category_link = urljoin(BASE_URL, category_link)
        categories.append({
            'category': category_name,
            'categoryLink': full_category_link
        })

print(f"Found {len(categories)} categories.")

# Step 2: For each category, crawl its page and extract product details.
# The CSV will combine category details with product information.
with open('products.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile, delimiter=';')
    writer.writerow(['category', 'categoryLink', 'productName', 'productLink', 'price', 'quantity', 'offer'])
    
    for cat in categories:
        print(f"Scraping category: {cat['category']}")
        cat_response = requests.get(cat['categoryLink'])
        if cat_response.status_code != 200:
            print(f"Failed to load category page: {cat['categoryLink']}")
            continue

        cat_soup = BeautifulSoup(cat_response.content, 'html.parser')
        # Assume that each product is within an <a> tag with data-testid="product-card"
        product_cards = cat_soup.find_all('a', attrs={'data-testid': 'product-card'})
        if not product_cards:
            print(f"No products found in category: {cat['category']}")
            continue
        
        for card in product_cards:
            # Get product link and ensure full URL
            product_link = card.get('href')
            full_product_link = urljoin(BASE_URL, product_link)
            
            # Product Name: inside an element with data-testid="product-card-name"
            name_tag = card.find(attrs={'data-testid': 'product-card-name'})
            product_name = name_tag.get_text(strip=True) if name_tag else "N/A"
            
            # Price: inside element with data-testid="product-card-price"
            price_tag = card.find(attrs={'data-testid': 'product-card-price'})
            price = price_tag.get_text(strip=True) if price_tag else "N/A"
            
            # Quantity: typically within an element with data-testid="product-card-quantity"
            quantity = "N/A"
            quantity_tag = card.find(attrs={'data-testid': 'product-card-quantity'})
            if quantity_tag:
                h5_tag = quantity_tag.find('h5')
                if h5_tag:
                    quantity = h5_tag.get_text(strip=True)
            
            # Offer: try to locate an element that contains "Off" (e.g., "24% Off")
            offer = "N/A"
            discount_tag = card.find('p', string=lambda t: t and "Off" in t)
            if discount_tag:
                offer = discount_tag.get_text(strip=True)
            
            writer.writerow([
                cat['category'], 
                # cat['categoryLink'], 
                product_name, 
                # full_product_link, 
                price, 
                quantity, 
                offer
            ])
            print(f"Scraped product: {product_name}")
        
        # Be polite and wait a bit between requests
        time.sleep(1)

print("CSV file 'products.csv' created successfully.")
