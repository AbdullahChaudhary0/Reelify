from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import os
import time
from datetime import datetime
import re
import matplotlib.pyplot as plt
import google.generativeai as genai

# Define file name
file_name = "trends24_source.html"

# Check if the file exists and is older than 1 hour
def is_file_outdated(file_path, max_age_seconds=3600):
    if os.path.exists(file_path):
        last_modified_time = os.path.getmtime(file_path)
        current_time = time.time()
        age_seconds = current_time - last_modified_time
        return age_seconds > max_age_seconds
    return True  # File doesn't exist, treat as outdated

# Configure Chrome options
options = Options()
options.add_argument('--headless')  
options.add_argument('--disable-gpu')
options.add_argument('--allow-insecure-localhost')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--disable-web-security')
options.add_argument('--dns-prefetch-disable')
options.add_argument('--enable-features=NetworkServiceInProcess')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")

# Set up WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# User input for location
print("Choose location for trends extraction:")
print("1. Pakistan")
print("2. United States")
choice = input("Enter your choice (1 or 2): ")

# Determine URL based on user's choice
if choice == "1":
    url = "https://trends24.in/pakistan/"
    location = "Pakistan"
elif choice == "2":
    url = "https://trends24.in/united-states/"
    location = "US"
else:
    print("Invalid choice. Defaulting to Pakistan.")
    url = "https://trends24.in/pakistan/"
    location = "Pakistan"

# Fetch the page source only if the file is outdated
if is_file_outdated(file_name):
    try:
        print("Fetching the latest trends data...")
        driver.get(url)
        driver.implicitly_wait(20)
        source_html = driver.page_source
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(source_html)
    finally:
        driver.quit()
else:
    print("Using cached trends data...")

# Load the HTML content
with open(file_name, "r", encoding="utf-8") as file:
    html_content = file.read()

# Parse with BeautifulSoup
soup = BeautifulSoup(html_content, "html.parser")

# Extract trends and their counts using appropriate selectors
import re

# Extract trends and their counts using appropriate selectors
trends_data = soup.select(".trend-card__list li")
top_50_trends = []

for trend_item in trends_data[:50]:
    trend_text = trend_item.select_one("a.trend-link").text.strip()
    trend_count_element = trend_item.select_one("span")
    trend_count = trend_count_element.text.strip() if trend_count_element else ""
    
    # Extract the numeric part of the trend count and add "K" if numeric
    if trend_count:
        # Use regex to extract the numeric part
        match = re.search(r'(\d+)', trend_count)
        if match:
            numeric_count = match.group(1)
            trend_count = f"{numeric_count}K"
        top_50_trends.append(f"{trend_text} ({trend_count})")
    else:
        top_50_trends.append(trend_text)

# Print the extracted trends
print(f"\nToday's Top 50 Twitter Trends in {location}:")
for i, trend in enumerate(top_50_trends, 1):
    print(f"{i}. {trend}")



# Extract trends and their counts
trends = []
counts = []

for trend_item in trends_data[:50]:
    trend_text = trend_item.select_one("a.trend-link").text.strip()
    trend_count_element = trend_item.select_one("span")
    trend_count = trend_count_element.text.strip() if trend_count_element else ""
    
    # Extract the numeric part of the trend count and add to counts
    if trend_count:
        match = re.search(r'(\d+)', trend_count)
        if match:
            numeric_count = int(match.group(1))  # Convert count to integer
            trends.append(trend_text)
            counts.append(numeric_count)
    else:
        trends.append(trend_text)
        counts.append(0)  # Assign 0 if no count is provided

# Print the extracted trends
print(f"\nToday's Top 50 Twitter Trends in {location}:")
for i, (trend, count) in enumerate(zip(trends, counts), 1):
    print(f"{i}. {trend} ({count}K)")

# Plotting the data
plt.figure(figsize=(12, 8))
plt.barh(trends[:20], counts[:20], color='skyblue')  
plt.xlabel('Trend Counts (K)')
plt.ylabel('Trends')
plt.title('Top 20 Twitter Trends and Their Counts')
plt.gca().invert_yaxis()  # Invert Y-axis for better readability
plt.tight_layout()
plt.show()

genai.configure(api_key="AIzaSyCymYZe_uKs05eXnyiPibp3TcDbuMQD8qU")

def get_one_liner_for_trend(trend_name):
    prompt = f"Give a short one-liner explanation (max 30 words) of why '{trend_name}' is trending on Twitter. Give context for a user who doesn't know about these trends."
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        time.sleep(2)
        return response.text.strip()
    except Exception as e:
        return "N/A"

trend_descriptions = []
print("\nGenerating one-liner descriptions using Gemini API...\n")

for i, trend in enumerate(trends[:50], 1):
    description = get_one_liner_for_trend(trend)
    trend_descriptions.append(description)
    print(f"{i}. {trend} - {description}")

