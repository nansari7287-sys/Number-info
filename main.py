import telebot
import json
import os
import requests
import time
import logging
import threading
import random
import re
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from flask import Flask

# ==========================================
# ⚙️ SYSTEM CONFIGURATION
# ==========================================

TOKEN = '8789692969:AAFE7m4pXvJ501TgUhzBg95d4e9OwvQYPrg' 
OWNER_ID = 8448533037

REQ_CHANNEL = "@frexyy_Era"
REQ_GROUP_1 = "@frexyyEra"

CHANNEL_LINK = "https://t.me/frexyy_Era"
GROUP_1_LINK = "https://t.me/frexyyEra"

SYSTEM_NAME = "@frexxxy"

# 📂 DATABASE FILES
DATA_FILE = "users_db.json"
CONFIG_FILE = "config.json"
GROUPS_FILE = "groups_db.json"   
ADS_FILE = "active_ads_db.json"  

# 🚨 DEFAULT API LINKS (Dynamic Setup) 🚨
DEFAULT_APIS = {
    "aadhaar": "https://num-info-paid.vercel.app/?num={}&key=ERROR",
    "vehicle": "https://vehicleinfobyterabaap.vercel.app/lookup?rc={}",
    "pak": "https://pkmkb.free.nf/api.php?number={}",
    "ifsc": "https://ifsc.razorpay.com/{}",
    "bin": "https://data.handyapi.com/bin/{}",
    "num": "https://database-sigma-nine.vercel.app/number/{}?api_key=YOUR-PASSWORD",
    "family": "https://number8899.vercel.app/?type=family&aadhar={}",
    "v2num": "https://your-v2num-api.com/api?num={}",
    "tg": "https://username-to-number.vercel.app/?key=my_dayne&q={}",
    "insta": "https://insta-profile-info-api.vercel.app/api/instagram.php?username={}",
    "gmail": "YOUR_GMAIL_API_HERE_{}" # Tum isko command se change kar lena
}

# ==========================================
# 🌐 FLASK SERVER
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return f"{SYSTEM_NAME} Bot is Running 24/7 on Render/Termux!"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ==========================================
# 🛠️ ADVANCED NETWORK ENGINE
# ==========================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(SYSTEM_NAME)

session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

def get_random_headers():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    return {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/json,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive'
    }

try:
    bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")
except Exception as e:
    print(f"❌ Critical Token Error: {e}")
    exit()

def set_bot_commands():
    commands = [
        telebot.types.BotCommand("start", "Premium Start Menu"),
        telebot.types.BotCommand("num", "Number Info"),
        telebot.types.BotCommand("family", "Family Info"),
        telebot.types.BotCommand("tg", "Telegram Info"),
        telebot.types.BotCommand("insta", "Instagram Info"),
        telebot.types.BotCommand("gmail", "Gmail Info"),
        telebot.types.BotCommand("chat", "Get Chat ID (Reply/Forward)"),
        telebot.types.BotCommand("vehicle", "Vehicle Info"),
        telebot.types.BotCommand("aadhaar", "Aadhaar Info"),
        telebot.types.BotCommand("pak", "Pak Info"),
        telebot.types.BotCommand("v2num", "V2 Number Info"),
        telebot.types.BotCommand("ifsc", "IFSC Info"),
        telebot.types.BotCommand("bin", "BIN Info")
    ]
    bot.set_my_commands(commands)

