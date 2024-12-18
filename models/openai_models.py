import requests
import json
import os
from project_utils.getkeys import getkeys
import sys
print("\n".join(sys.path))

config_path = os.path.join(os.path.dirname(__file__), '..', 'configs', 'config.yaml')
getkeys(config_path)

class OpenAIModel:
    def __init__(self, model, system_prompt, temperature):
        self.model_endpoint = 'https://api.openai.com/v1/chat/completions'
        self.temperature = temperature
        self.model = model
        self.system_prompt = system_prompt
        getkeys(config_path)
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
    
    def generate_text(self, prompt):
        payload = {
            "model": self.model,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False,
            "temperature": self.temperature,
        }

        try:
            # Send the request to the API
            response = requests.post(self.model_endpoint, headers=self.headers, data=json.dumps(payload))
            response_json = response.json()

            # Log the full response for debugging
            print("Full API Response:", response_json)

            # Handle 'choices' if present
            if 'choices' in response_json:
                content = response_json['choices'][0]['message']['content']
                return json.loads(content)
            else:
                # Fallback for unexpected response structures
                print("Unexpected response format. Returning raw response.")
                return {"error": "Unexpected response format", "raw_response": response_json}

        except requests.RequestException as e:
            print(f"Error in API call: {e}")
            return {"error": f"Error in API call: {str(e)}"}
        except Exception as e:
            print(f"Error parsing API response: {e}")
            return {"error": f"Error parsing API response: {str(e)}"}

    
    
    