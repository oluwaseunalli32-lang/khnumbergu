import os
import random

from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup, Update)
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          ContextTypes, MessageHandler, filters)

TOKEN = os.environ["BOT_TOKEN"]
BOT_NAME = "ហ្គេមទាយលេខ - Number Guess"
MAX_TRIES = 4

BTN_PLAY = "លេងហ្គេម"
BTN_SCORE = "ពិន្ទុរបស់ខ្ញុំ"
BTN_HELP = "ជំនួយ"

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [[BTN_PLAY], [BTN_SCORE, BTN_HELP]], resize_keyboard=True
)

WELCOME = (
    f"🎮 {BOT_NAME}\n\n"
    "សូមស្វាគមន៍! ខ្ញុំកំពុងគិតពីលេខមួយចន្លោះពី ១ ដល់ ១០។ "
    "តើអ្នកអាចទាយត្រូវទេ?\n\n"
    "របៀបលេង៖\n"
    f"• ចុច «{BTN_PLAY}» ដើម្បីចាប់ផ្តើមជុំថ្មី\n"
    f"• ជ្រើសរើសលេខ អ្នកមាន {MAX_TRIES} ដងដើម្បីទាយ\n"
    "• ក្រោយការទាយខុស អ្នកនឹងទទួលបានជំនួយ៖ ធំជាងនេះ ឬ តូចជាងនេះ\n"
    f"• ចុច «{BTN_SCORE}» ដើម្បីមើលចំនួនដងដែលអ្នកទាយត្រូវ ក្នុងវគ្គនេះ"
)

HELP = (
    f"{BOT_NAME} | {BTN_HELP}\n\n"
    f"១. ចុច «{BTN_PLAY}» ដើម្បីចាប់ផ្តើម។\n"
    "២. ជ្រើសរើសលេខពី ១ ដល់ ១០។\n"
    "៣. ប្រសិនបើខុស ខ្ញុំនឹងប្រាប់ថាលេខធំជាង ឬតូចជាង។\n"
    f"៤. អ្នកមាន {MAX_TRIES} ដងក្នុងមួយជុំ។\n"
    "៥. ពិន្ទុត្រូវបានរក្សាទុកតែក្នុងវគ្គបច្ចុប្បន្ន ហើយអាចត្រូវបានកំណត់ឡើងវិញ។\n\n"
    "នេះជាហ្គេមកម្សាន្តសាមញ្ញ គ្មានរង្វាន់ ឬប្រាក់ទេ។"
)

HIGHER = "⬆️ ទាយលេខធំជាងនេះ"
LOWER = "⬇️ ទាយលេខតូចជាងនេះ"


def number_markup() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(str(n), callback_data=f"g_{n}") for n in range(1, 6)],
        [InlineKeyboardButton(str(n), callback_data=f"g_{n}") for n in range(6, 11)],
    ]
    return InlineKeyboardMarkup(rows)


def again_markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔁 លេងម្តងទៀត", callback_data="again")]])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME, reply_markup=MAIN_KEYBOARD)


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP, reply_markup=MAIN_KEYBOARD)


async def begin_round(message, context: ContextTypes.DEFAULT_TYPE):
    d = context.user_data
    d["target"] = random.randint(1, 10)
    d["tries"] = MAX_TRIES
    d["active"] = True
    await message.reply_text(
        f"{BOT_NAME}\n\nខ្ញុំបានគិតពីលេខមួយហើយ។ ជ្រើសរើសលេខពី ១ ដល់ ១០។\n"
        f"នៅសល់ {MAX_TRIES} ដង។",
        reply_markup=number_markup(),
    )


async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await begin_round(update.message, context)


async def again(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await begin_round(query.message, context)


async def guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    d = context.user_data
    if not d.get("active"):
        await query.message.reply_text(
            f"សូមចុច «{BTN_PLAY}» ដើម្បីចាប់ផ្តើមជុំថ្មី។",
            reply_markup=MAIN_KEYBOARD)
        return

    n = int(query.data.split("_", 1)[1])
    target = d["target"]
    d["tries"] -= 1

    if n == target:
        d["active"] = False
        d["wins"] = d.get("wins", 0) + 1
        d["games"] = d.get("games", 0) + 1
        await query.edit_message_text(
            f"{BOT_NAME}\n\n🎉 ត្រឹមត្រូវ! លេខគឺ {target}។",
            reply_markup=again_markup())
    elif d["tries"] <= 0:
        d["active"] = False
        d["games"] = d.get("games", 0) + 1
        await query.edit_message_text(
            f"{BOT_NAME}\n\nអស់ឱកាសហើយ។ លេខគឺ {target}។",
            reply_markup=again_markup())
    else:
        hint = HIGHER if target > n else LOWER
        await query.edit_message_text(
            f"{BOT_NAME}\n\nអ្នកបានទាយ {n}។ {hint}\nនៅសល់ {d['tries']} ដង។",
            reply_markup=number_markup())


async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = context.user_data
    await update.message.reply_text(
        f"{BOT_NAME} | {BTN_SCORE}\n\n"
        f"ទាយត្រូវ {d.get('wins', 0)} ដង ក្នុងចំណោម {d.get('games', 0)} ជុំ។")


async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"{BOT_NAME}៖ សូមជ្រើសរើសពីម៉ឺនុយខាងក្រោម។",
        reply_markup=MAIN_KEYBOARD)


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.Text([BTN_PLAY]), play))
    app.add_handler(MessageHandler(filters.Text([BTN_SCORE]), score))
    app.add_handler(MessageHandler(filters.Text([BTN_HELP]), help_cmd))
    app.add_handler(CallbackQueryHandler(again, pattern="^again$"))
    app.add_handler(CallbackQueryHandler(guess, pattern="^g_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback))
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