# ==========================================
# 💾 DATABASE & API MANAGEMENT
# ==========================================
def load_json_file(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_json_file(data, filename):
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
    except: pass

def get_user_data(user_id):
    db = load_json_file(DATA_FILE)
    str_id = str(user_id)
    if str_id not in db:
        db[str_id] = {"joined_date": datetime.now().strftime("%Y-%m-%d"), "rank": "User"}
        save_json_file(db, DATA_FILE)
    return db, str_id

def get_api(api_name):
    config = load_json_file(CONFIG_FILE)
    if "apis" not in config:
        config["apis"] = DEFAULT_APIS
        save_json_file(config, CONFIG_FILE)
    return config["apis"].get(api_name, DEFAULT_APIS.get(api_name, ""))

def update_api(api_name, new_url):
    config = load_json_file(CONFIG_FILE)
    if "apis" not in config:
        config["apis"] = DEFAULT_APIS
    config["apis"][api_name] = new_url
    save_json_file(config, CONFIG_FILE)

def track_group(chat_id):
    if str(chat_id).startswith('-'):
        db = load_json_file(GROUPS_FILE)
        if str(chat_id) not in db:
            db[str(chat_id)] = True
            save_json_file(db, GROUPS_FILE)

# ==========================================
# 🔒 SECURITY, MEMBERSHIP & FILTERS
# ==========================================
def check_membership(user_id):
    try:
        c1 = bot.get_chat_member(REQ_CHANNEL, user_id)
        g1 = bot.get_chat_member(REQ_GROUP_1, user_id)
        valid = ['creator', 'administrator', 'member']
        if c1.status in valid and g1.status in valid:
            return True
        return False
    except Exception as e:
        return False

def is_allowed_chat(chat):
    return True

# 🗑️ MULTI AUTO DELETE 
def schedule_delete_multi(chat_id, message_ids_list, delay=15):
    def delete_task():
        time.sleep(delay)
        for msg_id in message_ids_list:
            if msg_id:
                try: bot.delete_message(chat_id, msg_id)
                except: pass
    threading.Thread(target=delete_task).start()

def send_force_join(chat_id, message_id):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK))
    markup.add(telebot.types.InlineKeyboardButton("👥 Join Group", url=GROUP_1_LINK))
    markup.add(telebot.types.InlineKeyboardButton("✅ Verify", callback_data="check_subscription"))
    msg = "🛑 **ACCESS DENIED** 🛑\n\nCommands use karne ke liye hamare Channel aur Group join karo."
    sent_msg = bot.send_message(chat_id, msg, reply_markup=markup, reply_to_message_id=message_id)
    schedule_delete_multi(chat_id, [sent_msg.message_id, message_id], delay=30)

def send_welcome_menu(chat_id, user, user_msg_id=None):
    get_user_data(user.id)
    name = user.first_name
    
    id_card = (
        f"💎 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐈𝐍𝐅𝐎 𝐆𝐀𝐓𝐄𝐖𝐀𝐘 💎\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 𝐔𝐬𝐞𝐫 : `{name}`\n"
        f"🆔 𝐈𝐃   : `{user.id}`\n"
        f"🎖️ 𝐑𝐚𝐧𝐤 : `VIP Member`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⚙️ 𝐌𝐀𝐈𝐍 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒:\n"
        f"├ 📱 `/num` `[Number]` ➾ Get Number Details\n"
        f"├ 👨‍👩‍👧 `/family` `[Aadhar]` ➾ Get Family Details\n"
        f"├ ✈️ `/tg` `[@Username]` ➾ Get Telegram Info\n"
        f"├ 📸 `/insta` `[Username]` ➾ Get Instagram Info\n" # NAYA ADD HUA
        f"├ 📧 `/gmail` `[Email]` ➾ Get Gmail Info\n"         # NAYA ADD HUA
        f"├ 💬 `/chat` ➾ Get ID (Reply/Forward/Username)\n"
        f"├ 🚙 `/vehicle` `[RC]` ➾ Get Vehicle Info\n"
        f"├ 💳 `/aadhaar` `[UID]` ➾ Get Aadhaar Info\n"
        f"├ 🇵🇰 `/pak` `[Number]` ➾ Pak Number Info\n"
        f"├ 🏦 `/ifsc` `[IFSC]` ➾ Bank Details\n"
        f"├ 💳 `/bin` `[BIN]` ➾ Card Details\n"
        f"└ ♻️ `/v2num` `[Number]` ➾ V2 DB Search\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ 𝐏𝐨𝐰𝐞𝐫𝐞𝐝 𝐁𝐲 : {SYSTEM_NAME}"
    )
    sent_msg = bot.send_message(chat_id, id_card, parse_mode="Markdown")
    schedule_delete_multi(chat_id, [sent_msg.message_id, user_msg_id], delay=30)

@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
def check_sub_callback(call):
    if check_membership(call.from_user.id):
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        bot.answer_callback_query(call.id, "✅ Verified!", show_alert=True)
        veri_msg = bot.send_message(call.message.chat.id, "✅ **Verification Successful!**")
        schedule_delete_multi(call.message.chat.id, [veri_msg.message_id], delay=10)
        send_welcome_menu(call.message.chat.id, call.from_user)
    else:
        bot.answer_callback_query(call.id, "❌ Channel aur Group Join Karo Pehle!", show_alert=True)

