import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, \
    JobQueue

# Insert your token here
TOKEN = '7166182218:AAGXmE-E42GkUper1Mx-cmnFuypAQbU7734'

# Admin group chat ID
ADMIN_GROUP_CHAT_ID = -1002160161537  # Replace with your admin group's chat ID

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Dictionary to keep track of active conversations
active_conversations = {}


# Command /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = update.message.from_user.first_name  # Get user's first name
    keyboard = [
        [InlineKeyboardButton("Русский", callback_data='lang_ru')],
        [InlineKeyboardButton("Українська", callback_data='lang_ua')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"Добрый день, {user_name}!\n\n"
        "Пожалуйста, выберите язык / Будь ласка, оберіть мову.",
        reply_markup=reply_markup
    )


# Language selection handler
async def lang_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_name = query.from_user.first_name  # Get user's first name

    if query.data == 'lang_ru':
        context.user_data['lang'] = 'ru'
        await query.message.reply_text(
            f"Добро пожаловать, {user_name}!\n\n"
            "Вас приветствует Otec Karlo.\n\n"
            "Выберите услугу.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Купить Problem Set", callback_data='buy_problem_set')],
            ])
        )
    elif query.data == 'lang_ua':
        context.user_data['lang'] = 'ua'
        await query.message.reply_text(
            f"Ласкаво просимо, {user_name}!\n\n"
            "Вас вітає Otec Karlo.\n\n"
            "Оберіть послугу.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Купити Problem Set", callback_data='buy_problem_set')],
            ])
        )


# Command /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name  # Get user's first name
    lang = context.user_data.get('lang', 'ru')

    # Notify the admin group
    sent_message = await context.bot.send_message(
        chat_id=ADMIN_GROUP_CHAT_ID,
        text=f"Пользователь {user_name} (@{update.message.from_user.username}, {user_id}, {'RU' if lang == 'ru' else 'UA'}) запросил поддержку."
    )

    # Store the active conversation
    active_conversations[user_id] = sent_message.message_id

    await update.message.reply_text(
        "Ваша заявка на поддержку принята. Мы свяжемся с вами в ближайшее время." if lang == 'ru' else
        "Ваш запит на підтримку прийнято. Ми зв'яжемося з вами найближчим часом."
    )


# Button handler
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_name = query.from_user.first_name  # Get user's first name
    lang = context.user_data.get('lang', 'ru')

    if query.data == 'buy_problem_set':
        keyboard = [
            [InlineKeyboardButton("Купить" if lang == 'ru' else "Купити", callback_data='confirm_purchase')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            "Problem Set 1: Karel the Robot.\n\n"
            "Цена - 50 EUR.\n\n"
            "Лабораторная будет выполнена на максимальный балл. Также гарантируем антиплагиат. В случае приглашения вашего друга/знакомого на нашу платформу и осуществления покупки - вам будет дано 10 евро, а тому, кого пригласили - скидка 10 евро.\n\n"
            "Если вас заинтересовала покупка, то нажмите на кнопку 'Купить'." if lang == 'ru' else
            "Problem Set 1: Karel the Robot.\n\n"
            "Ціна - 50 EUR.\n\n"
            "Лабораторна робота буде виконана на максимальний бал. Також гарантуємо антиплагіат. У разі запрошення вашого друга/знайомого на нашу платформу та здійснення покупки - вам буде дано 10 євро, а тому, кого запросили - знижка 10 євро.\n\n"
            "Якщо вас зацікавила покупка, то натисніть на кнопку 'Купити'.",
            reply_markup=reply_markup
        )

    elif query.data == 'confirm_purchase':
        await query.message.reply_text(
            "В таком случае вам нужно будет внести предоплату на словацкий счет в размере 25 евро.\n\n"
            "С вами свяжется наш сотрудник и отправит вам часть работы. Вы проверите, что все работает. После чего вы внесете остальную сумму оплаты и мы отправим вам полную работу. Если данное предложение вас устраивает, то напишите '+'." if lang == 'ru' else
            "У такому разі вам потрібно буде внести передоплату на словацький рахунок у розмірі 25 євро.\n\n"
            "З вами зв'яжеться наш співробітник і відправить вам частину роботи. Ви перевірите, що все працює. Після чого ви внесете решту суми оплати і ми надішлемо вам повну роботу. Якщо вас влаштовує ця пропозиція, напишіть '+'."
        )


# Text message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.lower()  # Convert message text to lowercase
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name  # Get user's first name
    chat_id = update.message.chat_id
    lang = context.user_data.get('lang', 'ru')

    if text == '+':
        # Respond to the user with an auto-reply
        await update.message.reply_text(
            "Спасибо за подтверждение! Мы свяжемся с вами в ближайшее время." if lang == 'ru' else
            "Дякую за підтвердження! Ми зв'яжемося з вами найближчим часом."
        )

    # If the message is from a client
    if chat_id != ADMIN_GROUP_CHAT_ID:
        # Forward the message to the admin group
        sent_message = await context.bot.send_message(
            chat_id=ADMIN_GROUP_CHAT_ID,
            text=f"Сообщение от {user_name} (@{update.message.from_user.username}, {user_id}, {'RU' if lang == 'ru' else 'UA'}): {update.message.text}"
        )
        # Save the active conversation
        active_conversations[user_id] = sent_message.message_id
    else:
        # If the message is from the admin group, forward it to the corresponding user
        if update.message.reply_to_message:
            original_message_id = update.message.reply_to_message.message_id
            # Find the user_id associated with this conversation
            for user, msg_id in active_conversations.items():
                if msg_id == original_message_id:
                    target_user_id = user
                    await context.bot.send_message(
                        chat_id=target_user_id,
                        text=update.message.text
                    )
                    break


async def set_commands(context: ContextTypes.DEFAULT_TYPE) -> None:
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Вызвать поддержку")
    ]
    await context.bot.set_my_commands(commands)


def main() -> None:
    # Create the application and pass it your bot's token
    application = Application.builder().token(TOKEN).job_queue(JobQueue()).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(lang_selection, pattern='^lang_'))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Set the commands at the start of the bot
    application.job_queue.run_once(set_commands, when=1)

    # Start the bot
    application.run_polling()


if __name__ == '__main__':
    main()
