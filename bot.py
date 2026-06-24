import logging, json, os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ConversationHandler, ContextTypes, filters

TOKEN = "8914799757:AAHG4SkCFFAhqa0POVzMYRuAlJj3p0cEVZg"
CHANNEL_ID = "@Lio_Sep"
ADMIN_ID = 7442300373
PLAYERS_FILE = "players.json"

def load_players():
    if os.path.exists(PLAYERS_FILE):
        with open(PLAYERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_players(data):
    with open(PLAYERS_FILE, "w") as f:
        json.dump(data, f)

(REGISTER, CHOOSE_ACTION, MARCH_ORIGIN_COUNTRY, MARCH_ORIGIN_CITY, MARCH_DEST_COUNTRY, MARCH_DEST_CITY, MARCH_TYPE, MARCH_TIME, MARCH_STATS, WAR_ORIGIN_COUNTRY, WAR_ORIGIN_CITY, WAR_DEST, WAR_STATS, DECLARE_TEXT, AMBUSH_COUNTRY, AMBUSH_STATS, CHANGE_DEST, CHANGE_TIME) = range(18)

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

MAIN_KB = InlineKeyboardMarkup([[InlineKeyboardButton("⚔️ لشکرکشی", callback_data="march")],[InlineKeyboardButton("🗡️ جنگ", callback_data="war")],[InlineKeyboardButton("📜 بیانیه", callback_data="declare")]])
BACK_KB = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_menu")]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    players = load_players()
    uid = str(update.message.from_user.id)
    args = context.args
    if args and args[0].startswith("ambush_"):
        msg_id = args[0].replace("ambush_", "")
        context.user_data["ambush_msg_id"] = msg_id
        if uid in players:
            p = players[uid]
            context.user_data["king"] = p["king"]
            context.user_data["country"] = p["country"]
            await update.message.reply_text("🏹 *کمین*\n\n📊 آمار کمین:", parse_mode="Markdown")
            return AMBUSH_STATS
        else:
            context.user_data["pending_ambush"] = msg_id
            await update.message.reply_text("🏰 *خوش آمدید!*\n\nلطفاً کد ورود به بازی را وارد کنید:", parse_mode="Markdown")
            return REGISTER
    if uid in players:
        p = players[uid]
        await update.message.reply_text(f"🏰 خوش آمدید!\n\nهویت شما مشخص شد\nپادشاه: *{p['king']}*\nکشور: *{p['country']}*", parse_mode="Markdown", reply_markup=MAIN_KB)
        return CHOOSE_ACTION
    await update.message.reply_text("🏰 *خوش آمدید!*\n\nلطفاً کد ورود به بازی را وارد کنید:", parse_mode="Markdown")
    return REGISTER

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    players = load_players()
    code = update.message.text.strip()
    uid = str(update.message.from_user.id)
    for pid, data in players.items():
        if data.get("code") == code and pid == "pending_" + code:
            players[uid] = {"king": data["king"], "country": data["country"], "code": code}
            del players["pending_" + code]
            save_players(players)
            context.user_data["king"] = data["king"]
            context.user_data["country"] = data["country"]
            if context.user_data.get("pending_ambush"):
                msg_id = context.user_data["pending_ambush"]
                context.user_data["ambush_msg_id"] = msg_id
                await update.message.reply_text(f"✅ هویت شما مشخص شد\nپادشاه: *{data['king']}*\nکشور: *{data['country']}*\n\n🏹 *کمین*\n\n📊 آمار کمین:", parse_mode="Markdown")
                return AMBUSH_STATS
            await update.message.reply_text(f"✅ هویت شما مشخص شد\nپادشاه: *{data['king']}*\nکشور: *{data['country']}*", parse_mode="Markdown", reply_markup=MAIN_KB)
            return CHOOSE_ACTION
    await update.message.reply_text("❌ کد نامعتبر است. دوباره امتحان کنید:")
    return REGISTER

async def addplayer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return
    args = context.args
    if len(args) < 3:
        await update.message.reply_text("فرمت: /addplayer [کد] [اسم پادشاه] [اسم کشور]")
        return
    code, king, country = args[0], args[1], args[2]
    players = load_players()
    players["pending_" + code] = {"code": code, "king": king, "country": country}
    save_players(players)
    await update.message.reply_text(f"✅ پلیر اضافه شد\nکد: `{code}`\nپادشاه: {king}\nکشور: {country}", parse_mode="Markdown")

async def action_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    data = update.callback_query.data
    uid = str(update.callback_query.from_user.id)
    players = load_players()
    if uid not in players:
        await update.callback_query.message.reply_text("ابتدا /start بزنید")
        return CHOOSE_ACTION
    p = players[uid]
    context.user_data["king"] = p["king"]
    context.user_data["country"] = p["country"]
    if data == "back_menu":
        await update.callback_query.message.reply_text("🏰 منوی اصلی:", reply_markup=MAIN_KB)
        return CHOOSE_ACTION
    elif data == "march":
        await update.callback_query.message.reply_text("⚔️ *لشکرکشی*\n\n📍 کشور مبدأ:", parse_mode="Markdown")
        return MARCH_ORIGIN_COUNTRY
    elif data == "war":
        await update.callback_query.message.reply_text("🗡️ *جنگ*\n\n📍 کشور مبدأ:", parse_mode="Markdown")
        return WAR_ORIGIN_COUNTRY
    elif data == "declare":
        await update.callback_query.message.reply_text("📜 *بیانیه*\n\n📝 متن بیانیه:", parse_mode="Markdown")
        return DECLARE_TEXT

async def march_origin_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mo_country"] = update.message.text
    await update.message.reply_text("🏙️ شهر مبدأ:")
    return MARCH_ORIGIN_CITY

async def march_origin_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mo_city"] = update.message.text
    await update.message.reply_text("🎯 کشور مقصد:")
    return MARCH_DEST_COUNTRY

async def march_dest_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["md_country"] = update.message.text
    await update.message.reply_text("🏙️ شهر مقصد:")
    return MARCH_DEST_CITY

async def march_dest_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["md_city"] = update.message.text
    await update.message.reply_text("📋 نوع لشکرکشی:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⚔️ تهاجمی", callback_data="mt_attack")],[InlineKeyboardButton("🛡️ دفاعی", callback_data="mt_defense")],[InlineKeyboardButton("🏰 تصرف", callback_data="mt_capture")],[InlineKeyboardButton("🔱 غارت", callback_data="mt_raid")]]))
    return MARCH_TYPE

