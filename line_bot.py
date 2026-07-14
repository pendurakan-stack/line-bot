#!/usr/bin/env python3
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

    message = "✅ Found parts:\n\n"
    for idx, (_, row) in enumerate(results.iterrows(), 1):
                part_name = str(row.get('ชื่อ', 'N/A'))
                part_code = str(row.get('รหัสสินค้า', 'N/A'))
                part_type = str(row.get('ประเภท', 'N/A'))

        message += f"{idx}. {part_name}\n"
        message += f"   Code: {part_code}\n"
        message += f"   Type: {part_type}\n\n"

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