def loading_effect(chat_id, message_id):
    bars = [
        "▒▒▒▒▒▒▒▒▒▒ 0% [CONNECTING]",
        "███▒▒▒▒▒▒▒ 25% [CHECKING DB]",
        "██████▒▒▒▒ 50% [GETTING INFO]",
        "█████████▒ 80% [PROCESSING]",
        "██████████ 100% [COMPLETED]"
    ]
    for bar in bars:
        try:
            bot.edit_message_text(f"```ini\n{bar}\n```", chat_id, message_id, parse_mode="Markdown")
            time.sleep(0.4) 
        except: pass

# ==========================================
# 🛠️ UNIVERSAL AUTO-FLATTENER & FORMATTER
# ==========================================
def extract_pure_json(text):
    try:
        match = re.search(r'(\[.*?\]|\{.*\})', text, re.DOTALL)
        if match: return json.loads(match.group(1))
    except: pass
    return None

def format_professional_data(data):
    if isinstance(data, dict):
        if "FULL_DETAILS" in data and isinstance(data["FULL_DETAILS"], dict):
            api1 = data["FULL_DETAILS"].get("api_1", {})
            if "result" in api1 and isinstance(api1["result"], list):
                data = api1["result"]
        elif "data" in data and isinstance(data["data"], (list, dict)):
            data = data["data"]
        elif "result" in data and isinstance(data["result"], (list, dict)):
            data = data["result"]

    ordered_keys = [
        "name", "username", "membername", "fname", "fathername", "mobile", "phone", 
        "alt", "circle", "state", "email", "id", "rcid", "uid", 
        "ration_card_no", "address", "relationship_name", "followers", "following", "bio"
    ]
    
    def flatten(item, depth=0):
        res = ""
        space = "  " * depth
        if isinstance(item, dict):
            for key in ordered_keys:
                actual_key = next((k for k in item.keys() if str(k).lower() == key), None)
                if actual_key and item[actual_key] not in [None, "", []]:
                    res += f"{space}{str(actual_key).upper().ljust(15)} : {item[actual_key]}\n"
            for k, v in item.items():
                key_lower = str(k).lower()
                if key_lower in ordered_keys or key_lower in ['status', 'count', 'search time', 'success', 'error', 'developer', 'message', 'api_key', 'cached']:
                    continue
                if isinstance(v, (dict, list)) and len(v) > 0:
                    res += f"\n{space}▼ {str(k).upper()} ▼\n{flatten(v, depth + 1)}"
                elif v not in [None, "", []]:
                    res += f"{space}{str(k).upper().ljust(15)} : {v}\n"
        elif isinstance(item, list):
            for i, val in enumerate(item, 1):
                res += f"\n{space}--- [ RECORD {i} ] ---\n{flatten(val, depth)}"
        else:
            res += f"{space}{item}\n"
        return res

    out = flatten(data)
    out = re.sub(r'\n\s*\n', '\n\n', out) 
    return out.strip()

# ==========================================
# 📢 VIP ADS BROADCAST ENGINE
# ==========================================
@bot.message_handler(commands=['ads'])
def cmd_ads_start(message):
    track_group(message.chat.id)
    if message.from_user.id != OWNER_ID: return
    msg = bot.reply_to(message, "📢 **VIP AD BROADCAST SYSTEM**\n\n📝 Kripya apna Ad message bhejiye jo aap sabhi groups me chalana chahte hain.\n*(Aap links aur formatting use kar sakte hain)*")
    bot.register_next_step_handler(msg, process_ad_broadcast)

