from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
CORS(app)


EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

print("📧 ইমেইল কনফিগারেশন চেক:")
print(f"ইমেইল: {EMAIL_ADDRESS}")
print(f"পাসওয়ার্ড: {'*' * len(EMAIL_PASSWORD) if EMAIL_PASSWORD else 'নেই'}")


@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)


@app.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory('static/images', filename)

def send_elite_email(name, client_email, service, message):
    """এলিট ওয়েবের জন্য ইমেইল পাঠানো"""
    try:
        print(f"📨 ইমেইল পাঠানো হচ্ছে: {name} - {service}")
        
        
        subject = f"🚀 এলিট ওয়েব - নতুন ক্লায়েন্ট: {name}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: #0f0f0f;
                    color: #ffffff;
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: #1a1a1a;
                    border-radius: 10px;
                    overflow: hidden;
                    border: 1px solid #00f3ff;
                }}
                .header {{
                    background: linear-gradient(135deg, #00f3ff, #b300ff);
                    padding: 30px;
                    text-align: center;
                }}
                .content {{
                    padding: 30px;
                }}
                .info-box {{
                    background: rgba(255,255,255,0.1);
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚡ এলিট ওয়েব ডেভেলপমেন্ট</h1>
                    <p>নতুন ক্লায়েন্ট কন্টাক্ট</p>
                </div>
                <div class="content">
                    <div class="info-box">
                        <h3>👤 ক্লায়েন্ট তথ্য</h3>
                        <p><strong>নাম:</strong> {name}</p>
                        <p><strong>ইমেইল:</strong> {client_email}</p>
                        <p><strong>সার্ভিস:</strong> {service}</p>
                    </div>
                    <div class="info-box">
                        <h3>💬 মেসেজ</h3>
                        <p>{message}</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        
        text_body = f"""
        এলিট ওয়েব - নতুন ক্লায়েন্ট
        
        নাম: {name}
        ইমেইল: {client_email}
        সার্ভিস: {service}
        
        মেসেজ:
        {message}
        """
        
        
        msg = MIMEMultipart('alternative')
        msg['From'] = f"Elite Web <{EMAIL_ADDRESS}>"
        msg['To'] = EMAIL_ADDRESS
        msg['Subject'] = subject
        msg['Reply-To'] = client_email
        
        
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
            
        print("✅ ইমেইল সফলভাবে পাঠানো হয়েছে!")
        return True
        
    except Exception as e:
        print(f"❌ ইমেইল এরর: {e}")
        return False

@app.route('/')
def home():
    """মূল ওয়েবসাইট দেখাবে"""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """সার্ভার চেক"""
    return jsonify({
        "status": "সক্রিয়",
        "message": "এলিট ওয়েব ব্যাকএন্ড কাজ করছে! 🚀",
        "email_configured": bool(EMAIL_ADDRESS and EMAIL_PASSWORD)
    })

@app.route('/api/contact', methods=['POST'])
def handle_contact():
    """কন্টাক্ট ফর্ম হ্যান্ডল করবে"""
    try:
        
        data = request.get_json()
        print(f"📩 নতুন রিকুয়েস্ট: {data}")
        
        if not data:
            return jsonify({"error": "কোন ডেটা পাওয়া যায়নি"}), 400
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        service = data.get('service', '').strip()
        message = data.get('message', '').strip()
        
        
        if not name:
            return jsonify({"error": "আপনার নাম লিখুন"}), 400
        if not email or '@' not in email:
            return jsonify({"error": "বৈধ ইমেইল দিন"}), 400
        if not service:
            return jsonify({"error": "সার্ভিস সিলেক্ট করুন"}), 400
        if not message:
            return jsonify({"error": "মেসেজ লিখুন"}), 400
        
    
        if send_elite_email(name, email, service, message):
            return jsonify({
                "success": True,
                "message": "ধন্যবাদ! আপনার মেসেজ পাঠানো হয়েছে। শীঘ্রই যোগাযোগ করব। 🚀"
            })
        else:
            return jsonify({"error": "ইমেইল পাঠানো যায়নি"}), 500
            
    except Exception as e:
        print(f"❌ সার্ভার এরর: {e}")
        return jsonify({"error": "সার্ভার সমস্যা"}), 500

if __name__ == '__main__':
    print("🚀 এলিট ওয়েব সার্ভার শুরু হচ্ছে...")
    print("📍 URL: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)