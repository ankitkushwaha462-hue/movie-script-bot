import os
import telebot
import requests
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

TELEGRAM_BOT_TOKEN = "8800738451:AAECG3MG16C8HB_ZlMVXFpJ-HMXBArT6UL4"
GEMINI_API_KEY = "AQ.Ab8RN6Kbuwu4ce9SnU5fG-44h7APwgjf72SUImpYQkelhjajWQ"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

SYSTEM_PROMPT = """
You are the world's best YouTube movie recap scriptwriter writing in the style of "MrHindiRockers", "The Cinema Book", and "Anokhi Films".
Produce a viral, high-retention, copyright-safe movie recap script in Hindi/Hinglish.

SCRIPTWRITING BLUEPRINT:
1. THE PSYCHOLOGICAL HOOK (0:00 - 0:35):
   - Never say generic greetings. Start immediately with a high-stakes question or shocking climax moment.
   - Include [SFX: Bass Drop / Heartbeat] and [Visual: 2-sec clip + Freeze Frame Zoom].

2. PACING & COPYRIGHT SAFETY:
   - Strict rule: No video clip runs longer than 2.5 - 3 seconds.
   - Use visual cues: [Visual: 2.5s clip of action], [Visual: High-res freeze frame + slow zoom].

3. MICRO-CLIFFHANGERS:
   - Build suspense every 60-90 seconds ("Lekin use andaza nahi tha ki asli musibat ab shuru hone wali thi...").

4. AUDIO & SFX CUES:
   - [BGM: Suspense Strings], [BGM: Sudden Silence], [SFX: Dramatic Thud].

5. CLIMAX & OUTRO:
   - Final plot twist with impact + audience debate question + subscribe call.

6. BONUS PACK:
   - 3 High-CTR Clickable Titles.
   - 1 Viral Thumbnail Concept (Left/Right composition, text overlay).
   - 5 Target SEO Keywords.

Language: Engaging conversational Hindi / Hinglish with Urdu storytelling flair.
"""

def generate_script_with_gemini(user_input):
    # Tested and official endpoint from Google curl quickstart
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
    
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY
    }
    
    prompt_text = f"{SYSTEM_PROMPT}\n\nUSER MOVIE REQUEST OR TRANSCRIPT:\n{user_input}\n\nGenerate the complete master script now:"
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt_text}
                ]
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=90)
        if response.status_code == 200:
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"API Error ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Network Error: {str(e)}"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "🎬 *Movie Recap Script Bot Active Hai!*\n\nMovie ka naam ya transcript bhej do, script turant ready ho jayegi.", parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_movie_request(message):
    user_text = message.text
    chat_id = message.chat.id
    status_msg = bot.reply_to(message, "⏳ Script likhi ja rahi hai... thoda intezaar kijiye...")
    
    script = generate_script_with_gemini(user_text)
    
    if len(script) > 4000:
        chunks = [script[i:i+4000] for i in range(0, len(script), 4000)]
        for idx, chunk in enumerate(chunks):
            if idx == 0:
                try:
                    bot.edit_message_text(chunk, chat_id=chat_id, message_id=status_msg.message_id)
                except Exception:
                    bot.send_message(chat_id, chunk)
            else:
                bot.send_message(chat_id, chunk)
    else:
        try:
            bot.edit_message_text(script, chat_id=chat_id, message_id=status_msg.message_id)
        except Exception:
            bot.send_message(chat_id, script)

# Dummy web server for Render Free Web Service
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Running 24/7!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

if __name__ == "__main__":
    print("Starting Web Server...")
    threading.Thread(target=run_web_server, daemon=True).start()
    print("Starting Telegram Bot Polling...")
    bot.infinity_polling()
