import pandas as pd
import google.generativeai as genai
import csv
import time
import os

# Configure the Gemini API
def configure_genai(api_key):
    genai.configure(api_key=api_key)
    
    # Set up the model
    generation_config = {
        "temperature": 0.2,
        "top_p": 0.95,
        "top_k": 40,
    }
    
    return genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config=generation_config
    )

def load_data(campaign_file, category_file):
    """Load campaign and category data from CSV files"""
    campaigns_df = pd.read_csv(campaign_file)
    categories_df = pd.read_csv(category_file)
    return campaigns_df, categories_df

def check_all_categories(model, campaign_text, categories_df):
    """Check a campaign against all categories at once"""
    # Format all categories for the prompt
    categories_list = []
    for _, category in categories_df.iterrows():
        cat_id = category['CategoryId']
        cat_items = [str(cat_id)] + [cat for cat in [category['Category1'], category['Category2'], category['Category3']] if not pd.isna(cat)]
        categories_list.append(" - ".join(cat_items))
    
    categories_str = "\n".join(categories_list)
    
    prompt = f"""
    Campaign Text: "{campaign_text}"
    
    Categories (ID - Categories):
    {categories_str}
    
    Which category IDs match with this campaign text? Respond with ONLY a CSV format:
    
    categoryId,match
    
    Where 'match' is either 'strong' or 'medium'. Only include categories that have a match.
    Do not include categories with no match.
    Do not include any explanations or additional text.
    """
    
    response = model.generate_content(prompt)
    response_text = response.text.strip()
    
    # Parse the response to get matching categories
    matches = []
    
    # Skip header row if present
    lines = response_text.split('\n')
    start_idx = 0
    if lines and "categoryId" in lines[0].lower():
        start_idx = 1
    
    for line in lines[start_idx:]:
        if line.strip():
            parts = line.split(',')
            if len(parts) >= 2:
                try:
                    category_id = parts[0].strip()
                    match_type = parts[1].strip().lower()
                    if match_type in ["strong", "medium"]:
                        matches.append({"categoryId": category_id, "match": match_type})
                except:
                    continue
    
    return matches

def main(api_key, campaign_file, category_file, output_file):
    # Set up Gemini
    model = configure_genai(api_key)
    
    # Load data
    campaigns_df, categories_df = load_data(campaign_file, category_file)
    
    # Prepare output
    output_rows = []
    
    # Process campaigns one by one
    for _, campaign in campaigns_df.iterrows():
        campaign_id = campaign['campaignId']
        campaign_text = campaign['campaignText']
        
        print(f"Processing campaign: {campaign_id} - {campaign_text}")
        
        # Check this campaign against all categories at once
        matches = check_all_categories(model, campaign_text, categories_df)
        
        # Add matches to output
        for match in matches:
            output_rows.append({
                'campaignId': campaign_id,
                'categoryId': match['categoryId'],
                'match': match['match']
            })
        
        # Print summary for this campaign
        if matches:
            print(f"  Found {len(matches)} matches for campaign {campaign_id}")
            for match in matches:
                print(f"    Category {match['categoryId']}: {match['match']}")
        else:
            print(f"  No matches found for campaign {campaign_id}")
        
        print("---")
        
        # Add a small delay before processing the next campaign
        time.sleep(1)
    
    # Write results to CSV
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['campaignId', 'categoryId', 'match'])
        writer.writeheader()
        writer.writerows(output_rows)
    
    print(f"Processing complete. Results written to {output_file}")

if __name__ == "__main__":
    # Replace with your actual Gemini API key
   
    API_KEY = os.getenv("GEMINI_API_KEY")
    if not API_KEY:
        raise ValueError("API key not found. Please set the GEMINI_API_KEY environment variable.")
    
    # File paths
    CAMPAIGN_FILE = "campaigns.csv"
    CATEGORY_FILE = "categories.csv"
    OUTPUT_FILE = "campaign_category_matches.csv"
    
    main(API_KEY, CAMPAIGN_FILE, CATEGORY_FILE, OUTPUT_FILE)