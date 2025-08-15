from flask import Flask, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

app = Flask(__name__)
CORS(app, origins="*")  # Allow all origins for Unity

def scrape_christ_events():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1200")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument("--disable-javascript")
    chrome_options.binary_location = "/usr/bin/google-chrome"
    
    service = Service("/usr/local/bin/chromedriver-linux64/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    data = []
    try:
        url = "https://christuniversity.in/events"
        driver.get(url)
        
        # Wait for the main event container to be present
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.tab-pane")))
        
        events = driver.find_elements(By.CSS_SELECTOR, "div.tab-pane div.d-flex.flex-direction-row.mt-2")
        
        for event in events[:10]:  # Limit to 10 events
            try:
                img = event.find_element(By.CSS_SELECTOR, ".event-img img").get_attribute("src")
                info_spans = event.find_elements(By.CSS_SELECTOR, ".icon-info div span:nth-child(2)")
                date = info_spans[0].text.strip() if len(info_spans) > 0 else ""
                time_slot = info_spans[1].text.strip() if len(info_spans) > 1 else ""
                venue = info_spans[2].text.strip() if len(info_spans) > 2 else ""
                title = event.find_element(By.CSS_SELECTOR, "h2").text.strip()
                dept = event.find_element(By.CSS_SELECTOR, ".poppins-medium.rounded-pill.p-2.dep").text.strip()
                
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
    except Exception as e:
        print(f"Error scraping events: {e}")
    finally:
        driver.quit()
    return data

@app.route('/')
def health_check():
    return jsonify({"status": "API is running", "message": "Christ Events API is operational"})

@app.route('/api/events', methods=['GET'])
def get_events():
    try:
        events = scrape_christ_events()
        return jsonify({
            "success": True, 
            "count": len(events), 
            "events": events,
            "message": f"Successfully fetched {len(events)} events"
        })
    except Exception as e:
        return jsonify({
            "success": False, 
            "error": str(e), 
            "events": [],
            "message": "Failed to fetch events"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)