def process_ad_broadcast(message):
    ad_text = message.text
    groups = load_json_file(GROUPS_FILE)
    if not groups:
        return bot.reply_to(message, "❌ Abhi tak bot kisi group me save nahi hua hai. Pehle bot ko groups me add karo.")

    broadcast_id = str(int(time.time()))
    status_msg = bot.reply_to(message, "🚀 **Broadcasting Ads... Please wait.**")
    
    success_count = 0
    sent_messages = {} 
    for gid in groups.keys():
        try:
            sent = bot.send_message(gid, ad_text, parse_mode="Markdown", disable_web_page_preview=True)
            sent_messages[gid] = sent.message_id
            success_count += 1
            time.sleep(0.3)
        except Exception: pass
            
    active_ads = load_json_file(ADS_FILE)
    active_ads[broadcast_id] = sent_messages
    save_json_file(active_ads, ADS_FILE)
    
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn_del = telebot.types.InlineKeyboardButton("🗑 Force Delete Now", callback_data=f"adact_del_{broadcast_id}")
    btn_5m = telebot.types.InlineKeyboardButton("⏳ 5 Min", callback_data=f"adact_time_{broadcast_id}_300")
    btn_30m = telebot.types.InlineKeyboardButton("⏳ 30 Min", callback_data=f"adact_time_{broadcast_id}_1800")
    btn_1h = telebot.types.InlineKeyboardButton("⏳ 1 Hour", callback_data=f"adact_time_{broadcast_id}_3600")
    markup.add(btn_5m, btn_30m, btn_1h)
    markup.add(btn_del)
    
    panel_text = f"✅ **Broadcast Complete!**\n\n📊 **Stats:** Successfully sent to `{success_count}` groups.\n\n⚙️ **Control Panel:** Niche diye gaye buttons se Ad ka Timer set karein ya Delete karein:"
    bot.edit_message_text(panel_text, chat_id=message.chat.id, message_id=status_msg.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('adact_'))
def ad_control_callback(call):
    if call.from_user.id != OWNER_ID:
        return bot.answer_callback_query(call.id, "Access Denied!", show_alert=True)
        
    data = call.data.split('_')
    action = data[1]
    b_id = data[2]
    
    active_ads = load_json_file(ADS_FILE)
    if b_id not in active_ads:
        return bot.answer_callback_query(call.id, "Ad already deleted or expired!", show_alert=True)
        
    if action == "del":
        bot.answer_callback_query(call.id, "Deleting ads from all groups...")
        delete_broadcast(b_id, active_ads)
        bot.edit_message_text(f"🗑 **Ads Deleted!**\nYe ad sabhi groups se hamesha ke liye hata di gayi hai.", call.message.chat.id, call.message.message_id)
        
    elif action == "time":
        seconds = int(data[3])
        mins = seconds // 60
        bot.answer_callback_query(call.id, f"Timer set for {mins} minutes.")
        
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("🗑 Force Delete Now", callback_data=f"adact_del_{b_id}"))
        bot.edit_message_text(f"⏳ **Timer Active!**\nYe ad `{mins} minutes` me sabhi groups se auto-delete ho jayegi.\n\n(Agar abhi delete karna hai to niche click karein)", call.message.chat.id, call.message.message_id, reply_markup=markup)
        threading.Thread(target=scheduled_ad_delete, args=(b_id, seconds, call.message.chat.id, call.message.message_id)).start()

def delete_broadcast(b_id, active_ads_db):
    targets = active_ads_db.get(b_id, {})
    for gid, mid in targets.items():
        try: bot.delete_message(gid, mid)
        except: pass
    if b_id in active_ads_db:
        del active_ads_db[b_id]
        save_json_file(active_ads_db, ADS_FILE)

def scheduled_ad_delete(b_id, delay, chat_id, msg_id):
    time.sleep(delay)
    active_ads = load_json_file(ADS_FILE)
    if b_id in active_ads:
        delete_broadcast(b_id, active_ads)
        try: bot.edit_message_text(f"⏳ **Timer Finished!**\nAd automatically sabhi groups se delete ho chuki hai.", chat_id, msg_id)
        except: pass

# ==========================================
# 🚀 START COMMAND
# ==========================================
@bot.message_handler(commands=['start'])
def start(message):
    track_group(message.chat.id)
    if not is_allowed_chat(message.chat): return
    user_id = message.from_user.id
    if not check_membership(user_id):
        send_force_join(message.chat.id, message.message_id)
        return
    send_welcome_menu(message.chat.id, message.from_user, message.message_id)

