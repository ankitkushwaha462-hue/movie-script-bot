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

def generate_script_with_gemini(user_input):
    # Step 1: Google se live active models ki list maango
    list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
    available_models = []
    
    try:
        res = requests.get(list_url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            for m in data.get("models", []):
                methods = m.get("supportedGenerationMethods", [])
                if "generateContent" in methods:
                    # Strip 'models/' prefix
                    model_id = m.get("name", "").replace("models/", "")
                    available_models.append(model_id)
    except Exception as e:
        return f"Failed to fetch models: {str(e)}"
        
    if not available_models:
        return "No text-generation models found for this API key."

    prompt_text = f"{SYSTEM_PROMPT}\n\nUSER REQUEST OR TRANSCRIPT:\n{user_input}\n\nGenerate master script now:"
    payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
    headers = {"Content-Type": "application/json"}
    
    # Step 2: Jo jo active model mila, ek ek karke try karo jab tak script na ban jaye
    errors = []
    for model_name in available_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                data = response.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                errors.append(f"{model_name} failed ({response.status_code})")
        except Exception as e:
            errors.append(f"{model_name} error: {str(e)}")
            
    return f"All available models failed. Log: {', '.join(errors)}"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "🎬 *Namaste! Movie Recap Script Bot Ready Hai!*\n\n"
        "Metro me ho ya ghar par, bas kisi movie ka naam ya transcript paste kar do.\n"
        "Script, SFX cues aur viral titles ready ho jayenge!"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_movie_request(message):
    user_text = message.text
    chat_id = message.chat.id
    status_msg = bot.reply_to(message, "⏳ Active free model dhoondh kar script generate ki ja rahi hai...")
    
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
