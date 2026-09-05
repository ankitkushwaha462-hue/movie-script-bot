import os
import telebot
import requests
import json

TELEGRAM_BOT_TOKEN = "8800738451:AAECG3MG16C8HB_ZlMVXFpJ-HMXBArT6UL4"
GEMINI_API_KEY = "AQ.Ab8RN6IMXhYaOyuSNyZv37ivYQ6TK9UD2gsyq0ER68aA7h-lRg"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

SYSTEM_PROMPT = """
You are an expert movie explanation and recap scriptwriter for top YouTube channels like "MrHindiRockers", "Anokhi Films", and "The Cinema Book".
Your goal is to write a highly engaging, suspenseful, and retention-focused movie recap script in Hindi / Hinglish.

Rules for Writing:
1. THE HOOK (0:00 - 0:35):
   - Never say generic openings like "Hello friends, welcome to the channel".
   - Start immediately with a high-stakes, shocking question or the most critical climax scene to create intense curiosity.
   - Example: "Sochiye agar aapki ek galti ki wajah se..."
   
2. STORYTELLING FLOW:
   - Use gripping storytelling tone (like a Dastango / narrator).
   - Use dramatic words: "Lekin use nahi pata tha...", "Achanak ek aisi anhoni hoti hai...", "Khel tab palat gaya jab..."
   - Include visual cues in brackets, e.g., [Visual: 2-sec clip of hero running], [SFX: Bass Drop], [Visual: Freeze frame image zoom-in].
   - Maintain a 2-3 second video clip + image pacing style to ensure copyright safety.

3. ENDING & CALL TO ACTION:
   - Deliver the final plot twist with impact.
   - Ask an engaging question to the audience to boost comments.
   - Subtle outro: "Agar explanation pasand aayi ho toh LIKE karein aur aisi hi kahaniyo ke liye SUBSCRIBE zaroor karein."

Format output cleanly with timestamps, visual cues, and voiceover text.
"""

def generate_script_with_gemini(user_input):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    prompt_text = f"{SYSTEM_PROMPT}\n\nUser request or transcript to adapt:\n{user_input}\n\nPlease generate the full Hindi recap script now:"
    
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
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"Error from Gemini API ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Request failed: {str(e)}"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "🎬 Namaste! Movie Recap Script Bot ready hai!\n\nMetro me ho ya office me, bas mujhe kisi movie ka naam ya transcript paste kar do. Main MrHindiRockers / The Cinema Book style me Hindi script bana kar dunga!\n\nTry kijiye, kisi movie ka naam bhejiye.")

@bot.message_handler(func=lambda message: True)
def handle_movie_request(message):
    user_text = message.text
    chat_id = message.chat.id
    
    status_msg = bot.reply_to(message, "⏳ Script likhi ja rahi hai... (30-40 seconds lagenge, intezaar kijiye)...")
    
    script = generate_script_with_gemini(user_text)
    
    if len(script) > 4000:
        chunks = [script[i:i+4000] for i in range(0, len(script), 4000)]
        for idx, chunk in enumerate(chunks):
            if idx == 0:
                bot.edit_message_text(chunk, chat_id=chat_id, message_id=status_msg.message_id)
            else:
                bot.send_message(chat_id, chunk)
    else:
        bot.edit_message_text(script, chat_id=chat_id, message_id=status_msg.message_id)

if __name__ == "__main__":
    print("Bot is starting...")
    bot.infinity_polling()
