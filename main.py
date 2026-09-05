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
You are the world's best YouTube movie recap scriptwriter and retention strategist, writing in the style of top channels like "MrHindiRockers", "The Cinema Book", and "Anokhi Films".
Your goal is to produce a viral, high-retention, copyright-safe movie recap script in Hindi/Hinglish.

SCRIPTWRITING BLUEPRINT:

1. THE PSYCHOLOGICAL HOOK (0:00 - 0:35):
   - Never say "Welcome to the channel" or generic greetings.
   - Start immediately with a high-stakes question, extreme moral dilemma, or the shocking climax moment.
   - Example tone: "Sochiye agar aap ek aise kamre me band ho jayein jahan se nikalne ka sirf ek hi rasta ho..."
   - Include [SFX: Bass Drop / Heartbeat] and [Visual: 2-sec clip + Freeze Frame Zoom].

2. PACING & COPYRIGHT SAFETY (Visual Cues):
   - Strict rule: No video clip runs longer than 2.5 - 3 seconds.
   - Specify visual cues cleanly:
     * [Visual: 2.5s clip of action]
     * [Visual: High-res freeze frame + slow Ken Burns zoom]
     * [Visual: Subtle blur overlay / newspaper clipping]

3. MICRO-CLIFFHANGERS (Every 60-90 seconds):
   - Never let the story sound like a boring flat summary.
   - Every 90 seconds, drop a curiosity gap:
     * "Lekin use andaza bhi nahi tha ki asli musibat toh ab shuru hone wali thi..."
     * "Ab yahan par hero ek aisi galti karta hai jo sab kuch badal degi..."

4. AUDIO & SFX DIRECTION:
   - Provide clear cues for editing:
     * [BGM: Slow Suspense Strings]
     * [BGM: Sudden Silence - Tension Peak]
     * [SFX: Glass break / Door creak / Dramatic Thud]

5. CLIMAX TWIST & ENGAGING OUTRO:
   - Deliver the ending twist with maximum dramatic impact.
   - Ask an open-ended debate question to trigger comments.
   - Smooth outro: "Agar kahani pasand aayi ho toh LIKE karein aur aisi hi thrilling movies ke liye SUBSCRIBE zaroor karein."

6. BONUS PACK AT THE END (FOR YOUTUBE & PPC OPTIMIZATION):
   - Provide:
     * 3 High-CTR Clickable Titles (Curiosity-driven, not clickbait).
     * 1 Viral Thumbnail Concept (Detailed visual description of left side, right side, text overlay, and color scheme).
     * 5 Target SEO Keywords.

Language: Engaging conversational Hindi / Hinglish with Urdu storytelling flair. Professional, serious, and cinematic.
"""

def generate_script_with_gemini(user_input):
    prompt_text = f"{SYSTEM_PROMPT}\n\nUSER MOVIE REQUEST OR TRANSCRIPT:\n{user_input}\n\nGenerate the complete master script, visual cues, sound effects, titles, and thumbnail idea now:"
    
    models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-flash-latest"]
    
    for m in models:
        try:
            model = genai.GenerativeModel(m)
            response = model.generate_content(prompt_text)
            if response and response.text:
                return response.text
        except Exception as e:
            continue
            
    return "Error: Unable to generate script right now. Please verify API key."

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "🎬 *Namaste! Master Movie Recap Script Bot Ready Hai!*\n\n"
        "Metro me ho ya ghar par, bas mujhe:\n"
        "1. Kisi movie ka naam bhej do, YA\n"
        "2. Kisi video ka transcript paste kar do.\n\n"
        "Main aapko *MrHindiRockers & The Cinema Book* style me:\n"
        "✅ High-Retention 30s Hook\n"
        "✅ Scene-by-Scene Script + 2-3 sec visual cues\n"
        "✅ Sound Effects & BGM timings\n"
        "✅ 3 Viral Titles + Thumbnail Concept + Tags\n\n"
        "Try kijiye, kisi movie ka naam bhejiye!"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_movie_request(message):
    user_text = message.text
    chat_id = message.chat.id
    status_msg = bot.reply_to(message, "⏳ Master Script likhi ja rahi hai... (30-45 seconds lagenge, intezaar kijiye)...")
    
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
        self.wfile.write(b"Movie Recap Bot is Active 24/7!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

if __name__ == "__main__":
    print("Starting Web Server...")
    threading.Thread(target=run_web_server, daemon=True).start()
    print("Starting Telegram Bot Polling...")
    bot.infinity_polling()
