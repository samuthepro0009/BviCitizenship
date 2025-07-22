import os
from flask import Flask
import threading
import time
import requests
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    """Health check endpoint"""
    return "British Virgin Islands Discord Bot is alive!", 200

@app.route('/health')
def health():
    """Health check endpoint for monitoring services"""
    return {"status": "healthy", "service": "BVI Discord Bot"}, 200

def run_flask():
    """Run the Flask server"""
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def ping_self():
    """Send periodic pings to keep the service alive"""
    base_url = os.getenv('RENDER_EXTERNAL_URL', 'http://localhost:5000')
    
    while True:
        try:
            response = requests.get(f"{base_url}/health", timeout=10)
            if response.status_code == 200:
                logger.info("Keep-alive ping successful")
            else:
                logger.warning(f"Keep-alive ping failed with status: {response.status_code}")
        except requests.RequestException as e:
            logger.error(f"Keep-alive ping error: {e}")
        
        # Wait 30 seconds before next ping
        time.sleep(30)

def keep_alive():
    """Start the Flask server and ping scheduler"""
    # Start Flask server in a thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Give Flask time to start
    time.sleep(2)
    
    # Start pinging in a separate thread
    ping_thread = threading.Thread(target=ping_self, daemon=True)
    ping_thread.start()
    
    logger.info("Keep-alive service started")

if __name__ == "__main__":
    keep_alive()
    # Keep the main thread alive
    while True:
        time.sleep(60)
