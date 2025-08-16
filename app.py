from flask import Flask, jsonify
from flask_cors import CORS
from playwright.sync_api import sync_playwright
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for Unity requests

def scrape_christ_events():
    """Scrape events from Christ University Events Page using Playwright."""
    data = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://christuniversity.in/events", timeout=60000)
        page.wait_for_selector("div.tab-pane div.d-flex.flex-direction-row.mt-2")

        # Give extra time if necessary to load dynamic content
        time.sleep(2)

        events = page.query_selector_all("div.tab-pane div.d-flex.flex-direction-row.mt-2")
        for event in events[:10]:
            # Event title
            title = event.query_selector("h2").inner_text().strip() if event.query_selector("h2") else "Event Title"
            
            # You can add more field extractions similarly, for example:
            # date = event.query_selector(".event-date").inner_text().strip() if event.query_selector(".event-date") else ""
            # Add these once you inspect the site and confirm selectors
            
            data.append({
                "title": title,
                # Add other fields here
            })
        browser.close()
    return data

@app.route('/api/events', methods=['GET'])
def get_events():
    try:
        events = scrape_christ_events()
        return jsonify({
            "success": True,
            "count": len(events),
            "events": events
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "events": []
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Events API is running"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
