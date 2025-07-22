"""
Keep-alive service for the British Virgin Islands Discord Bot
Prevents the bot from sleeping on hosting platforms like Render
"""
from flask import Flask, jsonify
import threading
import time
import requests
import logging
from config import settings

# Set up logging using settings
logger = settings.setup_logging()

app = Flask(__name__)

@app.route('/')
def home():
    """Health check endpoint"""
    return f"{settings.bot.bot_name} Discord Bot is alive!", 200

@app.route('/health')
def health():
    """Health check endpoint for monitoring services"""
    return jsonify({
        "status": "healthy", 
        "service": f"{settings.bot.bot_name} Discord Bot",
        "bot_name": settings.bot.bot_name
    }), 200

@app.route('/status')
def status():
    """Extended status endpoint with configuration info"""
    return jsonify({
        "status": "running",
        "service": f"{settings.bot.bot_name} Discord Bot",
        "channels": {
            "citizenship_log": settings.channels.citizenship_log,
            "citizenship_status": settings.channels.citizenship_status,
            "mod_log": settings.channels.mod_log
        },
        "admin_role_configured": settings.get_admin_role_id() != 0,
        "citizenship_manager_role_configured": settings.get_citizenship_manager_role_id() != 0,
        "port": settings.get_port()
    }), 200

def run_flask():
    """Run the Flask server"""
    port = settings.get_port()
    print(f"🌐 Starting health check server on port {port}")
    
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=False, 
        use_reloader=False,
        threaded=True
    )

def ping_self():
    """Send periodic pings to keep the service alive"""
    base_url = settings.get_render_url()
    ping_interval = settings.bot.keep_alive_interval
    timeout = settings.bot.api_timeout
    
    print(f"💓 Keep-alive monitoring started (every {ping_interval}s)")
    
    while True:
        try:
            response = requests.get(f"{base_url}/health", timeout=timeout)
            if response.status_code != 200:
                print(f"⚠️ Keep-alive ping failed with status: {response.status_code}")
        except requests.RequestException as e:
            print(f"❌ Keep-alive ping error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error during keep-alive ping: {e}")
        
        # Wait before next ping
        time.sleep(ping_interval)

def keep_alive():
    """Start the Flask server and ping scheduler"""
    try:
        # Start Flask server in a thread
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        
        # Give Flask time to start
        time.sleep(2)
        
        # Start pinging in a separate thread
        ping_thread = threading.Thread(target=ping_self, daemon=True)
        ping_thread.start()
        
        print("✅ Keep-alive service started successfully")
        
    except Exception as e:
        print(f"❌ Failed to start keep-alive service: {e}")

if __name__ == "__main__":
    keep_alive()
    # Keep the main thread alive
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Keep-alive service stopped")
