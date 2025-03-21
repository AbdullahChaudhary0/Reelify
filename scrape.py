from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import os

# Configure Chrome options
options = Options()
options.add_argument('--headless')  # Remove this line if testing non-headless mode
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

file_name = "trends24_source.html"

try:
    # Open the URL
    driver.get(url)

    # Wait for a moment to allow the page to load
    driver.implicitly_wait(20)

    # Retrieve and print the page source
    source_html = driver.page_source

    # Optionally save the source to a file for review
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(source_html)

finally:
    driver.quit()

# Load the HTML content
with open(file_name, "r", encoding="utf-8") as file:
    html_content = file.read()

# Parse with BeautifulSoup
soup = BeautifulSoup(html_content, "html.parser")

# Extract trends using appropriate selectors
# Assuming trends are within <a> tags with the class 'trend-link'
trends = [trend.text for trend in soup.select(".trend-card__list a.trend-link")]

# Get only the top 50 trends
top_50_trends = trends[:50]

# Print the extracted trends
print(f"\nToday's Top 50 Twitter Trends in {location}:")
for i, trend in enumerate(top_50_trends, 1):
    print(f"{i}. {trend}")