# ==========================================
# 👑 OWNER API MANAGEMENT COMMANDS
# ==========================================
@bot.message_handler(commands=['numapi', 'familyapi', 'tgapi', 'v2numapi', 'vehicleapi', 'pakapi', 'aadhaarapi', 'ifscapi', 'binapi', 'instaapi', 'gmailapi'])
def cmd_set_api(message):
    track_group(message.chat.id)
    if message.from_user.id != OWNER_ID:
        err = bot.reply_to(message, "❌ **ACCESS DENIED:** You are not the Owner!")
        schedule_delete_multi(message.chat.id, [err.message_id, message.message_id], delay=10)
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        err = bot.reply_to(message, "⚠️ **FORMAT:** `/command <API_LINK>`\n*Note:* API Link me `{}` lagana mat bhulna!")
        schedule_delete_multi(message.chat.id, [err.message_id, message.message_id], delay=15)
        return

    new_api = args[1].strip()
    if "{}" not in new_api:
        err = bot.reply_to(message, "⚠️ **ERROR:** Link me `{}` nahi hai! Bot ko kaise pata chalega ID kahan lagani hai?")
        schedule_delete_multi(message.chat.id, [err.message_id, message.message_id], delay=15)
        return

    raw_cmd = args[0].replace('/', '').replace('api', '')
    api_key = raw_cmd # Direct map kyunki commands same set kar diye hain

    current_api = get_api(api_key)
    
    # Same API Check
    if new_api == current_api:
        err = bot.reply_to(message, f"⚠️ **Same API:** Bhai, ye API pehle se hi set hai! Koi nayi API daalo.\n`{new_api}`")
        schedule_delete_multi(message.chat.id, [err.message_id, message.message_id], delay=15)
        return

    update_api(api_key, new_api)
    success_msg = bot.reply_to(message, f"✅ **{api_key.upper()} API Updated Successfully!**\n\nNaya Link: `{new_api}`")
    schedule_delete_multi(message.chat.id, [success_msg.message_id, message.message_id], delay=15)

# ==========================================
# 🕵️ CHAT ID EXTRACTOR 
# ==========================================
@bot.message_handler(commands=['chat', 'id'])
def cmd_chat_id(message):
    track_group(message.chat.id)
    if not is_allowed_chat(message.chat): return
    
    user_id = message.from_user.id
    if not check_membership(user_id):
        return send_force_join(message.chat.id, message.message_id)

    if message.reply_to_message:
        target = message.reply_to_message.from_user
        name = target.first_name
        username = f"@{target.username}" if target.username else "Private"
        
        res_text = (
            f"🎯 **TARGET INFO EXTRACTED**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **Name:** `{name}`\n"
            f"🔗 **Username:** `{username}`\n"
            f"🆔 **User ID:** `{target.id}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f" 💎 **@frexxxy** 💎\n"
        )
        msg = bot.reply_to(message, res_text, parse_mode="Markdown")
        return schedule_delete_multi(message.chat.id, [msg.message_id, message.message_id], delay=15)

    args = message.text.split()
    if len(args) < 2:
        err = bot.reply_to(message, "⚠️ **Usage:** `/chat @username`\n💡 *Tip: Kisi aam user ki ID chahiye toh uske message par reply karke `/chat` likho!*")
        return schedule_delete_multi(message.chat.id, [err.message_id, message.message_id], delay=10)
    
    target_username = args[1].strip()
    if not target_username.startswith('@'): target_username = '@' + target_username

    status_msg = bot.reply_to(message, f"```ini\n[ EXTRACTING CHAT ID... ]\n```", parse_mode="Markdown")
    loading_effect(message.chat.id, status_msg.message_id)

    try:
        chat_info = bot.get_chat(target_username)
        name = chat_info.first_name if chat_info.first_name else chat_info.title
        c_type = str(chat_info.type).capitalize()
        username = f"@{chat_info.username}" if chat_info.username else "Private"
        
        res_text = (
            f"🎯 **TARGET INFO EXTRACTED**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **Name:** `{name}`\n"
            f"🔗 **Username:** `{username}`\n"
            f"🆔 **Chat ID:** `{chat_info.id}`\n"
            f"🏷️ **Type:** `{c_type}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"   ⚡️ **𝐏𝐨𝐰𝐞𝐫𝐞𝐝 𝐁𝐲** ⚡️\n"
            f" 💎 **@frexxxy** 💎\n"
        )
        bot.edit_message_text(res_text, message.chat.id, status_msg.message_id, parse_mode="Markdown")
        schedule_delete_multi(message.chat.id, [status_msg.message_id, message.message_id], delay=15)
    except Exception:
        bot.edit_message_text("❌ **Error:** Telegram aam users ka search block karta hai. Kisi *insan* ki ID ke liye uske message ka reply karke `/chat` likho!", message.chat.id, status_msg.message_id)
        schedule_delete_multi(message.chat.id, [status_msg.message_id, message.message_id], delay=15)

