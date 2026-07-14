#!/usr/bin/env python3
"""
LINE Bot สำหรับตอบลูกค้าอะไหล่รถขุด
ค้นหาจากฐานข้อมูล Excel แล้วตอบลูกค้าโดยอัตโนมัติ
"""

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# ตั้งค่า LINE Bot
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# โหลดฐานข้อมูล
def load_database():
      """โหลดข้อมูลอะไหล่จากไฟล์ Excel"""
      try:
                df = pd.read_excel('อะไหล่รถขุดกาน.xlsx')
                return df
except FileNotFoundError:
        print("⚠️ ไฟล์ฐานข้อมูลไม่พบ")
        return None

# ค้นหาข้อมูลอะไหล่
def search_parts(keyword):
      """ค้นหาอะไหล่จากฐานข้อมูล"""
      df = load_database()
      if df is None:
                return None

      # ค้นหาในทุกคอลัมน์
      mask = df.astype(str).apply(lambda x: x.str.contains(keyword, case=False, na=False)).any(axis=1)
      results = df[mask]

    if len(results) == 0:
              return None

    # คืนผลลัพธ์ 5 รายการแรก
    return results.head(5)

# จัดรูปแบบข้อมูลสำหรับตอบลูกค้า
def format_response(results):
    if len(results) == 0:
        return "ไม่พบอะไหล่ที่ค้นหา กรุณาลองค้นหาด้วยคำอื่น"
        
    message = "ผลการค้นหาอะไหล่ดังนี้:\n\n"
    for idx, row in results.iterrows():
        part_name = row.get('ชื่อ', 'N/A')
        part_code = row.get('รหัสสินค้า', 'N/A')
        part_type = row.get('ประเภท', 'N/A')
        
        message += f"#{idx + 1}\n"
        message += f"📦 ชื่อ: {part_name}\n"
        message += f"🏷️ รหัส: {part_code}\n"
        message += f"🗂️ ประเภท: {part_type}\n"
        message += "---\n"
        
    return message

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
      """จัดการข้อความที่ได้รับจาก LINE"""
      user_message = event.message.text

    # ค้นหาข้อมูลอะไหล่
      results = search_parts(user_message)
      response_text = format_response(results)

    # ตอบกลับลูกค้า
      line_bot_api.reply_message(
          event.reply_token,
          TextSendMessage(text=response_text)
      )

if __name__ == '__main__':
      print("🤖 LINE Bot เริ่มทำงาน...")
      print("📍 Webhook URL: http://your-domain.com/callback")
      app.run(port=5000, debug=True)
