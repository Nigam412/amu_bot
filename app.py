from flask import Flask, request
import requests
from ai_logic import generate_reply  # Make sure ai_logic.py file exists
import logging
import json

app = Flask(__name__)

# --- 🚨 IMPORTANT 🚨 ---
# 1. YAHAN APNA SECRET VERIFY TOKEN LIKHEIN
# Yeh aap khud banayein (e.g., "my_super_secret_bot_123")
# Yahi token aapko Meta Dashboard mein bhi daalna hai.
VERIFY_TOKEN = "nigam_1234" 

# 2. 🚨 SECURITY WARNING! 🚨
# Aapka ACCESS_TOKEN public ho chuka hai.
# Kripya ise turant Meta Dashboard se RESET karein!
# Ise code mein aise direct likhna unsafe hai. Environment variables ka istemaal karein.
ACCESS_TOKEN = "EAA1O6ZBHz3rcBPyL5dZAB4o4CyR1GS80py4ENZAJOfYA3flJh88ETGRRXHlJrKkmgFn2mIB04EhJ7edvbjfFNxpiDhaFpQgQlCvocZBFjnDYFZCmAyuPr7w4hEuvZCbJnM8teNJIZA7SerLJymODtvrOHyjsAgwlt1aanmZCwsowNZCJsGLdlXi6hIGyZCJMR0X7NhbvukcYc6v8k32kyQSyzVm8iDmdMZA1BgI38D7Agoor49fggZDZD"
PHONE_ID = "865232840000202"
# --- End of Warning ---

# Logging setup taaki aap errors terminal mein dekh sakein
logging.basicConfig(level=logging.INFO)

def send_whatsapp_message(to, message):
    """WhatsApp par message bhejta hai."""
    url = f"https://graph.facebook.com/v17.0/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status() # HTTP errors ke liye check karega
        app.logger.info(f"Message sent to {to}: {response.json()}")
    except requests.exceptions.RequestException as e:
        app.logger.error(f"❌ Error sending message: {e}")

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """
    Yeh function do kaam karta hai:
    1. GET Request: Meta se verification ke liye.
    2. POST Request: Naye messages receive karne ke liye.
    """
    
    # === Meta Webhook Verification (GET Request) ===
    if request.method == 'GET':
        app.logger.info("Received verification request (GET)")
        
        # Check karein ki VERIFY_TOKEN match hua ya nahi
        if request.args.get('hub.mode') == 'subscribe' and request.args.get('hub.verify_token') == VERIFY_TOKEN:
            # Agar match hua, toh 'hub.challenge' ko wapas bhejein
            app.logger.info("✅ Verification successful!")
            return request.args.get('hub.challenge'), 200
        else:
            # Agar match nahi hua
            app.logger.error("❌ Verification failed! Tokens do not match.")
            return "Verification failed, token mismatch", 403

    # === Naye Message Handle Karna (POST Request) ===
    if request.method == 'POST':
        app.logger.info("Received new message (POST)")
        data = request.json
        
        # Log karein ki kya data aaya hai (debug ke liye)
        app.logger.debug(json.dumps(data, indent=2)) 

        try:
            # Check karein ki data sahi format mein hai
            if 'entry' in data and data['entry'] and 'changes' in data['entry'][0] and \
               data['entry'][0]['changes'] and 'value' in data['entry'][0]['changes'][0] and \
               'messages' in data['entry'][0]['changes'][0]['value'] and \
               data['entry'][0]['changes'][0]['value']['messages']:
                
                message_data = data['entry'][0]['changes'][0]['value']['messages'][0]
                
                # Sirf text messages ko process karein
                if 'text' in message_data:
                    sender_phone = message_data['from']
                    message_body = message_data['text']['body']
                    app.logger.info(f"Message from {sender_phone}: {message_body}")
                    
                    # AI logic se reply generate karein
                    reply = generate_reply(message_body)
                    
                    # Reply wapas WhatsApp par bhej dein
                    send_whatsapp_message(sender_phone, reply)
            
            # Meta ko batayein ki sab theek hai
            return "OK", 200
        
        except Exception as e:
            app.logger.error(f"❌ Error processing POST request: {e}", exc_info=True)
            return "Error", 500 # Internal server error

    # Agar koi aur method (jaise PUT/DELETE) aaye
    return "Method Not Allowed", 405

if __name__ == '__main__':
    # Database setup check
    try:
        # Simple check to see if ai_logic can be imported and run
        test_reply = generate_reply("test")
        app.logger.info(f"Test reply: {test_reply}")
        app.logger.info("Database connection (ai_logic) seems OK.")
    except Exception as e:
        app.logger.error(f"❌ Could not initialize ai_logic. Did you run db_setup.py?\nError: {e}")
        
    app.run(port=5000, debug=True) 
