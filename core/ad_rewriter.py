import requests
import json
import os
import logging
import time

class AdRewriter:
    def __init__(self, config_path='config/settings.json', max_retries=3):
        self.logger = logging.getLogger(__name__)
        self.config_path = os.path.join(os.path.dirname(__file__), f'../{config_path}')
        self.api_key = self.load_api_key()
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        self.max_retries = max_retries

    def load_api_key(self):
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            api_key = config.get('gemini', {}).get('api_key', '')
            if not api_key:
                self.logger.error("No Gemini API key provided in config")
            return api_key
        except Exception as e:
            self.logger.error(f"Error loading Gemini API key: {str(e)}")
            return ''

    def rewrite_ad(self, title, description, retries=0, use_fallback=False):
        """Rewrite ad title and description using Gemini API."""
        if not self.api_key:
            self.logger.error("No Gemini API key provided, returning original content")
            return title, description

        # Use fallback prompt if previous attempt failed
        if use_fallback:
            prompt = (
                f"Rewrite this Craigslist ad title and description to keep the same meaning and tone but make it unique. "
                f"Return only a JSON object with 'title' and 'description' fields.\n"
                f"Title: {title}\nDescription: {description}\n"
                f"Example: {{ \"title\": \"New Title\", \"description\": \"New Description\" }}"
            )
        else:
            prompt = (
                f"Rewrite the following Craigslist ad title and description to keep the same meaning and tone but make it unique. "
                f"Return the response as a JSON object with only 'title' and 'description' fields, enclosed in triple backticks.\n"
                f"```json\n{{ \"title\": \"New Title\", \"description\": \"New Description\" }}\n```\n\n"
                f"Title: {title}\nDescription: {description}"
            )

        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 1.0,
                "maxOutputTokens": 200
            }
        }

        try:
            response = requests.post(self.api_url, json=data, timeout=10)
            self.logger.debug(f"HTTP Status: {response.status_code}, Headers: {response.headers}, Response Text: {response.text}")
            response.raise_for_status()
            response_json = response.json()
            self.logger.debug(f"Gemini API response: {json.dumps(response_json, indent=2)}")

            # Check if response contains valid content
            if not response_json.get('candidates') or not response_json['candidates'][0].get('content', {}).get('parts'):
                self.logger.error("Invalid response structure from Gemini API")
                raise ValueError("Invalid response structure")

            rewritten_text = response_json['candidates'][0]['content']['parts'][0]['text']
            self.logger.debug(f"Raw rewritten text: {rewritten_text}")

            if not rewritten_text.strip():
                self.logger.error("Empty rewritten text received")
                raise ValueError("Empty response text")

            # Try to find JSON in the response (handles cases where response might include other text)
            json_start = rewritten_text.find('{')
            json_end = rewritten_text.rfind('}') + 1
            if json_start == -1 or json_end == 0:
                self.logger.error("No JSON found in response")
                raise ValueError("No JSON found in response")

            json_str = rewritten_text[json_start:json_end]
            self.logger.debug(f"Extracted JSON: {json_str}")

            try:
                rewritten_json = json.loads(json_str)
            except json.JSONDecodeError as e:
                # Try cleaning up common issues
                json_str = json_str.strip().strip('```').strip()
                rewritten_json = json.loads(json_str)

            if not isinstance(rewritten_json, dict) or 'title' not in rewritten_json or 'description' not in rewritten_json:
                self.logger.error("Invalid JSON structure in rewritten text")
                raise ValueError("Missing title or description in JSON")

            new_title = rewritten_json['title']
            new_description = rewritten_json['description']
            self.logger.info("Ad rewritten successfully")
            return new_title, new_description

        except (requests.exceptions.RequestException, KeyError, ValueError, json.JSONDecodeError) as e:
            self.logger.error(f"Error rewriting ad with Gemini: {str(e)}")
            if retries < self.max_retries:
                self.logger.info(f"Retrying Gemini API call ({retries + 1}/{self.max_retries})")
                time.sleep(2 ** retries)  # Exponential backoff
                # Use fallback prompt on next retry if not already used
                return self.rewrite_ad(title, description, retries + 1, use_fallback=True if not use_fallback else False)
            self.logger.error("Max retries reached, returning original content")
            return title, description