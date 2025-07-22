import asyncio
import threading
from bot import run_bot
from keep_alive import keep_alive

def main():
    # Start the keep-alive server in a separate thread
    keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
    keep_alive_thread.start()
    
    # Start the Discord bot
    run_bot()

if __name__ == "__main__":
    main()
