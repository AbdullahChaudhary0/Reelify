from flask import Flask, render_template, request, jsonify, session
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
import google.generativeai as genai
import requests
import json
import threading
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure random key

# Configure Gemini API
genai.configure(api_key="AIzaSyCymYZe_uKs05eXnyiPibp3TcDbuMQD8qU")

class TrendScraper:
    def __init__(self):
        self.file_name = "trends24_source.html"
    
    def is_file_outdated(self, file_path, max_age_seconds=3600):
        if os.path.exists(file_path):
            last_modified_time = os.path.getmtime(file_path)
            current_time = time.time()
            age_seconds = current_time - last_modified_time
            return age_seconds > max_age_seconds
        return True
    
    def setup_driver(self):
        options = Options()
        options.add_argument('--headless')  
        options.add_argument('--disable-gpu')
        options.add_argument('--allow-insecure-localhost')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--disable-web-security')
        options.add_argument('--dns-prefetch-disable')
        options.add_argument('--enable-features=NetworkServiceInProcess')
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    
    def scrape_trends(self, location):
        if location == "pakistan":
            url = "https://trends24.in/pakistan/"
        elif location == "united-states":
            url = "https://trends24.in/united-states/"
        else:
            url = "https://trends24.in/pakistan/"
        
        # Check if cached data is available and fresh
        if not self.is_file_outdated(self.file_name):
            print("Using cached trends data...")
            with open(self.file_name, "r", encoding="utf-8") as file:
                html_content = file.read()
        else:
            print("Fetching fresh trends data...")
            driver = None
            try:
                driver = self.setup_driver()
                driver.get(url)
                driver.implicitly_wait(20)
                html_content = driver.page_source
                
                with open(self.file_name, "w", encoding="utf-8") as file:
                    file.write(html_content)
            finally:
                if driver:
                    driver.quit()
        
        # Parse trends
        soup = BeautifulSoup(html_content, "html.parser")
        trends_data = soup.select(".trend-card__list li")
        
        trends = []
        for i, trend_item in enumerate(trends_data[:50]):
            trend_text_element = trend_item.select_one("a.trend-link")
            if not trend_text_element:
                continue
                
            trend_text = trend_text_element.text.strip()
            trend_count_element = trend_item.select_one("span")
            trend_count = trend_count_element.text.strip() if trend_count_element else ""
            
            # Extract numeric count
            numeric_count = 0
            if trend_count:
                match = re.search(r'(\d+)', trend_count)
                if match:
                    numeric_count = int(match.group(1))
                    trend_count = f"{numeric_count}K"
            
            trends.append({
                'rank': i + 1,
                'name': trend_text,
                'count': trend_count,
                'numeric_count': numeric_count
            })
        
        return trends

class LlamaStoryGenerator:
    def __init__(self, model_name="llama3.1:8b", base_url="http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
    
    def check_ollama_status(self):
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                return self.model_name in model_names
            return False
        except:
            return False
    
    def create_story_prompt(self, tag, description, story_length="2-3 minutes"):
        return f"""You are a professional news story writer creating engaging and educatiion content for video production as a Pakistani.

TRENDING TOPIC: {tag}
CONTEXT: {description}

Create a compelling {story_length} news story suitable for video content with the following structure:

1. HOOK (15-20 seconds): Start with an attention-grabbing opening that immediately draws viewers in
2. BACKGROUND (30-45 seconds): Provide essential context and background information
3. CURRENT DEVELOPMENTS (60-90 seconds): Detail what's happening right now and recent events
4. ANALYSIS (30-45 seconds): Explain why this matters and potential implications
5. CONCLUSION (15-20 seconds): Wrap up with what to watch for next

REQUIREMENTS:
- Write in a conversational, engaging tone suitable for video narration
- Include natural pauses and transitions
- Make it factual but compelling
- Suggest 2-3 visual elements or B-roll opportunities
- Keep sentences clear and not too long for speaking
- Total length should be approximately {story_length} when read aloud

Generate the complete story now:"""
    
    def generate_story_with_llama(self, tag, description, max_tokens=600, temperature=0.7):
        if not self.check_ollama_status():
            return None
        
        prompt = self.create_story_prompt(tag, description)
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": 0.9,
                "num_predict": max_tokens,
                "stop": ["Human:", "Assistant:", "\n\n---"]
            }
        }
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=300)
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            return None
        except:
            return None

def get_one_liner_for_trend(trend_name):
    prompt = f"Give a short one-liner explanation (max 30 words) of why '{trend_name}' is trending on Twitter. Give context for a user who doesn't know about these trends."
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        time.sleep(1)  # Rate limiting
        return response.text.strip()
    except Exception as e:
        return f"Trending topic related to current events and social discussions."

# Initialize global objects
trend_scraper = TrendScraper()
story_generator = LlamaStoryGenerator()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/scrape-trends', methods=['POST'])
def scrape_trends():
    try:
        data = request.get_json()
        location = data.get('location', 'pakistan')
        
        # Scrape trends
        trends = trend_scraper.scrape_trends(location)
        
        # Add descriptions using Gemini
        for trend in trends:
            trend['description'] = get_one_liner_for_trend(trend['name'])
        
        session['current_trends'] = trends
        session['location'] = location
        
        return jsonify({
            'success': True,
            'trends': trends,
            'location': location,
            'count': len(trends)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate-story', methods=['POST'])
def generate_story():
    try:
        data = request.get_json()
        tag = data.get('tag')
        description = data.get('description')
        
        if not tag or not description:
            return jsonify({
                'success': False,
                'error': 'Missing tag or description'
            }), 400
        
        # Try Llama first
        story = story_generator.generate_story_with_llama(tag, description)
        
        if not story:
            # Fallback to Gemini if Llama is not available
            prompt = f"""Create a compelling 2-3 minute news story about the trending topic '{tag}'.

Context: {description}

Structure the story with:
1. HOOK (15-20 seconds): Attention-grabbing opening
2. BACKGROUND (30-45 seconds): Essential context
3. CURRENT DEVELOPMENTS (60-90 seconds): What's happening now
4. ANALYSIS (30-45 seconds): Why this matters
5. CONCLUSION (15-20 seconds): What to watch next

Write in a conversational, engaging tone suitable for video narration."""
            
            try:
                model = genai.GenerativeModel("gemini-2.0-flash")
                response = model.generate_content(prompt)
                story = response.text.strip()
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Failed to generate story: {str(e)}'
                }), 500
        
        return jsonify({
            'success': True,
            'story': story,
            'tag': tag,
            'model_used': 'Llama 3.1' if story_generator.check_ollama_status() else 'Gemini AI'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    llama_status = story_generator.check_ollama_status()
    
    return jsonify({
        'status': 'healthy',
        'llama_available': llama_status,
        'gemini_available': True,  # Assuming Gemini is configured
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)