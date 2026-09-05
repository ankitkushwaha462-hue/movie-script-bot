import os
import telebot
import requests
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

TELEGRAM_BOT_TOKEN = "8800738451:AAECG3MG16C8HB_ZlMVXFpJ-HMXBArT6UL4"
GEMINI_API_KEY = "AIzaSyAKYg2uLUDjd9piFmljeBUX8x4Uc239ucU"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

SYSTEM_PROMPT = """
You are the world's best YouTube movie recap scriptwriter writing in the style of "MrHindiRockers", "The Cinema Book", and "Anokhi Films".
Produce a viral, high-retention, copyright-safe movie recap script in Hindi/Hinglish.

SCRIPT FORMAT:
1. THE PSYCHOLOGICAL HOOK (0:00 - 0:30): Shocking question or critical climax moment. Include [SFX: Bass Drop].
2. SCENE-BY-SCENE STORY: Gripping narration with [Visual: 2.5s clip] and [Visual: Freeze frame zoom] cues.
3. MICRO-CLIFFHANGERS: Build suspense every 60-90 seconds ("Lekin use nahi pata tha...").
4. CLIMAX & OUTRO: Final plot twist + comment question + call to subscribe.
5. BONUS: 3 High-CTR Clickable Titles + 1 Viral Thumbnail Concept + 5 SEO Keywords.

Language: Engaging conversational Hindi / Hinglish.
"""

def get_best_model():
    # Automatically get the supported model for this API key
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            for m in data.get("models", []):
                name = m.get("name", "")
                methods = m.get("supportedGenerationMethods", [])
                if "generateContent" in methods and "flash" in name:
                    return name.replace("models/", "")
            # Fallback to any model that supports generateContent
            for m in data.get("models", []):
                if "generateContent" in m.get("supportedGenerationMethods", []):
                    return m.get("name", "").replace("models/", "")
    except Exception:
        pass
    return "gemini-2.0-flash"

def generate_script_with_gemini(user_input):
    model_name = get_best_model()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
    
    headers = {"Content-Type": "application/json"}
    prompt_text = f"{SYSTEM_PROMPT}\n\nUSER REQUEST OR TRANSCRIPT:\n{user_input}\n\nGenerate master script now:"
    payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=90)
        if response.status_code == 200:
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"Error from model {model_name} ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Request failed: {str(e)}"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "🎬 *Namaste! Movie Recap Script Bot Ready Hai!*\n\n"
        "Metro me ho ya ghar par, bas kisi movie ka naam ya transcript paste kar do.\n"
        "Script, SFX cues aur viral titles turant ready ho jayenge!"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_movie_request(message):
    user_text = message.text
    chat_id = message.chat.id
    status_msg = bot.reply_to(message, "⏳ Script generate ho rahi hai...")
    
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
