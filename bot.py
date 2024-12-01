import os
import logging
import smtplib
import re
from email.mime.text import MIMEText
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext



logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None


def send_email(to_email, message):
    from_email = os.getenv('EMAIL')  
    app_password =  os.getenv('PASSWORD') 

    msg = MIMEText(message)
    msg['Subject'] = 'Сообщение от Telegram бота'
    msg['From'] = from_email
    msg['To'] = to_email

    try:
        with smtplib.SMTP_SSL('smtp.yandex.ru', 465) as server:
            server.login(from_email, app_password)  
            server.sendmail(from_email, to_email, msg.as_string())
        return True
    except Exception as e:
        logger.error(f"Ошибка при отправке email: {e}")
        return False


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Пожалуйста, введите ваш email:')
    context.user_data['awaiting_email'] = True  


def handle_text(update: Update, context: CallbackContext) -> None:
    if context.user_data.get('awaiting_email', False): 
        email = update.message.text.strip() 
        if is_valid_email(email):
            context.user_data['email'] = email
            context.user_data['awaiting_email'] = False  
            update.message.reply_text('Спасибо! Теперь введите текст сообщения:')
        else:
            logger.warning(f"Неверный email: {email}")
            update.message.reply_text('Неверный email. Пожалуйста, введите корректный email:')
    elif 'email' in context.user_data:  
        email = context.user_data['email']
        message = update.message.text
        if send_email(email, message):
            update.message.reply_text('Сообщение успешно отправлено!')
            context.user_data.clear() 
        else:
            update.message.reply_text('Ошибка при отправке сообщения.')
    else:
        update.message.reply_text('Сначала введите ваш email.')

def main() -> None:

    updater = Updater(os.getenv('TOKEN'))
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()