# WebGenius AI — Updated

A responsive prompt-to-website generator using Flask and Google's Gemini API.

## Run on Windows / VS Code

1. Extract this ZIP and open the `WebGenius_AI_Updated` folder in VS Code.
2. Open **Terminal → New Terminal**.
3. Run these commands one at a time:

```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

4. Copy `.env.example` and rename the copy to `.env`.
5. Open `.env` and replace `PASTE_YOUR_GEMINI_API_KEY_HERE` with your own Gemini API key. Keep the key private.
6. Start the app:

```powershell
python app.py
```

7. Open this address in Chrome: http://127.0.0.1:5000

## Troubleshooting

- **API key missing:** Make sure `.env` is beside `app.py`, contains your key, and restart `python app.py`.
- **429 quota error:** Your Google Gemini quota/rate limit is reached. Check https://ai.dev/rate-limit or wait for the quota to reset. UI changes cannot remove provider quota limits.
- **503 busy:** Gemini may be temporarily overloaded; wait and try again.
- **Model unavailable:** Set `GEMINI_MODEL` in `.env` to a model currently supported by your Gemini API account.
- **Backend not connected:** Keep the terminal window running and open the local URL above.

## Security

- Do not share `.env` or expose your API key in frontend files.
- `.env` is excluded from Git by `.gitignore`.
- Generated sites run inside a sandboxed iframe. Review generated HTML before publishing.
- This demo generates frontend HTML only. Contact forms, checkout and other server actions are not connected unless you add a backend.
