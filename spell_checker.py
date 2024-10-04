from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

class TextCorrectionModule:
    def correct_text(self, text):
        api_url = "https://api.languagetool.org/v2/check"
        payload = {
            "text": text,
            "language": "en-US"
        }
        logging.info(f"Original Text: {text}")

        # Send request to LanguageTool API
        response = requests.post(api_url, data=payload)
        
        if response.status_code == 200:
            corrections = response.json().get("matches", [])
            corrected_text = text

            # Apply each correction to the text
            for match in sorted(corrections, key=lambda x: x['offset'], reverse=True):
                start = match['offset']
                end = start + match['length']
                replacement = match['replacements'][0]['value'] if match['replacements'] else ""
                corrected_text = corrected_text[:start] + replacement + corrected_text[end:]

            logging.info(f"Corrected Text: {corrected_text}")
            return corrected_text
        else:
            logging.error(f"Error from LanguageTool API: {response.status_code} - {response.text}")
            return text  # Return original if there’s an error

text_corrector = TextCorrectionModule()

@app.route('/api/spellcheck', methods=['POST'])
def spell_check():
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({"error": "Invalid input, please provide 'text' in JSON."}), 400

    text_to_check = data['text']
    corrected_text = text_corrector.correct_text(text_to_check)

    return jsonify({"corrected_text": corrected_text}), 200

if __name__ == "__main__":
    app.run(port=5001)  # Run on a different port than your Express app
