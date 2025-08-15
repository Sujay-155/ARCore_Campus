from flask import Flask, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC    
import json
import time
import traceback

app = Flask(__name__)
CORS(app)  # Enable CORS for Unity requests

def scrape_christ_events():
    """Scrape events from Christ University Events Page"""
    chrome_options = Options()
    chrome_options.binary_location =  "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")


    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        url = "https://christuniversity.in/events"
        driver.get(url)
        
        # Wait for events to load
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.tab-pane div.d-flex.flex-direction-row.mt-2")))
        
        # Scroll to load all events
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_scrolls = 10
        
        while scroll_attempts < max_scrolls:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                scroll_attempts += 1
            else:
                scroll_attempts = 0
                last_height = new_height
        
        # Extract events
        events = driver.find_elements(By.CSS_SELECTOR, "div.tab-pane div.d-flex.flex-direction-row.mt-2")
        data = []
        
        for event in events[:10]:  # Limit to 10 events for performance
            try:
                # Event image
                try:
                    img = event.find_element(By.CSS_SELECTOR, ".event-img img").get_attribute("src")
                except:
                    img = ""
                
                # Extract date, time, venue
                info_spans = event.find_elements(By.CSS_SELECTOR, ".icon-info div span:nth-child(2)")
                date = info_spans[0].text.strip() if len(info_spans) > 0 else ""
                time_slot = info_spans[1].text.strip() if len(info_spans) > 1 else ""
                venue = info_spans[2].text.strip() if len(info_spans) > 2 else ""
                
                # Title
                try:
                    title = event.find_element(By.CSS_SELECTOR, "h2").text.strip()
                except:
                    title = "Event Title"
                
                # Department/Category
                try:
                    dept = event.find_element(By.CSS_SELECTOR, ".poppins-medium.rounded-pill.p-2.dep").text.strip()
                except:
                    dept = "General"
                
                data.append({
                    "title": title,
                    "date": date,
                    "time": time_slot,
                    "venue": venue,
                    "category": dept,
                    "image": img
                })
            except Exception as e:
                print(f"Error processing event: {e}")
                continue
        
        return data
        
    finally:
        driver.quit()

@app.route('/api/events', methods=['GET'])
def get_events():
    """API endpoint to get Christ University events"""
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
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Events API is running"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)