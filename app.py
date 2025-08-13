from flask import Flask, request, render_template_string, redirect, url_for, jsonify
from flasgger import Swagger
from google.generativeai import GenerativeModel
import google.generativeai as genai

app = Flask(__name__)
swagger = Swagger(app)

API_KEY = "AIzaSyBVApkZjLr_CdQOrgrhKVJYpDtaGrgyBVk"

GEMINI_MODELS = [
    ("gemini-2.5-pro", "Gemini 2.5 Pro"),
    ("gemini-2.5-flash", "Gemini 2.5 Flash"),
    ("gemini-2.5-flash-lite", "Gemini 2.5 Flash Lite"),
    ("gemini-live-2.5-flash-preview", "Gemini 2.5 Flash Live"),
    ("gemini-2.5-flash-preview-native-audio-dialog", "Gemini 2.5 Flash Native Audio"),
    ("gemini-2.5-flash-preview-tts", "Gemini 2.5 Flash Text-to-Speech"),
    ("gemini-2.5-pro-preview-tts", "Gemini 2.5 Pro Text-to-Speech"),
    ("gemini-2.0-flash", "Gemini 2.0 Flash"),
    ("gemini-2.0-flash-preview-image-generation", "Gemini 2.0 Flash Image Generation"),
    ("gemini-2.0-flash-lite", "Gemini 2.0 Flash Lite"),
    ("gemini-2.0-flash-live-001", "Gemini 2.0 Flash Live"),
    ("gemini-1.5-flash", "Gemini 1.5 Flash"),
    ("gemini-1.5-flash-8b", "Gemini 1.5 Flash-8B"),
    ("gemini-1.5-pro", "Gemini 1.5 Pro"),
]


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Gemini Chat Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            margin: 0;
            font-family: 'Inter', sans-serif;
            background-color: #f5f7fa;
            color: #333;
        }

        .container {
            max-width: 800px;
            margin: 50px auto;
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.05);
        }

        h1 {
            text-align: center;
            font-weight: 700;
            color: #1d3557;
            margin-bottom: 20px;
        }

        label {
            font-weight: 600;
            margin-top: 20px;
            display: block;
        }

        select, textarea {
            width: 100%;
            padding: 12px;
            margin-top: 10px;
            border-radius: 8px;
            border: 1px solid #ccc;
            font-size: 1rem;
            box-sizing: border-box;
        }

        textarea {
            height: 120px;
            resize: vertical;
        }

        button {
            display: inline-block;
            background: #457b9d;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            margin-top: 20px;
            transition: background 0.3s ease;
        }

        button:hover {
            background: #1d3557;
        }

        .response, .error {
            margin-top: 30px;
            padding: 20px;
            border-radius: 8px;
            background: #f1faee;
            border-left: 5px solid #2a9d8f;
        }

        .error {
            background: #ffe8e8;
            border-left-color: #e63946;
            color: #a4161a;
        }

        .footer {
            margin-top: 40px;
            text-align: center;
        }

        .swagger-link {
            display: inline-block;
            background: #06d6a0;
            color: #073b4c;
            text-decoration: none;
            padding: 10px 16px;
            border-radius: 6px;
            font-weight: 600;
            transition: background 0.2s ease;
        }

        .swagger-link:hover {
            background: #04b387;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Chat with Gemini</h1>
        <form method="post">
            <label for="model">Select Model:</label>
            <select name="model" id="model">
                {% for val, name in models %}
                    <option value="{{ val }}" {% if val == model %}selected{% endif %}>{{ name }}</option>
                {% endfor %}
            </select>

            <label for="prompt">Your Prompt:</label>
            <textarea name="prompt" id="prompt" required>{{ prompt or '' }}</textarea>

            <button type="submit">Generate Response</button>
        </form>

        {% if response %}
            <div class="response">
                <strong>Gemini says:</strong><br>
                {{ response }}
            </div>
        {% elif error %}
            <div class="error">
                <strong>Error:</strong><br>
                {{ error }}
            </div>
        {% endif %}

        <div class="footer">
            <a class="swagger-link" href="{{ url_for('flasgger.apidocs') }}" target="_blank">📘 View Swagger API Docs</a>
        </div>
    </div>
</body>
</html>

"""

@app.route("/", methods=["GET", "POST"])
def index():
    response = error = None
    prompt = ""
    model = GEMINI_MODELS[0][0]
    if request.method == "POST":
        prompt = request.form.get("prompt", "").strip()
        model = request.form.get("model", model)
        try:
            genai.configure(api_key=API_KEY)
            gemini = GenerativeModel(model)
            result = gemini.generate_content(prompt)
            response = result.text or ""
        except Exception as e:
            error = str(e)

    return render_template_string(
        HTML_TEMPLATE, models=GEMINI_MODELS, model=model, prompt=prompt,
        response=response, error=error
    )

@app.route("/generate", methods=["POST"])
def generate_api():
    """
    Generate content using Gemini model
    ---
    tags:
      - Gemini API
    parameters:
      - in: body
        name: payload
        required: true
        schema:
          type: object
          properties:
            model:
              type: string
              description: Gemini model identifier
            prompt:
              type: string
              description: Text prompt for Gemini
          required:
            - model
            - prompt
    responses:
      200:
        description: The generated response from Gemini
        schema:
          type: object
          properties:
            response:
              type: string
    """
    data = request.get_json()
    model = data.get("model")
    prompt = data.get("prompt")
    try:
        genai.configure(api_key=API_KEY)
        gemini = GenerativeModel(model)
        result = gemini.generate_content(prompt)
        return jsonify({"response": result.text or ""})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use Render's PORT or fallback 5000
    app.run(host="0.0.0.0", port=port, debug=True)
