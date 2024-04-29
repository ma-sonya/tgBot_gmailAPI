# telegram bot
from telegram.ext import (Updater, CommandHandler, ConversationHandler, MessageHandler,
                          Filters, CallbackContext)
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from email_data import Email
import os
# gmail API
from Google import Create_Service
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

CLIENT_SECRET_FILE = 'credentials.json'
API_NAME = 'gmail'
API_VERSION = 'v1'
SCOPES = ['https://mail.google.com/']

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

USER_TO_SEND, SUBJ_TO_SEND, MSG_TO_SEND = range (3)
TOKEN = os.getenv("TOKEN")
ADD_GMAIL_TEXT = "Create and send email 🕊📨"

def send_message(email: Email):
    mimeMessage = MIMEMultipart()
    mimeMessage['to'] = email.receiver
    mimeMessage['subject'] = email.subj
    mimeMessage.attach(MIMEText(email.message, 'plain'))
    raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()
    service.users().messages().send(userId='me', body={'raw': raw_string}).execute()

def start_handler(update, context):
    update.message.reply_text("Hello there!", reply_markup=add_gmail_button())

def add_gmail_button():
    keyboard = [[KeyboardButton(ADD_GMAIL_TEXT)]]
    return ReplyKeyboardMarkup(keyboard)

def add_gmail_handler(update: Update, context: CallbackContext):
    update.message.reply_text("Please enter an address you want to send an email:")
    return USER_TO_SEND

def user2send_handler(update: Update, context: CallbackContext):
    update.message.reply_text("Please enter a subject to your email:")
    context.user_data["message_receiver"] = update.message.text
    return SUBJ_TO_SEND

def subj2send_handler(update: Update, context: CallbackContext):
    update.message.reply_text("Please enter main text:")
    context.user_data["message_subject"] = update.message.text
    return MSG_TO_SEND

def msg2send_handler(update: Update, context: CallbackContext):
    update.message.reply_text("Your email was successfully sent!🙌")
    message_receiver = context.user_data["message_receiver"]
    message_subject = context.user_data["message_subject"]
    message_text = update.message.text
    send_message(Email(message_receiver, message_subject, message_text))
    update.message.reply_text("Send message again👇", reply_markup=add_gmail_button())
    return ConversationHandler.END

if __name__ == '__main__':
    updater = Updater(TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler("start", start_handler))
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(ADD_GMAIL_TEXT), add_gmail_handler)],
        states={
            USER_TO_SEND: [MessageHandler(Filters.all, user2send_handler)],
            SUBJ_TO_SEND: [MessageHandler(Filters.all, subj2send_handler)],
            MSG_TO_SEND: [MessageHandler(Filters.all, msg2send_handler)]
        },
        fallbacks=[]
    )
    updater.dispatcher.add_handler(conv_handler)
    updater.start_polling()