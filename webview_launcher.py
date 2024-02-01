import webview
import threading
from app import app  # Import your Flask app

def run_flask():
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)


if __name__ == '__main__':
    # Run Flask in a separate thread
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

    # Create a PyWebView window that points to the Flask app
    webview.create_window('Home Information System', 'http://127.0.0.1:5000/')
    webview.start()
    
