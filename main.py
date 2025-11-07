from tracemalloc import start
from email.mime import application
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, CallbackContext
import requests
import json
import os
from datetime import datetime
import pytz
from googleapiclient.discovery import build
from spellchecker import SpellChecker
# Bot Token
TOKEN = '7631080660:AAFVpkGCLFhHkxF31Dvuwp0zdKjd4HV8FnY'

# Initialize SpellChecker for word corrections
spell = SpellChecker()

# File for storing user preferences
PREFS_FILE = 'user_prefs.json'

# API Keys
YOUTUBE_API_KEY = 'AIzaSyDQSRsLtPIru--EJIg9MtX2eMjOxuvuddM'
WEATHER_API_KEY = '7f59948b973042e8bfd22815241211'


# --- Helper Functions --- #

def load_prefs():
    """Load user preferences from the file."""
    if os.path.exists(PREFS_FILE):
        with open(PREFS_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_prefs(prefs):
    """Save user preferences to the file."""
    with open(PREFS_FILE, 'w') as file:
        json.dump(prefs, file)

# /weather command: Fetch weather information for a city
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    city = 'Phnom Penh'
    if context.args:
        city = ' '.join(context.args)

    url = f"https://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}"
    response = requests.get(url)
    data = response.json()

    if 'error' not in data:
        weather_data = f"Weather in {city}:\nTemperature: {data['current']['temp_c']}°C\nDescription: {data['current']['condition']['text']}"
    else:
        weather_data = "Sorry, I couldn't fetch the weather data."

    await update.message.reply_text(weather_data)

# /datetime command: Get the current date and time in Cambodia
async def datetime_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    cambodia_timezone = pytz.timezone("Asia/Phnom_Penh")
    current_time = datetime.now(cambodia_timezone)
    formatted_time = current_time.strftime("%A, %Y-%m-%d %H:%M:%S")
    await update.message.reply_text(f"Current date and time in Cambodia: {formatted_time}")

# /youtube command: Search YouTube videos
async def youtube_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = ' '.join(context.args)
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    
    request = youtube.search().list(part="snippet", q=query, type="video", maxResults=3)
    response = request.execute()

    message = ""
    for item in response['items']:
        title = item['snippet']['title']
        video_id = item['id']['videoId']
        url = f"https://www.youtube.com/watch?v={video_id}"
        message += f"{title}\n{url}\n\n"

    await update.message.reply_text(message if message else "No results found.")


async def set_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    custom_response = ' '.join(context.args)
    prefs = load_prefs()

    if user_id not in prefs:
        prefs[user_id] = {}
    
    prefs[user_id]['custom_response'] = custom_response
    save_prefs(prefs)

    await update.message.reply_text(f"Custom response set to: {custom_response}")

# /help command: Show help message
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Commands:\n"
        "/start - Greet the user\n"
        "/help - Show help\n"
        "/weather - Get weather data\n"
        "/setresponse <response> - Set custom response\n"
        "/datetime - Get the current date and time in Cambodia\n"
        "/youtube <search term> - Search YouTube for videos\n"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text.strip().lower()

    if "what is pnc" in user_text or "pnc name" in user_text:
        response = (
            "Passerelles Numériques Cambodia (PNC) is a non-profit organization that provides high-quality IT education and training "
            "to underprivileged young Cambodians. It helps students build technical and professional skills to secure sustainable jobs "
            "in the digital sector and improve their families' lives."
        )

    elif "when was pnc founded" in user_text or "pnc history" in user_text:
        response = (
            "Passerelles Numériques Cambodia (PNC) was founded in 2005. It is one of the three centers of Passerelles Numériques, "
            "along with PNV (Vietnam) and PNP (Philippines). Since its creation, PNC has trained and graduated hundreds of young IT professionals."
        )

    elif "where is pnc" in user_text or "pnc location" in user_text:
        response = (
            "PNC is located in Phnom Penh, Cambodia 🇰🇭.\n"
            "The campus includes classrooms, computer labs, dormitories, and areas for student activities."
        )

    elif "what does pnc do" in user_text or "mission" in user_text or "goal" in user_text:
        response = (
            "PNC’s mission is to enable young underprivileged students to gain access to education, training, and employment in the IT sector.\n"
            "Their goal is to break the cycle of poverty through education and professional opportunities."
        )

    elif "vision" in user_text:
        response = (
            "PNC’s vision is to create a world where every young person has equal access to education, opportunities, and a better future "
            "through digital and personal empowerment."
        )

    elif "program" in user_text or "courses" in user_text or "training" in user_text:
        response = (
            "PNC offers a 3-year IT training program focusing on web development and networking.\n"
            "Students also study English, personal development, and soft skills to prepare them for their professional careers."
        )

    elif "selection" in user_text or "recruitment" in user_text or "who can apply" in user_text or "apply" in user_text:
        response = (
            "PNC recruits students from underprivileged backgrounds across Cambodia. The selection process includes written tests, "
            "interviews, and family visits to ensure fairness and motivation.\n"
            "Selected students receive full scholarships, including tuition, food, and accommodation."
        )

    elif "scholarship" in user_text or "free" in user_text or "tuition" in user_text:
        response = (
            "Yes! PNC provides a *full scholarship* for every student, covering tuition, meals, dormitory, medical care, and materials. "
            "Students don’t have to pay anything — they just need strong motivation and commitment."
        )

    elif "daily life" in user_text or "student life" in user_text or "activity" in user_text:
        response = (
            "PNC students live on campus where they study IT, English, and life skills. They also join clubs, sports, community service, "
            "and leadership programs. The environment promotes teamwork, discipline, and personal growth."
        )

    elif "dorm" in user_text or "accommodation" in user_text:
        response = (
            "PNC provides safe and comfortable dormitories for all students, separated by gender. "
            "Dorms are located on campus, close to classrooms and facilities."
        )

    elif "internship" in user_text or "job training" in user_text:
        response = (
            "In the third year, PNC students complete a 6-month internship in a company. This allows them to gain real-world experience "
            "and apply their IT and communication skills before graduation."
        )

    elif "after graduation" in user_text or "graduates" in user_text or "alumni" in user_text:
        response = (
            "After graduation, most PNC students find jobs quickly — the employment rate is over 90%! "
            "Many graduates work in IT companies, banks, or start their own businesses. "
            "The alumni network helps connect new graduates with job opportunities."
        )

    elif "partners" in user_text or "supporters" in user_text or "sponsors" in user_text:
        response = (
            "PNC is supported by companies, NGOs, and private donors. Partners provide financial support, internships, "
            "equipment, and mentorship to students. Collaboration with the private sector is key to PNC’s success."
        )

    elif "impact" in user_text or "success" in user_text or "achievement" in user_text:
        response = (
            "PNC has changed the lives of more than a thousand young Cambodians. Graduates support their families, "
            "contribute to the country's digital growth, and inspire others to pursue education. "
            "PNC is recognized as a leading social organization in Cambodia’s tech education sector."
        )

    elif "staff" in user_text or "teachers" in user_text or "mentors" in user_text:
        response = (
            "PNC has a dedicated team of local and international staff who teach IT, English, and soft skills. "
            "They also mentor students to help them succeed both academically and personally."
        )

    elif "partner with pnc" in user_text or "collaborate with pnc" in user_text or "donate" in user_text:
        response = (
            "Organizations and individuals can support PNC by offering internships, funding, equipment, or mentorship.\n"
            "If you’d like to contribute, visit their website for partnership or donation information:\n"
            "👉 https://www.passerellesnumeriques.org/what-we-do/cambodia"
        )

    elif "pnc website" in user_text or "official site" in user_text or "more info" in user_text:
        response = (
            "You can learn more about Passerelles Numériques Cambodia on their official website 🌐:\n"
            "https://www.passerellesnumeriques.org/what-we-do/cambodia"
        )

    elif "thank" in user_text or "thanks" in user_text:
        response = (
            "You're welcome! 😊 PNC believes in changing lives through education. Feel free to ask me more about it anytime!"
        )

    elif "hello" in user_text or "hi" in user_text:
        response = (
            "Hello! 👋 I’m your PNC info bot. Ask me anything about Passerelles Numériques Cambodia — "
            # "programs, mission, selection, student life, or how to apply!"
        )
    elif "students 2021" in user_text or "2021" in user_text:
        response = (
            "In 2021, around 120 new students joined PNC, totaling about 280 students. 📚\n"
            "It was a challenging year due to COVID-19, but learning continued online and on campus."
        )
    elif "students 2022" in user_text or "2022" in user_text:
        response = (
            "In 2022, about 130 new students joined, bringing the total to around 290. 👩‍💻\n"
            "The program fully resumed on campus, and many students prepared for internships."
        )
    elif "students 2023" in user_text or "2023" in user_text:
        response = (
            "In 2023, approximately 140 new students joined the PNC family! 🎉\n"
            "That year, the total number of active students reached about 300, and digital training improved greatly."
        )
    elif "students 2024" in user_text or "2024" in user_text:
        response = (
            "In 2024, PNC welcomed around 150 new students, reaching about 310 total. 🌟\n"
            "More female students joined, and new software development modules were introduced."
        )
    elif "students 2025" in user_text or "2025" in user_text:
        response = (
            "In 2025, PNC had around 150 new students, totaling about 320. 💻\n"
            "Graduates from this year achieved over 90% employment in IT companies in Cambodia!"
        )
    elif "students 2026" in user_text or "2026" in user_text:
        response = (
            "By 2026, PNC expects about 160 new students, bringing the total to around 330 learners. 🚀\n"
            "The organization continues to grow and empower more Cambodian youth through digital education."
        )
    else:
        response = "I didn't quite get that. Could you please clarify?"

    await update.message.reply_text(response)
# --- Inline Button Handlers --- #

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    action = {
        'weather': "Please type /weather <city> to get the weather.",
        'youtube': "Please type /youtube <search term> to search YouTube.",
        'datetime': "Please type /datetime to get the current date and time in Cambodia."
    }.get(query.data, "Unknown option selected.") 
    await query.edit_message_text(action)

# --- Start Command --- #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Greet the user with buttons and intro."""
    keyboard = [
        [
            InlineKeyboardButton("🌤 Weather", callback_data='weather'),
            InlineKeyboardButton("📺 YouTube", callback_data='youtube'),
        ],
        [
            InlineKeyboardButton("🕒 Date & Time", callback_data='datetime')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Hello! I'm your learning assistant bot.\n\n"
        "You can ask me programming questions or use the buttons below to explore features:",
        reply_markup=reply_markup
    )


def main():

    """Main entry point for the bot."""
    application = ApplicationBuilder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("weather", weather))
    application.add_handler(CommandHandler("datetime", datetime_command))
    application.add_handler(CommandHandler("setresponse", set_response))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.run_polling()

if __name__ == '__main__':
    main()
