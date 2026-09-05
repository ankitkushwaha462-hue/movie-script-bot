GREETINGS = ["hi", "hello", "hey", "hii", "helo", "kaise ho", "kya haal", "namaste", "namaskar", "hola"]

@bot.message_handler(func=lambda message: True)
def handle_movie_request(message):
    user_text = message.text.strip().lower()
    chat_id = message.chat.id

    # Greeting detect karo
    if any(user_text == greet or user_text.startswith(greet) for greet in GREETINGS):
        bot.reply_to(message, 
            "👋 *Namaste! Main bilkul ready hoon!*\n\n"
            "Kisi bhi movie ka naam ya YouTube transcript paste karo, "
            "main turant *MrHindiRockers style* me full script bana dunga! 🎬",
            parse_mode="Markdown"
        )
        return

    # Script generation sirf movie/transcript request par
    status_msg = bot.reply_to(message, "⏳ Active free model dhoondh kar script generate ki ja rahi hai...")
    script = generate_script_with_gemini(message.text)

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