@bot.message_handler(func=lambda message: message.forward_from or message.forward_from_chat)
def handle_forward(message):
    track_group(message.chat.id)
    if not is_allowed_chat(message.chat): return
    if not check_membership(message.from_user.id): return
    
    status_msg = bot.reply_to(message, f"```ini\n[ SCANNING FORWARDED DATA... ]\n```", parse_mode="Markdown")
    loading_effect(message.chat.id, status_msg.message_id)

    if message.forward_from:
        target = message.forward_from
        name = target.first_name
        username = f"@{target.username}" if target.username else "Private"
        t_type = "User"
        t_id = target.id
    elif message.forward_from_chat:
        target = message.forward_from_chat
        name = target.title
        username = f"@{target.username}" if target.username else "Private"
        t_type = str(target.type).capitalize()
        t_id = target.id
        
    res_text = (
        f"🎯 **FORWARDED TARGET EXTRACTED**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **Name:** `{name}`\n"
        f"🔗 **Username:** `{username}`\n"
        f"🆔 **ID:** `{t_id}`\n"
        f"🏷️ **Type:** `{t_type}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f" 💎 **@frexxxy** 💎\n"
    )
    bot.edit_message_text(res_text, message.chat.id, status_msg.message_id, parse_mode="Markdown")
    schedule_delete_multi(message.chat.id, [status_msg.message_id, message.message_id], delay=15)

# ==========================================
# 🛠️ UNIVERSAL API ENGINE
# ==========================================
def handle_api(message, api_key, command_name):
    track_group(message.chat.id)
    if not is_allowed_chat(message.chat): return
    
    user_id = message.from_user.id
    if not check_membership(user_id):
        send_force_join(message.chat.id, message.message_id)
        return

    args = message.text.split()
    if len(args) < 2:
        err = bot.reply_to(message, f"⚠️ **Usage:** `/{command_name.lower()} <ID>`")
        schedule_delete_multi(message.chat.id, [err.message_id, message.message_id], delay=10)
        return
    
    input_id = args[1].strip()
    api_url = get_api(api_key)
    
    if "YOUR-PASSWORD" in api_url or "ERROR" in api_url or "YOUR_GMAIL" in api_url or not api_url:
        err = bot.reply_to(message, f"⚠️ **API NOT SET:** Bhai, `{command_name}` ki API abhi set nahi hai ya expired hai!")
        schedule_delete_multi(message.chat.id, [err.message_id, message.message_id], delay=15)
        return
    
    status_msg = bot.reply_to(message, f"```ini\n[ SEARCHING {command_name.upper()}... ]\n```", parse_mode="Markdown")
    loading_effect(message.chat.id, status_msg.message_id)

    try:
        full_url = api_url.format(input_id)
        response = session.get(full_url, headers=get_random_headers(), timeout=30)
        
        if response.status_code == 200:
            data = None
            try:
                raw_json = response.json()
                if "raw_text" in raw_json:
                    extracted = extract_pure_json(raw_json["raw_text"])
                    if extracted: data = extracted
                else: data = raw_json
            except json.JSONDecodeError:
                extracted = extract_pure_json(response.text)
                if extracted: data = extracted
                else: data = {"Result": "Data found but format is unknown", "Raw": response.text[:500]}

            if isinstance(data, dict):
                bad_keys = ["developer", "system", "server", "credit", "owner", "powered_by", "auth", "api_owner"]
                keys_to_delete = [k for k in data.keys() if k.lower() in bad_keys]
                for k in keys_to_delete: del data[k]

            has_valid_data = True
            if not data:
                has_valid_data = False
            elif isinstance(data, dict):
                if data.get("status") == "failed" or data.get("success") is False:
                    if not data.get("data") and not data.get("results"): has_valid_data = False
                if len(data) <= 2:
                    check_str = str(data).lower()
                    if "no data" in check_str or "not found" in check_str or "invalid" in check_str: has_valid_data = False
            elif isinstance(data, str) and ("no data" in data.lower() or "not found" in data.lower()):
                has_valid_data = False

            if not has_valid_data:
                no_data_msg = (
                    f"🚫 **NO DATA FOUND**\n"
                    f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
                    f"🔍 **Input:** `{input_id}`\n"
                    f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
                )
                bot.edit_message_text(no_data_msg, message.chat.id, status_msg.message_id)
                schedule_delete_multi(message.chat.id, [status_msg.message_id, message.message_id], delay=15)
                return

            formatted_text = format_professional_data(data)
            
            if len(formatted_text) > 3800:
                formatted_text = formatted_text[:3800] + "\n\n... [DATA TRUNCATED DUE TO TELEGRAM LIMITS]"

            result_msg = (
                f"**🗂️ {command_name.upper()} INFORMATION**\n\n"
                f"```yaml\n"
                f"{formatted_text}\n"
                f"```\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"   ⚡️ **𝐏𝐨𝐰𝐞𝐫𝐞𝐝 𝐁𝐲** ⚡️\n"
                f" 💎 **@frexxxy** 💎\n"
                f"━━━━━━━━━━━━━━━━━━━━━━"
            )
            
            bot.edit_message_text(result_msg, message.chat.id, status_msg.message_id, parse_mode="Markdown")
            schedule_delete_multi(message.chat.id, [status_msg.message_id, message.message_id], delay=15)

        else:
            bot.edit_message_text(f"❌ API Error: Server returned {response.status_code}", message.chat.id, status_msg.message_id)
            schedule_delete_multi(message.chat.id, [status_msg.message_id, message.message_id], delay=15)

    except requests.exceptions.Timeout:
        bot.edit_message_text("⚠️ **Timeout:** Server took too long to respond.", message.chat.id, status_msg.message_id)
        schedule_delete_multi(message.chat.id, [status_msg.message_id, message.message_id], delay=15)
    except Exception as e:
        bot.edit_message_text("⚠️ **Connection Error or No Data Found**", message.chat.id, status_msg.message_id)
        schedule_delete_multi(message.chat.id, [status_msg.message_id, message.message_id], delay=15)

