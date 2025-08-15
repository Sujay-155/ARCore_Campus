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
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins="*")  # Allow all origins for Unity

def scrape_christ_events():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--window-size=1920,1200")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument("--disable-javascript")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    
    # Set Chrome binary location
    chrome_options.binary_location = "/usr/bin/google-chrome"
    
    # Set ChromeDriver path
    service = Service("/usr/local/bin/chromedriver")
    
    data = []
    driver = None
    
    try:
        logger.info("Starting Chrome driver...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        url = "https://christuniversity.in/events"
        logger.info(f"Navigating to {url}")
        driver.get(url)
        
        # Wait for the main event container to be present
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.tab-pane")))
        logger.info("Page loaded successfully")
        
        events = driver.find_elements(By.CSS_SELECTOR, "div.tab-pane div.d-flex.flex-direction-row.mt-2")
        logger.info(f"Found {len(events)} events")
        
        for i, event in enumerate(events[:10]):  # Limit to 10 events
            try:
                img = event.find_element(By.CSS_SELECTOR, ".event-img img").get_attribute("src")
                info_spans = event.find_elements(By.CSS_SELECTOR, ".icon-info div span:nth-child(2)")
                date = info_spans[0].text.strip() if len(info_spans) > 0 else ""
                time_slot = info_spans[1].text.strip() if len(info_spans) > 1 else ""
                venue = info_spans[2].text.strip() if len(info_spans) > 2 else ""
                title = event.find_element(By.CSS_SELECTOR, "h2").text.strip()
                dept = event.find_element(By.CSS_SELECTOR, ".poppins-medium.rounded-pill.p-2.dep").text.strip()
                
                event_data = {
                    "title": title, 
                    "date": date, 
                    "time": time_slot, 
                    "venue": venue,
                    "category": dept, 
                    "image": img
                }
                data.append(event_data)
                logger.info(f"Successfully processed event {i+1}: {title}")
                
            except Exception as e:
                logger.error(f"Error processing event {i+1}: {e}")
                continue
                
    except Exception as e:
        logger.error(f"Error scraping events: {e}")
    finally:
        if driver:
            driver.quit()
            logger.info("Chrome driver closed")
    
    return data

@app.route('/')
def health_check():
    return jsonify({
        "status": "API is running", 
        "message": "Christ Events API is operational",
        "chrome_available": os.path.exists("/usr/bin/google-chrome"),
        "chromedriver_available": os.path.exists("/usr/local/bin/chromedriver")
    })

@app.route('/api/events', methods=['GET'])
def get_events():
    try:
        logger.info("Events endpoint called")
        events = scrape_christ_events()
        logger.info(f"Successfully scraped {len(events)} events")
        
        return jsonify({
            "success": True, 
            "count": len(events), 
            "events": events,
            "message": f"Successfully fetched {len(events)} events"
        })
    except Exception as e:
        logger.error(f"Error in get_events: {e}")
        return jsonify({
            "success": False, 
            "error": str(e), 
            "events": [],
            "message": "Failed to fetch events"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
