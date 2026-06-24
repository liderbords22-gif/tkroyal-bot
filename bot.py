import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, ContextTypes, filters
)

# ==================== تنظیمات ====================
TOKEN = "8914799757:AAHG4SkCFFAhqa0POVzMYRuAlJj3p0cEVZg"
CHANNEL_ID = "@Lio_Sep"
ADMIN_ID = 7442300373

# ==================== مراحل ====================
(
    CHOOSE_ACTION,
    MARCH_COUNTRY, MARCH_ORIGIN, MARCH_DEST, MARCH_TYPE, MARCH_STATS,
    WAR_COUNTRY, WAR_ORIGIN, WAR_DEST, WAR_STATS,
    DECLARE_COUNTRY, DECLARE_TEXT,
    AMBUSH_LINK, AMBUSH_STATS
) = range(14)

logging.basicConfig(level=logging.INFO)

# ==================== منوی اصلی ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⚔️ لشکرکشی", callback_data="march")],
        [InlineKeyboardButton("🗡️ جنگ", callback_data="war")],
        [InlineKeyboardButton("📜 بیانیه", callback_data="declare")],
        [InlineKeyboardButton("🏹 کمین", callback_data="ambush")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🏰 *به ربات سه پادشاهی خوش آمدید*\n\nعملیات مورد نظر را انتخاب کنید:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return CHOOSE_ACTION

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⚔️ لشکرکشی", callback_data="march")],
        [InlineKeyboardButton("🗡️ جنگ", callback_data="war")],
        [InlineKeyboardButton("📜 بیانیه", callback_data="declare")],
        [InlineKeyboardButton("🏹 کمین", callback_data="ambush")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text(
        "🏰 *منوی اصلی*\n\nعملیات مورد نظر را انتخاب کنید:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return CHOOSE_ACTION

# ==================== لشکرکشی ====================
async def march_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("⚔️ *لشکرکشی*\n\n🏴 اسم کشور خود را وارد کنید:", parse_mode="Markdown")
    return MARCH_COUNTRY

async def march_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["march_country"] = update.message.text
    await update.message.reply_text("📍 مبدأ لشکرکشی:")
    return MARCH_ORIGIN

async def march_origin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["march_origin"] = update.message.text
    await update.message.reply_text("🎯 مقصد لشکرکشی:")
    return MARCH_DEST

async def march_dest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["march_dest"] = update.message.text
    keyboard = [
        [InlineKeyboardButton("⚔️ تهاجمی", callback_data="mt_attack")],
        [InlineKeyboardButton("🛡️ دفاعی", callback_data="mt_defense")],
        [InlineKeyboardButton("🏰 تصرف", callback_data="mt_capture")],
        [InlineKeyboardButton("🔱 غارت", callback_data="mt_raid")],
    ]
    await update.message.reply_text(
        "📋 نوع لشکرکشی را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MARCH_TYPE

async def march_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    types = {
        "mt_attack": "⚔️ تهاجمی",
        "mt_defense": "🛡️ دفاعی",
        "mt_capture": "🏰 تصرف",
        "mt_raid": "🔱 غارت"
    }
    context.user_data["march_type"] = types[update.callback_query.data]
    await update.callback_query.message.reply_text("📊 آمار لشکر (تعداد سربازان، سواره‌نظام، و...):")
    return MARCH_STATS

async def march_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["march_stats"] = update.message.text
    now = datetime.now().strftime("%H:%M — %Y/%m/%d")
    d = context.user_data
    user = update.message.from_user
    username = f"@{user.username}" if user.username else user.full_name

    # پیام چنل
    channel_msg = (
        f"⚔️ *لشکرکشی*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🏴 کشور: *{d['march_country']}*\n"
        f"📍 مبدأ: *{d['march_origin']}*\n"
        f"🎯 مقصد: *{d['march_dest']}*\n"
        f"📋 نوع: *{d['march_type']}*\n"
        f"📊 آمار: {d['march_stats']}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🕐 زمان: {now}"
    )

    # پیام ادمین
    admin_msg = (
        f"📋 *گزارش لشکرکشی جدید*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👤 فرستنده: {username} (`{user.id}`)\n"
        f"🏴 کشور: {d['march_country']}\n"
        f"📍 مبدأ: {d['march_origin']}\n"
        f"🎯 مقصد: {d['march_dest']}\n"
        f"📋 نوع: {d['march_type']}\n"
        f"📊 آمار: {d['march_stats']}\n"
        f"🕐 زمان: {now}"
    )

    await context.bot.send_message(CHANNEL_ID, channel_msg, parse_mode="Markdown")
    await context.bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")
    await update.message.reply_text("✅ لشکرکشی در چنل ثبت شد!")

    keyboard = [[InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_menu")]]
    await update.message.reply_text("بازگشت به منو:", reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSE_ACTION

# ==================== جنگ ====================
async def war_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("🗡️ *جنگ*\n\n🏴 اسم کشور خود را وارد کنید:", parse_mode="Markdown")
    return WAR_COUNTRY

async def war_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["war_country"] = update.message.text
    await update.message.reply_text("📍 مبدأ:")
    return WAR_ORIGIN

async def war_origin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["war_origin"] = update.message.text
    await update.message.reply_text("🎯 مقصد (کشور دشمن):")
    return WAR_DEST

async def war_dest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["war_dest"] = update.message.text
    await update.message.reply_text("📊 آمار جنگ (تلفات، غنائم، نتیجه و...):")
    return WAR_STATS

async def war_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["war_stats"] = update.message.text
    now = datetime.now().strftime("%H:%M — %Y/%m/%d")
    d = context.user_data
    user = update.message.from_user
    username = f"@{user.username}" if user.username else user.full_name

    channel_msg = (
        f"🗡️ *جنگ*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🏴 کشور: *{d['war_country']}*\n"
        f"📍 مبدأ: *{d['war_origin']}*\n"
        f"🎯 دشمن: *{d['war_dest']}*\n"
        f"📊 آمار: {d['war_stats']}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🕐 زمان: {now}"
    )

    admin_msg = (
        f"📋 *گزارش جنگ جدید*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👤 فرستنده: {username} (`{user.id}`)\n"
        f"🏴 کشور: {d['war_country']}\n"
        f"📍 مبدأ: {d['war_origin']}\n"
        f"🎯 دشمن: {d['war_dest']}\n"
        f"📊 آمار: {d['war_stats']}\n"
        f"🕐 زمان: {now}"
    )

    await context.bot.send_message(CHANNEL_ID, channel_msg, parse_mode="Markdown")
    await context.bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")
    await update.message.reply_text("✅ جنگ در چنل ثبت شد!")

    keyboard = [[InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_menu")]]
    await update.message.reply_text("بازگشت به منو:", reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSE_ACTION

# ==================== بیانیه ====================
async def declare_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("📜 *بیانیه*\n\n🏴 اسم کشور خود را وارد کنید:", parse_mode="Markdown")
    return DECLARE_COUNTRY

async def declare_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["declare_country"] = update.message.text
    await update.message.reply_text("📝 متن بیانیه را بنویسید:")
    return DECLARE_TEXT

async def declare_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["declare_text"] = update.message.text
    now = datetime.now().strftime("%H:%M — %Y/%m/%d")
    d = context.user_data
    user = update.message.from_user
    username = f"@{user.username}" if user.username else user.full_name

    channel_msg = (
        f"📜 *بیانیه رسمی*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🏴 کشور: *{d['declare_country']}*\n\n"
        f"{d['declare_text']}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🕐 زمان: {now}"
    )

    admin_msg = (
        f"📋 *بیانیه جدید*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👤 فرستنده: {username} (`{user.id}`)\n"
        f"🏴 کشور: {d['declare_country']}\n"
        f"📝 متن: {d['declare_text']}\n"
        f"🕐 زمان: {now}"
    )

    await context.bot.send_message(CHANNEL_ID, channel_msg, parse_mode="Markdown")
    await context.bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")
    await update.message.reply_text("✅ بیانیه در چنل منتشر شد!")

    keyboard = [[InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_menu")]]
    await update.message.reply_text("بازگشت به منو:", reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSE_ACTION

# ==================== کمین ====================
async def ambush_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text(
        "🏹 *کمین*\n\n"
        "🔗 لینک پیام لشکرکشی دشمن را ارسال کنید:\n"
        "(مثال: https://t.me/Lio_Sep/123)",
        parse_mode="Markdown"
    )
    return AMBUSH_LINK

async def ambush_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ambush_link"] = update.message.text
    await update.message.reply_text("📊 آمار کمین (تعداد نیرو، نوع حمله و...):")
    return AMBUSH_STATS

async def ambush_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ambush_stats"] = update.message.text
    now = datetime.now().strftime("%H:%M — %Y/%m/%d")
    d = context.user_data
    user = update.message.from_user
    username = f"@{user.username}" if user.username else user.full_name

    channel_msg = (
        f"🏹 *کمین خورد!*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🔗 لشکرکشی هدف: {d['ambush_link']}\n"
        f"📊 آمار کمین: {d['ambush_stats']}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🕐 زمان: {now}"
    )

    admin_msg = (
        f"📋 *گزارش کمین*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👤 فرستنده: {username} (`{user.id}`)\n"
        f"🔗 لینک هدف: {d['ambush_link']}\n"
        f"📊 آمار: {d['ambush_stats']}\n"
        f"🕐 زمان: {now}"
    )

    await context.bot.send_message(CHANNEL_ID, channel_msg, parse_mode="Markdown")
    await context.bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")
    await update.message.reply_text("✅ کمین در چنل ثبت شد!")

    keyboard = [[InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_menu")]]
    await update.message.reply_text("بازگشت به منو:", reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSE_ACTION

# ==================== هندلر callback انتخاب ====================
async def action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data == "march":
        return await march_start(update, context)
    elif data == "war":
        return await war_start(update, context)
    elif data == "declare":
        return await declare_start(update, context)
    elif data == "ambush":
        return await ambush_start(update, context)
    elif data == "back_menu":
        return await menu(update, context)

# ==================== اجرا ====================
def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE_ACTION: [CallbackQueryHandler(action_handler)],

            # لشکرکشی
            MARCH_COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, march_country)],
            MARCH_ORIGIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, march_origin)],
            MARCH_DEST: [MessageHandler(filters.TEXT & ~filters.COMMAND, march_dest)],
            MARCH_TYPE: [CallbackQueryHandler(march_type, pattern="^mt_")],
            MARCH_STATS: [MessageHandler(filters.TEXT & ~filters.COMMAND, march_stats)],

            # جنگ
            WAR_COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, war_country)],
            WAR_ORIGIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, war_origin)],
            WAR_DEST: [MessageHandler(filters.TEXT & ~filters.COMMAND, war_dest)],
            WAR_STATS: [MessageHandler(filters.TEXT & ~filters.COMMAND, war_stats)],

            # بیانیه
            DECLARE_COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, declare_country)],
            DECLARE_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, declare_text)],

            # کمین
            AMBUSH_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, ambush_link)],
            AMBUSH_STATS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ambush_stats)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(conv_handler)
    print("✅ ربات سه پادشاهی در حال اجراست...")
    app.run_polling()

if __name__ == "__main__":
    main()
