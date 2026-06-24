import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ConversationHandler, ContextTypes, filters

TOKEN = "8914799757:AAHG4SkCFFAhqa0POVzMYRuAlJj3p0cEVZg"
CHANNEL_ID = "@Lio_Sep"
ADMIN_ID = 7442300373

(CHOOSE_ACTION, MARCH_COUNTRY, MARCH_ORIGIN, MARCH_DEST, MARCH_TYPE, MARCH_STATS, WAR_COUNTRY, WAR_ORIGIN, WAR_DEST, WAR_STATS, DECLARE_COUNTRY, DECLARE_TEXT, AMBUSH_LINK, AMBUSH_STATS) = range(14)

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

MAIN_KB = InlineKeyboardMarkup([[InlineKeyboardButton("⚔️ لشکرکشی", callback_data="march")],[InlineKeyboardButton("🗡️ جنگ", callback_data="war")],[InlineKeyboardButton("📜 بیانیه", callback_data="declare")],[InlineKeyboardButton("🏹 کمین", callback_data="ambush")]])
BACK_KB = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_menu")]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏰 *به ربات سه پادشاهی خوش آمدید*\n\nعملیات را انتخاب کنید:", reply_markup=MAIN_KB, parse_mode="Markdown")
    return CHOOSE_ACTION

async def action_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    data = update.callback_query.data
    if data == "back_menu":
        await update.callback_query.message.reply_text("🏰 *منوی اصلی*\n\nعملیات را انتخاب کنید:", reply_markup=MAIN_KB, parse_mode="Markdown")
        return CHOOSE_ACTION
    elif data == "march":
        await update.callback_query.message.reply_text("⚔️ *لشکرکشی*\n\n🏴 اسم کشور:", parse_mode="Markdown")
        return MARCH_COUNTRY
    elif data == "war":
        await update.callback_query.message.reply_text("🗡️ *جنگ*\n\n🏴 اسم کشور:", parse_mode="Markdown")
        return WAR_COUNTRY
    elif data == "declare":
        await update.callback_query.message.reply_text("📜 *بیانیه*\n\n🏴 اسم کشور:", parse_mode="Markdown")
        return DECLARE_COUNTRY
    elif data == "ambush":
        await update.callback_query.message.reply_text("🏹 *کمین*\n\n🔗 لینک لشکرکشی دشمن:", parse_mode="Markdown")
        return AMBUSH_LINK

async def march_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mc"] = update.message.text
    await update.message.reply_text("📍 مبدأ:")
    return MARCH_ORIGIN

async def march_origin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mo"] = update.message.text
    await update.message.reply_text("🎯 مقصد:")
    return MARCH_DEST

async def march_dest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["md"] = update.message.text
    await update.message.reply_text("📋 نوع لشکرکشی:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⚔️ تهاجمی", callback_data="mt_attack")],[InlineKeyboardButton("🛡️ دفاعی", callback_data="mt_defense")],[InlineKeyboardButton("🏰 تصرف", callback_data="mt_capture")],[InlineKeyboardButton("🔱 غارت", callback_data="mt_raid")]]))
    return MARCH_TYPE

async def march_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    types = {"mt_attack": "⚔️ تهاجمی", "mt_defense": "🛡️ دفاعی", "mt_capture": "🏰 تصرف", "mt_raid": "🔱 غارت"}
    context.user_data["mt"] = types[update.callback_query.data]
    await update.callback_query.message.reply_text("📊 آمار لشکر:")
    return MARCH_STATS

async def march_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ms"] = update.message.text
    now = datetime.now().strftime("%H:%M — %Y/%m/%d")
    d = context.user_data
    user = update.message.from_user
    uname = f"@{user.username}" if user.username else user.full_name
    await context.bot.send_message(CHANNEL_ID, f"⚔️ *لشکرکشی*\n━━━━━━━━━━━━━━━\n🏴 کشور: *{d['mc']}*\n📍 مبدأ: *{d['mo']}*\n🎯 مقصد: *{d['md']}*\n📋 نوع: *{d['mt']}*\n📊 آمار: {d['ms']}\n━━━━━━━━━━━━━━━\n🕐 زمان: {now}", parse_mode="Markdown")
    await context.bot.send_message(ADMIN_ID, f"📋 *گزارش لشکرکشی*\n👤 {uname} (`{user.id}`)\n🏴 {d['mc']}\n📍 {d['mo']}\n🎯 {d['md']}\n📋 {d['mt']}\n📊 {d['ms']}\n🕐 {now}", parse_mode="Markdown")
    await update.message.reply_text("✅ ثبت شد!", reply_markup=BACK_KB)
    return CHOOSE_ACTION

async def war_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["wc"] = update.message.text
    await update.message.reply_text("📍 مبدأ:")
    return WAR_ORIGIN

