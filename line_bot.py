#!/usr/bin/env python3
"""
Simple LINE Bot for excavator parts sales
Searches Excel database and responds to customers
Clean version - no GitHub API calls
"""

import requests
import base64

TOKEN = "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"
REPO = "pendurakan-stack/line-bot"
FILE = "line_bot.py"

# Clean bot code - NO GitHub calls
CLEAN_BOT_CODE = '''#!/usr/bin/env python3
"""
LINE Bot for excavator parts sales
Searches Excel database and responds to customers
"""

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# LINE Bot configuration
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Global cache for database
_db = None

def load_database():
    """Load parts database from Excel file"""
    global _db
    if _db is not None:
        return _db

    try:
        _db = pd.read_excel('อะไหล่รถขุดกาน_2.xlsx')
        print(f"✅ Loaded {len(_db)} parts from Excel")
        return _db
    except FileNotFoundError:
        print("⚠️ Excel file not found: อะไหล่รถขุดกาน_2.xlsx")
        return None
    except Exception as e:
        print(f"⚠️ Error loading database: {e}")
        return None

def search_parts(keyword):
    """Search for parts by keyword"""
    df = load_database()
    if df is None or len(df) == 0:
        return None

    try:
        mask = df.astype(str).apply(lambda x: x.str.contains(keyword, case=False, na=False)).any(axis=1)
        results = df[mask]

        if len(results) == 0:
            return None

        return results.head(5)
    except Exception as e:
        print(f"⚠️ Search error: {e}")
        return None

def format_response(results):
    """Format search results as message"""
    if results is None or len(results) == 0:
        return "🔍 No parts found. Try different keywords."

    message = "✅ Found parts:\\n\\n"
    for idx, (_, row) in enumerate(results.iterrows(), 1):
        part_name = str(row.get('ชื่อ', 'N/A'))
        part_code = str(row.get('รหัสสินค้า', 'N/A'))
        part_type = str(row.get('ประเภท', 'N/A'))

        message += f"{idx}. {part_name}\\n"
        message += f"   Code: {part_code}\\n"
        message += f"   Type: {part_type}\\n\\n"

    message += "Contact us for more details"
    return message

@app.route('/callback', methods=['POST'])
def callback():
    """LINE webhook endpoint"""
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """Handle incoming messages"""
    try:
        user_message = event.message.text
        results = search_parts(user_message)
        response_text = format_response(results)

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response_text)
        )
    except Exception as e:
        print(f"⚠️ Error handling message: {e}")

if __name__ == '__main__':
    print("🤖 LINE Bot starting...")
    print("📍 Webhook: /callback")
    load_database()
    app.run(port=5000, debug=False)
'''

print("=" * 60)
print("🔧 Uploading CLEAN LINE BOT code")
print("=" * 60)

headers = {"Authorization": f"token {TOKEN}"}
url = f"https://api.github.com/repos/{REPO}/contents/{FILE}"

try:
    # Get current SHA
    print("\n📖 Getting current file...")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed: {response.status_code}")
        exit(1)

    sha = response.json()['sha']
    print(f"✅ Got SHA: {sha[:8]}")

    # Upload clean code
    print("\n📤 Uploading clean bot code...")
    content_b64 = base64.b64encode(CLEAN_BOT_CODE.encode()).decode()

    payload = {
        "message": "fix: replace bot code with clean version - remove GitHub API calls",
        "content": content_b64,
        "sha": sha,
        "branch": "main"
    }

    response = requests.put(url, json=payload, headers=headers)

    if response.status_code in [200, 201]:
        print("✅ Upload successful!")
        print(f"   Commit: {response.json()['commit']['sha'][:8]}")
        print("\n" + "=" * 60)
        print("🚀 Railway will redeploy in ~30-60 seconds")
        print("=" * 60)
        print("\n✅ Bot will now:")
        print("   1. Load Excel file from GitHub")
        print("   2. Search parts when users send messages")
        print("   3. NO GitHub API calls = NO 401 errors")
    else:
        print(f"❌ Upload failed: {response.status_code}")

except Exception as e:
    print(f"❌ Error: {e}")