async def march_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    types = {"mt_attack": "⚔️ تهاجمی", "mt_defense": "🛡️ دفاعی", "mt_capture": "🏰 تصرف", "mt_raid": "🔱 غارت"}
    context.user_data["mt"] = types[update.callback_query.data]
    await update.callback_query.message.reply_text("🕐 زمان رسیدن (مثلاً ۲۲:۳۴):")
    return MARCH_TIME

async def march_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["m_time"] = update.message.text
    await update.message.reply_text("📊 آمار لشکر (فقط برای ادمین):")
    return MARCH_STATS

async def march_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ms"] = update.message.text
    d = context.user_data
    now = datetime.now().strftime("%H:%M — %Y/%m/%d")
    user = update.message.from_user
    channel_msg = (f"⚔️ *لشکرکشی*\n━━━━━━━━━━━━━━━\n"
        f"ارتش *{d['country']}* از {d['mo_city']} ({d['mo_country']}) "
        f"به سوی {d['md_city']} ({d['md_country']}) لشکرکشید\n"
        f"📋 نوع: {d['mt']}\n🕐 زمان رسیدن: {d['m_time']}\n━━━━━━━━━━━━━━━\n🗓 {now}")
    msg = await context.bot.send_message(CHANNEL_ID, channel_msg, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏹 کمین", url=f"https://t.me/ThreeKingdomsRoyal_bot?start=ambush_{user.id}"), InlineKeyboardButton("🔙 بک", callback_data=f"back_{user.id}_{update.message.message_id}"), InlineKeyboardButton("🔀 تغییر مسیر", callback_data=f"change_{user.id}")]]))
    context.user_data["last_channel_msg_id"] = msg.message_id
    await context.bot.send_message(ADMIN_ID,
        f"📋 *گزارش لشکرکشی*\n👤 {user.full_name} (`{user.id}`)\n"
        f"🏴 {d['country']} | پادشاه: {d['king']}\n"
        f"📍 {d['mo_city']} ({d['mo_country']}) ← {d['md_city']} ({d['md_country']})\n"
        f"📋 {d['mt']}\n📊 {d['ms']}\n🕐 {d['m_time']}", parse_mode="Markdown")
    await update.message.reply_text("✅ لشکرکشی ثبت شد!", reply_markup=BACK_KB)
    return CHOOSE_ACTION

async def ambush_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = context.user_data
    now = datetime.now().strftime("%H:%M — %Y/%m/%d")
    user = update.message.from_user
    msg_id = d.get("ambush_msg_id")
    await context.bot.send_message(CHANNEL_ID,
        f"🏹 *کمین خورد!*\n━━━━━━━━━━━━━━━\n"
        f"لشکرکشی خاندان کمین خورد\n📊 توسط ارتش *{d['country']}*\n"
        f"━━━━━━━━━━━━━━━\n🗓 {now}", parse_mode="Markdown",
        reply_to_message_id=int(msg_id) if msg_id else None)
    await context.bot.send_message(ADMIN_ID,
        f"📋 *گزارش کمین*\n👤 {user.full_name} (`{user.id}`)\n"
        f"🏴 {d['country']} | پادشاه: {d['king']}\n📊 {update.message.text}\n🗓 {now}", parse_mode="Markdown")
    await update.message.reply_text("✅ کمین ثبت شد!", reply_markup=MAIN_KB)
    return CHOOSE_ACTION

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    now = datetime.now().strftime("%H:%M — %Y/%m/%d")
    msg_id = query.message.message_id
    if data.startswith("back_"):
        original = query.message.text or ""
        country = ""
        for line in original.split("\n"):
            if "ارتش" in line and "*" in line:
                parts = line.split("*")
                if len(parts) >= 2:
                    country = parts[1]
        await context.bot.send_message(CHANNEL_ID,
            f"🔙 *بازگشت*\n━━━━━━━━━━━━━━━\nلشکر *{country}* بازگشت\n🗓 {now}",
            parse_mode="Markdown", reply_to_message_id=msg_id)
        await query.edit_message_reply_markup(reply_markup=None)
    elif data.startswith("change_"):
        uid = int(data.split("_")[1])
        context.user_data["change_msg_id"] = msg_id
        context.user_data["change_original"] = query.message.text
        await context.bot.send_message(uid, "🔀 کشور مقصد جدید را وارد کنید:")

async def war_origin_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["wo_country"] = update.message.text
    await update.message.reply_text("🏙️ شهر مبدأ:")
    return WAR_ORIGIN_CITY

async def war_origin_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["wo_city"] = update.message.text
    await update.message.reply_text("🎯 کشور دشمن:")
    return WAR_DEST

async def war_dest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["wd"] = update.message.text
    await update.message.reply_text("📊 آمار جنگ (فقط برای ادمین):")
    return WAR_STATS

async def war_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ws"] = update.message.text
    d = context.user_data
    now = datetime.now().strftime("%H:%M — %Y/%m/%d")
    user = update.message.from_user
    await context.bot.send_message(CHANNEL_ID,
        f"🗡️ *جنگ*\n━━━━━━━━━━━━━━━\n"
        f"شهر {d['wo_city']} در کشور {d['wo_country']} مورد هجوم ارتش *{d['wd']}* قرار گرفت\n"
        f"━━━━━━━━━━━━━━━\n🗓 {now}", parse_mode="Markdown")
    await context.bot.send_message(ADMIN_ID,
        f"📋 *گزارش جنگ*\n👤 {user.full_name} (`{user.id}`)\n"
        f"🏴 {d['country']} | پادشاه: {d['king']}\n"
        f"📍 {d['wo_city']} ({d['wo_country']}) ← {d['wd']}\n📊 {d['ws']}", parse_mode="Markdown")
    await update.message.reply_text("✅ جنگ ثبت شد!", reply_markup=BACK_KB)
    return CHOOSE_ACTION

async def declare_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = context.user_data
    now = datetime.now().strftime("%H:%M — %Y/%m/%d")
    user = update.message.from_user
    await context.bot.send_message(CHANNEL_ID,
        f"📜 *بیانیه رسمی*\n━━━━━━━━━━━━━━━\n🏴 کشور: *{d['country']}*\n\n{update.message.text}\n━━━━━━━━━━━━━━━\n🗓 {now}", parse_mode="Markdown")
    await context.bot.send_message(ADMIN_ID,
        f"📋 *بیانیه جدید*\n👤 {user.full_name} (`{user.id}`)\n🏴 {d['country']}\n📝 {update.message.text}", parse_mode="Markdown")
    await update.message.reply_text("✅ بیانیه منتشر شد!", reply_markup=BACK_KB)
    return CHOOSE_ACTION

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("addplayer", addplayer))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(back_|change_)"))
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            REGISTER: [MessageHandler(filters.TEXT & ~filters.COMMAND, register)],
            CHOOSE_ACTION: [CallbackQueryHandler(action_router)],
            MARCH_ORIGIN_COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, march_origin_country)],
            MARCH_ORIGIN_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, march_origin_city)],
            MARCH_DEST_COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, march_dest_country)],
            MARCH_DEST_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, march_dest_city)],
            MARCH_TYPE: [CallbackQueryHandler(march_type, pattern="^mt_")],
            MARCH_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, march_time)],
            MARCH_STATS: [MessageHandler(filters.TEXT & ~filters.COMMAND, march_stats)],
            WAR_ORIGIN_COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, war_origin_country)],
            WAR_ORIGIN_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, war_origin_city)],
            WAR_DEST: [MessageHandler(filters.TEXT & ~filters.COMMAND, war_dest)],
            WAR_STATS: [MessageHandler(filters.TEXT & ~filters.COMMAND, war_stats)],
            DECLARE_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, declare_text)],
            AMBUSH_STATS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ambush_stats)],
        },
        fallbacks=[CommandHandler("start", start)],
        allow_reentry=True,
    )
    app.add_handler(conv)
    print("✅ ربات در حال اجراست...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
