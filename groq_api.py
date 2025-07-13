# groq_api.py

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_groq_connection():
    """Test if Groq API is accessible"""
    try:
        response = groq_chat("Hello", temperature=0.1, max_tokens=10)
        return not response.startswith("Error:")
    except:
        return False

def groq_chat(prompt, temperature=0.7, max_tokens=500):
    """
    Send a prompt to Groq API and get response
    """
    api_key = os.getenv("GROQ_API_KEY")
    
    # Try different models in order of preference
    models_to_try = [
        "llama3-8b-8192",
        "llama3-70b-8192", 
        "mixtral-8x7b-32768",
        "gemma-7b-it"
    ]
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Try each model until one works
    for model in models_to_try:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful AI assistant. When asked to provide JSON format, respond with valid JSON. Otherwise, respond in clear, natural text format."},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        # Try each model with retries
        for retry in range(2):  # 2 retries per model
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=45)
                
                if response.status_code == 200:
                    result = response.json()
                    return result['choices'][0]['message']['content'].strip()
                elif response.status_code == 400:
                    # Try next model if this one fails
                    break  # Break retry loop, try next model
                elif response.status_code == 429:
                    # Rate limit, wait and retry
                    import time
                    time.sleep(2)
                    continue
                else:
                    response.raise_for_status()
                    
            except requests.exceptions.Timeout:
                if retry == 1:  # Last retry for this model
                    break  # Try next model
                continue  # Retry same model
            except requests.exceptions.ConnectionError:
                if retry == 1:  # Last retry for this model
                    break  # Try next model
                import time
                time.sleep(1)
                continue  # Retry same model
            except requests.exceptions.RequestException as e:
                if "400" in str(e) or "401" in str(e):
                    break  # Try next model
                if retry == 1:  # Last retry for this model
                    break  # Try next model
                continue  # Retry same model
            except Exception as e:
                if retry == 1:  # Last retry for this model
                    break  # Try next model
                continue  # Retry same model
    
    # If all models fail, return a helpful error
    return "Error: Unable to connect to Groq API. Please check your internet connection and API key."