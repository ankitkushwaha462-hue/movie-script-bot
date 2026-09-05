import os
import telebot
import threading
import google.generativeai as genai
from http.server import HTTPServer, BaseHTTPRequestHandler

TELEGRAM_BOT_TOKEN = "8800738451:AAECG3MG16C8HB_ZlMVXFpJ-HMXBArT6UL4"
GEMINI_API_KEY = "AQ.Ab8RN6Kbuwu4ce9SnU5fG-44h7APwgjf72SUImpYQkelhjajWQ"

# Configure Official Google Gemini SDK
genai.configure(api_key=GEMINI_API_KEY)

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

SYSTEM_PROMPT = """
You are the world's best YouTube movie recap scriptwriter writing in the style of "MrHindiRockers", "The Cinema Book", and "Anokhi Films".
Produce a viral, high-retention, copyright-safe movie recap script in Hindi/Hinglish.

SCRIPT FORMAT:
1. THE PSYCHOLOGICAL HOOK (0:00 - 0:30): Shocking question or critical climax moment. Include [SFX: Bass Drop].
2. SCENE-BY-SCENE STORY: Gripping narration with [Visual: 2.5s clip] and [Visual: Freeze frame zoom] cues.
3. MICRO-CLIFFHANGERS: Build suspense every 60-90 seconds ("Lekin use nahi pata tha...").
4. CLIMAX & OUTRO: Final plot twist + comment question + call to subscribe.
5. BONUS: 3 High-CTR Clickable Titles + 1 Viral Thumbnail Concept.

Language: Engaging conversational Hindi / Hinglish.
"""

def generate_script_with_gemini(user_input):
    prompt_text = f"{SYSTEM_PROMPT}\n\nUSER REQUEST OR TRANSCRIPT:\n{user_input}\n\nGenerate script now:"
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt_text)
        if response and response.text:
            return response.text
        return "Empty response received from Gemini."
    except Exception as e:
        return f"Exact API Error: {str(e)}"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "🎬 *Namaste! Movie Recap Bot Ready Hai!*\n\n"
        "Kisi bhi movie ka naam bhejiye ya transcript paste kijiye!"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_movie_request(message):
    user_text = message.text
    chat_id = message.chat.id
    status_msg = bot.reply_to(message, "⚡ Script likhi ja rahi hai...")
    
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

# Web Server for Render
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Active!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

if __name__ == "__main__":
    print("Starting Web Server...")
    threading.Thread(target=run_web_server, daemon=True).start()
    print("Starting Telegram Bot Polling...")
    bot.infinity_polling()
