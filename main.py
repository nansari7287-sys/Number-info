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

TOKEN = '8798383938:AAG39HCUnLkf3VtDWKodXo77zOBrZoxtv-k' 
OWNER_ID = 8448533037

# 📂 CHANNELS & GROUPS SETUP (REQUIREMENTS)
REQ_CHANNEL = "@frexyy_Era"
REQ_GROUP_1 = "@frexyyEra"

CHANNEL_LINK = "https://t.me/frexyy_Era"
GROUP_1_LINK = "https://t.me/frexyyEra"

SYSTEM_NAME = "@frexxxy"

# 🚨 API LINKS CONFIGURATION 🚨
API_AADHAAR = "https://num-info-paid.vercel.app/?num={}&key=ERROR" 
API_VEHICLE = "https://vehicleinfobyterabaap.vercel.app/lookup?rc={}"
API_PAK = "https://pkmkb.free.nf/api.php?number={}" 
API_IFSC = "https://ifsc.razorpay.com/{}"
API_BIN = "https://data.handyapi.com/bin/{}"
API_NUM = "https://database-sigma-nine.vercel.app/number/{}?api_key=YOUR-PASSWORD"
API_FAMILY = "https://aadhar-to-fam-chi.vercel.app/?key=FATIMAPSK&id={}"
API_V2NUM = "https://your-v2num-api.com/api?num={}" 
API_TG = "https://tg-to-num-six.vercel.app/?key=rootxsuryansh&q={}"

# 📂 DATABASE
DATA_FILE = "users_db.json"

# ==========================================
# 🌐 FLASK SERVER (FOR RENDER HOSTING)
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return f"{SYSTEM_NAME} Bot is Running 24/7 on Render!"

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
        telebot.types.BotCommand("start", "Start Bot & See Menu"),
        telebot.types.BotCommand("aadhaar", "Aadhaar Info"),
        telebot.types.BotCommand("pak", "Pak Number Info"),
        telebot.types.BotCommand("vehicle", "Vehicle Info"),
        telebot.types.BotCommand("num", "Number Info"),
        telebot.types.BotCommand("v2num", "V2 Number Info"),
        telebot.types.BotCommand("family", "Family Info"),
        telebot.types.BotCommand("tg", "Telegram User Info"),
        telebot.types.BotCommand("ifsc", "Bank IFSC Info"),
        telebot.types.BotCommand("bin", "Card BIN Info")
    ]
    bot.set_my_commands(commands)

# ==========================================
# 💾 DATABASE MANAGEMENT
# ==========================================
def load_db():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_db(data):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except: pass

def get_user_data(user_id):
    db = load_db()
    str_id = str(user_id)
    if str_id not in db:
        db[str_id] = {"joined_date": datetime.now().strftime("%Y-%m-%d"), "rank": "User"}
        save_db(db)
    return db, str_id

# ==========================================
# 🔒 SECURITY, MEMBERSHIP & CHAT FILTERS
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
    # 👇 Yahan change kiya hai: Ab bot kisi bhi group ya private chat me allow hoga 👇
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
        f"💳 **WELCOME USER**\n"
        f"╔══════════════════════╗\n"
        f"║ 👤 **NAME:** `{name}`\n"
        f"║ 🆔 **ID:** `{user.id}`\n"
        f"╚══════════════════════╝\n\n"
        f"🤖 **COMMANDS:**\n"
        f"👉 `/aadhaar 1234xxxx` - Aadhaar Info\n"
        f"👉 `/pak 0300xxxx` - Pak Info\n"
        f"👉 `/vehicle MH01xxxx` - Vehicle Info\n"
        f"👉 `/num 98xxxxxxxx` - Number Info\n"
        f"👉 `/v2num 98xxxxxxxx` - V2 Number Info\n"
        f"👉 `/family 1234xxxx` - Family Info\n"
        f"👉 `/tg @username` - Telegram Info\n"
        f"👉 `/ifsc SBIN0xxxx` - Bank IFSC Info\n"
        f"👉 `/bin 531xxxx` - Card BIN Info"
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
        "ration_card_no", "address", "relationship_name"
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
                    res += f"\n{space}▼ {str(k).upper()} ▼\n"
                    res += flatten(v, depth + 1)
                elif v not in [None, "", []]:
                    res += f"{space}{str(k).upper().ljust(15)} : {v}\n"
        
        elif isinstance(item, list):
            for i, val in enumerate(item, 1):
                res += f"\n{space}--- [ RECORD {i} ] ---\n"
                res += flatten(val, depth)
        else:
            res += f"{space}{item}\n"
            
        return res

    out = flatten(data)
    out = re.sub(r'\n\s*\n', '\n\n', out) 
    return out.strip()

# ==========================================
# 🚀 START COMMAND
# ==========================================
@bot.message_handler(commands=['start'])
def start(message):
    if not is_allowed_chat(message.chat): return
    
    user_id = message.from_user.id
    if not check_membership(user_id):
        send_force_join(message.chat.id, message.message_id)
        return

    send_welcome_menu(message.chat.id, message.from_user, message.message_id)

# ==========================================
# 🛠️ UNIVERSAL API ENGINE
# ==========================================
def handle_api(message, api_url, command_name):
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
def cmd_aadhaar(m): handle_api(m, API_AADHAAR, "Aadhaar")

@bot.message_handler(commands=['pak'])
def cmd_pak(m): handle_api(m, API_PAK, "Pak")

@bot.message_handler(commands=['vehicle'])
def cmd_vehicle(m): handle_api(m, API_VEHICLE, "Vehicle")

@bot.message_handler(commands=['num'])
def cmd_num(m): handle_api(m, API_NUM, "Number")

@bot.message_handler(commands=['v2num'])
def cmd_v2num(m): handle_api(m, API_V2NUM, "V2 Number")

@bot.message_handler(commands=['family'])
def cmd_family(m): handle_api(m, API_FAMILY, "Family")

@bot.message_handler(commands=['tg', 'telegram'])
def cmd_tg(m): handle_api(m, API_TG, "Telegram")

@bot.message_handler(commands=['ifsc'])
def cmd_ifsc(m): handle_api(m, API_IFSC, "IFSC")

@bot.message_handler(commands=['bin'])
def cmd_bin(m): handle_api(m, API_BIN, "BIN")

@bot.message_handler(commands=['getid'])
def get_group_id(message):
    if message.from_user.id == OWNER_ID:
        bot.reply_to(message, f"The ID of this chat is: `{message.chat.id}`\nType: {message.chat.type}")
    else:
        bot.reply_to(message, "You are not authorized to use this command.")

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
