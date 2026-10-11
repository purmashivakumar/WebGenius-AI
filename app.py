import os
import re
import logging
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai import errors

load_dotenv()
app = Flask(__name__, static_folder=None)

API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()

@app.get("/")
def home():
    return send_from_directory(".", "index.html")

@app.get("/<path:path>")
def static_files(path):
    allowed = {"style.css", "script.js"}
    if path in allowed:
        return send_from_directory(".", path)
    return jsonify({"error": "Not found"}), 404

def clean_html(text):
    text = (text or "").strip()
    text = re.sub(r"^```(?:html)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()

@app.get("/api/health")
def health():
    return jsonify({"ok": True, "api_key_configured": bool(API_KEY), "model": MODEL})

@app.post("/api/generate")
def generate():
    if not API_KEY:
        return jsonify({
            "error": "Gemini API key is missing. Open .env, add your key after GEMINI_API_KEY=, save, then restart the server."
        }), 503

    data = request.get_json(silent=True) or {}
    prompt = str(data.get("prompt", "")).strip()
    site_type = str(data.get("site_type", "portfolio"))[:40]
    theme = str(data.get("theme", "dark"))[:40]

    if not prompt:
        return jsonify({"error": "Please describe the website you want to create."}), 400
    if len(prompt) > 1200:
        return jsonify({"error": "Your prompt is too long. Keep it under 1200 characters."}), 400

    system_instruction = """
You are WebGenius AI, an expert frontend website generator.
Return ONLY one complete, valid, standalone HTML document. Do not use Markdown fences or explanations.
Include CSS in a style tag and small interactions in a script tag.
Create a polished, modern, responsive website tailored to the user's prompt.
Use semantic HTML, accessible contrast, responsive layout, clear visual hierarchy, realistic sample content,
and working in-page navigation. Avoid external JavaScript libraries. Never include API keys or server code.
For portfolios include hero, about, skills, projects and contact sections.
For e-commerce demos include product cards and demo cart interactions without real payments.
Never claim a form sends messages unless connected to a backend.
"""
    user_prompt = f"""Website category: {site_type}
Visual style: {theme}
User requirements: {prompt}

Generate the complete website HTML now. Keep it self-contained and suitable for an iframe preview."""

    try:
        client = genai.Client(api_key=API_KEY)
        response = client.models.generate_content(
            model=MODEL,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7,
                max_output_tokens=8192,
            ),
        )
        html = clean_html(getattr(response, "text", "") or "")
        if "<html" not in html.lower() and "<!doctype" not in html.lower():
            app.logger.warning("Gemini returned a response without a complete HTML document")
            return jsonify({"error": "The AI response was not valid HTML. Try a more specific prompt."}), 502
        return jsonify({"html": html})

    except errors.APIError as exc:
        app.logger.warning("Gemini API error (%s): %s", getattr(exc, "code", "unknown"), exc)
        code = getattr(exc, "code", None)
        message = str(exc).lower()

        if code == 429 or "resource_exhausted" in message or "quota" in message:
            return jsonify({
                "error": "Gemini quota limit reached. This is a Google API limit, not a UI bug. Check your quota or wait until it resets."
            }), 429
        if code == 503 or "unavailable" in message or "high demand" in message:
            return jsonify({
                "error": "Gemini is busy right now. Please wait a little and try again."
            }), 503
        if code == 401 or code == 403 or "api key" in message or "unauthenticated" in message or "permission" in message:
            return jsonify({
                "error": "Your Gemini API key is invalid or does not have access. Check GEMINI_API_KEY in .env."
            }), 401
        if code == 404 or "not found" in message:
            return jsonify({
                "error": f"The model '{MODEL}' is unavailable for this API. Check GEMINI_MODEL in .env and choose a supported model."
            }), 502
        return jsonify({"error": "Gemini could not generate the website. Check your connection and try again."}), 502

    except Exception:
        app.logger.exception("Unexpected website generation error")
        return jsonify({"error": "Something went wrong in the backend. Check the VS Code terminal for details."}), 500

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host="127.0.0.1", port=5000, debug=False)