async def war_origin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["wo"] = update.message.text
    await update.message.reply_text("🎯 مقصد (کشور دشمن):")
    return WAR_DEST

async def war_dest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["wd"] = update.message.text
    await update.message.reply_text("📊 آمار جنگ:")
    return WAR_STATS

async def war_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ws"] = update.message.text
    now = datetime.now().strftime("%H:%M — %Y/%m/%d")
    d = context.user_data
    user = update.message.from_user
    uname = f"@{user.username}" if user.username else user.full_name
    await context.bot.send_message(CHANNEL_ID, f"🗡️ *جنگ*\n━━━━━━━━━━━━━━━\n🏴 کشور: *{d['wc']}*\n📍 مبدأ: *{d['wo']}*\n🎯 دشمن: *{d['wd']}*\n📊 آمار: {d['ws']}\n━━━━━━━━━━━━━━━\n🕐 زمان: {now}", parse_mode="Markdown")
    await context.bot.send_message(ADMIN_ID, f"📋 *گزارش جنگ*\n👤 {uname} (`{user.id}`)\n🏴 {d['wc']}\n📍 {d['wo']}\n🎯 {d['wd']}\n📊 {d['ws']}\n🕐 {now}", parse_mode="Markdown")
    await update.message.reply_text("✅ ثبت شد!", reply_markup=BACK_KB)
    return CHOOSE_ACTION

async def declare_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["dc"] = update.message.text
    await update.message.reply_text("📝 متن بیانیه:")
    return DECLARE_TEXT

async def declare_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["dt"] = update.message.text
    now = datetime.now().strftime("%H:%M — %Y/%m/%d")
    d = context.user_data
    user = update.message.from_user
    uname = f"@{user.username}" if user.username else user.full_name
    await context.bot.send_message(CHANNEL_ID, f"📜 *بیانیه رسمی*\n━━━━━━━━━━━━━━━\n🏴 کشور: *{d['dc']}*\n\n{d['dt']}\n━━━━━━━━━━━━━━━\n🕐 زمان: {now}", parse_mode="Markdown")
    await context.bot.send_message(ADMIN_ID, f"📋 *بیانیه جدید*\n👤 {uname} (`{user.id}`)\n🏴 {d['dc']}\n📝 {d['dt']}\n🕐 {now}", parse_mode="Markdown")
    await update.message.reply_text("✅ منتشر شد!", reply_markup=BACK_KB)
    return CHOOSE_ACTION

async def ambush_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["al"] = update.message.text
    await update.message.reply_text("📊 آمار کمین:")
    return AMBUSH_STATS

async def ambush_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["as_"] = update.message.text
    now = datetime.now().strftime("%H:%M — %Y/%m/%d")
    d = context.user_data
    user = update.message.from_user
    uname = f"@{user.username}" if user.username else user.full_name
    await context.bot.send_message(CHANNEL_ID, f"🏹 *کمین خورد!*\n━━━━━━━━━━━━━━━\n🔗 هدف: {d['al']}\n📊 آمار: {d['as_']}\n━━━━━━━━━━━━━━━\n🕐 زمان: {now}", parse_mode="Markdown")
    await context.bot.send_message(ADMIN_ID, f"📋 *گزارش کمین*\n👤 {uname} (`{user.id}`)\n🔗 {d['al']}\n📊 {d['as_']}\n🕐 {now}", parse_mode="Markdown")
    await update.message.reply_text("✅ ثبت شد!", reply_markup=BACK_KB)
    return CHOOSE_ACTION

def main():
    app = Application.builder().token(TOKEN).build()
    conv = ConversationHandler(entry_points=[CommandHandler("start", start)],states={CHOOSE_ACTION: [CallbackQueryHandler(action_router)],MARCH_COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, march_country)],MARCH_ORIGIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, march_origin)],MARCH_DEST: [MessageHandler(filters.TEXT & ~filters.COMMAND, march_dest)],MARCH_TYPE: [CallbackQueryHandler(march_type, pattern="^mt_")],MARCH_STATS: [MessageHandler(filters.TEXT & ~filters.COMMAND, march_stats)],WAR_COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, war_country)],WAR_ORIGIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, war_origin)],WAR_DEST: [MessageHandler(filters.TEXT & ~filters.COMMAND, war_dest)],WAR_STATS: [MessageHandler(filters.TEXT & ~filters.COMMAND, war_stats)],DECLARE_COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, declare_country)],DECLARE_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, declare_text)],AMBUSH_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, ambush_link)],AMBUSH_STATS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ambush_stats)]},fallbacks=[CommandHandler("start", start)],allow_reentry=True)
    app.add_handler(conv)
    print("✅ ربات در حال اجراست...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
