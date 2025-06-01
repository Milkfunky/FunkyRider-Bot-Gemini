import os
from flask import Request # ไม่จำเป็นต้อง import Flask app โดยตรงใน GCF
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import google.generativeai as genai # สำหรับ Gemini

# ดึงค่าจาก Environment Variables
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') # หรือใช้ Service Account ตามที่แนะนำไปก่อนหน้า

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Configure Gemini API
# ถ้าใช้ API Key:
genai.configure(api_key=GEMINI_API_KEY)
# ถ้าใช้ Service Account (แนะนำ):
# ไม่ต้องกำหนดอะไร ถ้า GOOGLE_APPLICATION_CREDENTIALS ถูกตั้งค่าใน Environment
model = genai.GenerativeModel('gemini-pro')

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    reply_message = "ไม่เข้าใจคำถามของคุณ" # Default reply

    try:
        response = model.generate_content(user_message)
        gemini_response_text = response.text
        reply_message = gemini_response_text
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        reply_message = "เกิดข้อผิดพลาดในการเชื่อมต่อกับ Gemini API"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message)
    )

def line_webhook(request: Request):
    """
    Main function for Line Bot Webhook, to be deployed as a Google Cloud Function.
    """
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        return 'Invalid signature', 400 # Return appropriate HTTP status
    except Exception as e:
        print(f"Unhandled error: {e}")
        return 'Internal Server Error', 500
    return 'OK'