# ==========================================
# 🎮 COMMAND HANDLERS
# ==========================================
@bot.message_handler(commands=['aadhaar', 'uid'])
def cmd_aadhaar(m): handle_api(m, "aadhaar", "Aadhaar")

@bot.message_handler(commands=['pak'])
def cmd_pak(m): handle_api(m, "pak", "Pak")

@bot.message_handler(commands=['vehicle'])
def cmd_vehicle(m): handle_api(m, "vehicle", "Vehicle")

@bot.message_handler(commands=['num'])
def cmd_num(m): handle_api(m, "num", "Number")

@bot.message_handler(commands=['v2num'])
def cmd_v2num(m): handle_api(m, "v2num", "V2 Number")

@bot.message_handler(commands=['family'])
def cmd_family(m): handle_api(m, "family", "Family")

@bot.message_handler(commands=['tg', 'telegram'])
def cmd_tg(m): handle_api(m, "tg", "Telegram")

@bot.message_handler(commands=['insta', 'instagram'])
def cmd_insta(m): handle_api(m, "insta", "Instagram")

@bot.message_handler(commands=['gmail', 'email'])
def cmd_gmail(m): handle_api(m, "gmail", "Gmail")

@bot.message_handler(commands=['ifsc'])
def cmd_ifsc(m): handle_api(m, "ifsc", "IFSC")

@bot.message_handler(commands=['bin'])
def cmd_bin(m): handle_api(m, "bin", "BIN")

# 🔥 GROUP TRACKER (Catches any text to ensure group is saved) 🔥
@bot.message_handler(content_types=['text', 'new_chat_members', 'left_chat_member'])
def background_tracker(message):
    if message.chat.type in ['group', 'supergroup']:
        track_group(message.chat.id)

# ==========================================
# 🔥 MAIN LOOP
# ==========================================
def keep_alive():
    while True:
        time.sleep(200)

if __name__ == "__main__":
    print(f"🔥 {SYSTEM_NAME} Online & Protected...")
    set_bot_commands() 
    threading.Thread(target=run_server, daemon=True).start()
    threading.Thread(target=keep_alive, daemon=True).start()
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            print(f"⚠️ Bot Crashed! Restarting... Error: {e}")
            time.sleep(2)
