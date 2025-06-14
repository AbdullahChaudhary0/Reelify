import requests
import json
import time

class LlamaStoryGenerator:
    def __init__(self, model_name="llama3.1:8b", base_url="http://localhost:11434"):
        """
        Initialize the Llama Story Generator
        
        Args:
            model_name: The Llama model to use (llama3.1:8b or llama3.1:7b)
            base_url: Ollama API base URL
        """
        self.model_name = model_name
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
    
    def check_ollama_status(self):
        """Check if Ollama is running and model is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                if self.model_name in model_names:
                    print(f"✅ {self.model_name} is available and ready!")
                    return True
                else:
                    print(f"❌ {self.model_name} not found. Available models: {model_names}")
                    print(f"💡 Try running: ollama pull {self.model_name}")
                    return False
            else:
                print("❌ Ollama is not responding")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to Ollama. Make sure it's running with: ollama serve")
            return False
        except requests.exceptions.Timeout:
            print("❌ Ollama connection timed out. Check if ollama serve is running.")
            return False
    
    def create_story_prompt(self, tag, description, story_length="2-3 minutes"):
        """Create a structured prompt for story generation"""
        prompt = f"""You are a professional news story writer creating engaging content for video production.

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
        
        return prompt
    
    def generate_story(self, tag, description, max_tokens=600, temperature=0.7):
        """Generate a story using Llama 3.1"""
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
            print(f"🔄 Generating story for '{tag}'...")
            print("⏳ First generation may take 2-5 minutes as model loads into memory...")
            start_time = time.time()
            
            response = requests.post(self.api_url, json=payload, timeout=300)
            
            if response.status_code == 200:
                result = response.json()
                story = result.get('response', '').strip()
                
                end_time = time.time()
                print(f"✅ Story generated in {end_time - start_time:.2f} seconds")
                
                return {
                    'tag': tag,
                    'story': story,
                    'generation_time': end_time - start_time,
                    'model_used': self.model_name
                }
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            print("❌ Request timed out. The model might be loading for the first time.")
            print("💡 This is normal for first use. Try running again - it should be much faster!")
            return None
        except Exception as e:
            print(f"❌ Error generating story: {str(e)}")
            return None
    
    def format_story_output(self, result):
        """Format the generated story for display"""
        if not result:
            return "No story generated."
        
        output = f"""
{'='*80}
TRENDING TOPIC: {result['tag']}
MODEL USED: {result['model_used']}
GENERATION TIME: {result['generation_time']:.2f} seconds
{'='*80}

{result['story']}

{'='*80}
"""
        return output

def test_quick_generation():
    """Quick test with a simple prompt"""
    generator = LlamaStoryGenerator()
    
    print("🚀 Quick Test - Simple Story Generation")
    print("=" * 50)
    
    # Simple test prompt
    simple_prompt = {
        "tag": "Test",
        "description": "This is a simple test to check if the model is working properly."
    }
    
    result = generator.generate_story(
        tag=simple_prompt["tag"],
        description=simple_prompt["description"],
        max_tokens=200,  # Very short for quick test
        temperature=0.5
    )
    
    if result:
        print("✅ Quick test successful!")
        print(f"Generated {len(result['story'])} characters in {result['generation_time']:.2f} seconds")
        return True
    else:
        print("❌ Quick test failed")
        return False

def main():
    # Initialize the generator
    generator = LlamaStoryGenerator()
    
    # Your sample data
    trending_topics = [
        {
            "tag": "Iran",
            "description": "Iran is trending because of escalating tensions in the Middle East, possibly related to recent attacks and retaliatory strikes between Iran and other nations or groups, especially with Israel. Trends reflect current events and popular discussions."
        },
        {
            "tag": "Syria", 
            "description": "Syria is trending due to the ongoing conflict, often related to airstrikes, humanitarian crises, or political developments reported in the news and discussed online."
        },
        {
            "tag": "Netanyahu",
            "description": "Netanyahu is trending due to ongoing protests in Israel against his government's proposed judicial reforms, seen by many as undermining democracy."
        },
        {
            "tag": "Mossad",
            "description": "Mossad is trending because of unconfirmed reports and speculation surrounding recent attacks and events, often involving geopolitics and international espionage. It's Israel's national intelligence agency, like the CIA or MI6."
        }
    ]
    
    print("🚀 Testing Llama 3.1 Story Generation")
    print("=" * 50)
    
    # Ask user what they want to do
    print("Choose an option:")
    print("1. Quick test (recommended for first time)")
    print("2. Generate story for Iran")
    print("3. Generate stories for all topics")
    
    choice = input("Enter choice (1/2/3): ").strip()
    
    if choice == "1":
        # Quick test first
        if test_quick_generation():
            print("\n🎉 System is working! You can now try generating full stories.")
        return
    
    elif choice == "2":
        # Test with Iraq topic
        test_topic = trending_topics[0]
        
        result = generator.generate_story(
            tag=test_topic["tag"],
            description=test_topic["description"],
            temperature=0.7
        )
        
        if result:
            print(generator.format_story_output(result))
            
            # Save to file
            filename = f"generated_story_{test_topic['tag'].lower()}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(generator.format_story_output(result))
            print(f"💾 Story saved to {filename}")
        
    elif choice == "3":
        # Generate all stories
        all_results = []
        for i, topic in enumerate(trending_topics, 1):
            print(f"\n📰 Processing {i}/{len(trending_topics)}: {topic['tag']}")
            result = generator.generate_story(
                tag=topic["tag"],
                description=topic["description"]
            )
            if result:
                all_results.append(result)
                print(f"✅ Generated story for {topic['tag']} ({result['generation_time']:.1f}s)")
            else:
                print(f"❌ Failed to generate story for {topic['tag']}")
            
            # Small delay between requests
            if i < len(trending_topics):
                time.sleep(2)
        
        # Save all results
        if all_results:
            with open("all_generated_stories.json", "w", encoding="utf-8") as f:
                json.dump(all_results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 All stories saved to all_generated_stories.json")
            print(f"📊 Successfully generated {len(all_results)}/{len(trending_topics)} stories")
    
    else:
        print("Invalid choice. Please run again and choose 1, 2, or 3.")

if __name__ == "__main__":
    main()