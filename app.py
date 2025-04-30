from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize Groq client with API key from environment, with validation
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    logger.error("GROQ_API_KEY is not set in the environment")
    raise ValueError("GROQ_API_KEY environment variable is required")

try:
    client = Groq(api_key=api_key)
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {str(e)}")
    raise

# Add health check route
@app.route('/', methods=['GET'])
def health_check():
    logger.debug("Health check endpoint accessed")
    return jsonify({"status": "healthy"}), 200

@app.route('/api/query', methods=['POST'])
def query():
    logger.debug("Query endpoint accessed")
    try:
        data = request.get_json()
        if not data:
            logger.warning("No JSON data provided in request")
            return jsonify({"error": "No data provided"}), 400

        prompt = data.get("prompt")
        if not prompt:
            logger.warning("No prompt provided in JSON data")
            return jsonify({"error": "No prompt provided"}), 400

        logger.debug(f"Processing prompt: {prompt}")
        # Call Groq API
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        result = response.choices[0].message.content

        logger.debug(f"Groq API response: {result}")
        return jsonify({
            "text": result,
            "code": ["# Example code based on response"]
        })

    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)