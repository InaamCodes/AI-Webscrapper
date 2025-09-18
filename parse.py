# parse.py

import os
import requests
import time

# --- 1. Get the Hugging Face API Key ---
api_key = os.getenv("HUGGINGFACE_API_KEY")

# --- 2. Check for the API Key ---
if not api_key:
    raise ValueError("HUGGINGFACE_API_KEY not found in environment variables. Please set it in your .env file.")

# --- 3. Define the Hugging Face Model and API URL ---
# --- THIS IS THE UPDATED MODEL ID ---
MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"
# ------------------------------------

API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"
headers = {"Authorization": f"Bearer {api_key}"}

# --- 4. Define the Parsing Function ---
def parse_with_huggingface(dom_chunks, parse_description):
    """
    Parses content chunks using the Hugging Face Inference API with robust error handling.
    """
    parsed_results = []
    total_chunks = len(dom_chunks)
    
    print(f"Starting parsing with Hugging Face ({MODEL_ID}) for {total_chunks} chunk(s)...")

    for i, chunk in enumerate(dom_chunks, start=1):
        # A clear, direct prompt works best.
        prompt = (
            f"You are an expert data extraction agent. Your task is to extract information that matches the "
            f"description '{parse_description}' from the following text. "
            f"Respond with ONLY the extracted data and nothing else. If no information matches, return an empty response.\n\n"
            f"Text to analyze: \n---\n{chunk}"
        )

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 500,
                "temperature": 0.1,
                "return_full_text": False # This is important to get only the answer
            }
        }

        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            try:
                result = response.json()
                extracted_content = result[0].get('generated_text', '').strip()
                if extracted_content:
                    parsed_results.append(extracted_content)
                print(f"Parsed batch: {i} of {total_chunks}")
            except requests.exceptions.JSONDecodeError:
                print(f"Error on batch {i}: Received OK status but failed to decode JSON.")
        else:
            # Handle non-200 responses (like 503 for model loading)
            error_message = ""
            try:
                error_data = response.json()
                error_message = error_data.get("error", "An unknown JSON error occurred.")
                if "estimated_time" in error_data:
                    wait_time = int(error_data["estimated_time"])
                    error_message += f" The model is loading. Please wait ~{wait_time}s and try again."
            except requests.exceptions.JSONDecodeError:
                error_message = f"Server returned a non-JSON response. Status Code: {response.status_code}. Response Text: {response.text}"
            
            print(f"Error on batch {i}: {error_message}")
            
        if i < total_chunks:
            time.sleep(2)

    return "\n".join(parsed_results)