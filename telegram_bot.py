import logging
import csv
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define states
NAME, LOCATION, DATE, PHONE = range(4)

# Path for the CSV file
DATA_FILE = 'user_data.csv'

# Random description paragraph
DESCRIPTION_PARAGRAPHS = [
    "Welcome! This bot helps you collect and store information such as your name, location, date, and phone number.",
    "Hello there! With this bot, you can easily provide your details, which will be securely saved for future reference.",
    "Greetings! This bot allows you to submit your personal information, including your name and location, to keep track of important dates.",
]

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    description = random.choice(DESCRIPTION_PARAGRAPHS)
    await update.message.reply_text(description)
    await update.message.reply_text("Now, what's your name?")
    return NAME

# Get name
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    await update.message.reply_text(f"Nice to meet you, {update.message.text}! Where are you located?")
    return LOCATION

# Get location
async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['location'] = update.message.text
    await update.message.reply_text(f"Got it! You are located in {update.message.text}. What date do you want to provide?")
    return DATE

# Get date
async def get_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['date'] = update.message.text
    await update.message.reply_text("Please provide your phone number:")
    return PHONE

# Get phone number and save data
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['phone'] = update.message.text
    name = context.user_data['name']
    location = context.user_data['location']
    date = context.user_data['date']
    phone = update.message.text

    # Save to CSV
    with open(DATA_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([name, location, date, phone])

    await update.message.reply_text(f"Thank you, {name}! You are located in {location}, provided the date {date}, and your phone number is {phone}.")
    return ConversationHandler.END

# Command to access data
async def access_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.id != Telegram user ID:  # Replace with your Telegram user ID
        await update.message.reply_text("You are not authorized to access this data.")
        return

    try:
        with open(DATA_FILE, mode='r') as file:
            data = file.read()
            await update.message.reply_text(f"Here is the collected data:\n{data}")
    except FileNotFoundError:
        await update.message.reply_text("No data found yet.")

# Cancel command
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Conversation canceled.')
    return ConversationHandler.END

# Main function to set up the bot
def main() -> None:
    # Replace 'YOUR_TOKEN' with your bot's API token
    application = ApplicationBuilder().token("YOUR_TOKEN").build()

    # Define conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_location)],
            DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_date)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('access_data', access_data))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()