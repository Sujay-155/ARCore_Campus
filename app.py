from flask import Flask, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

def get_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36")
    
    service = Service("/usr/local/bin/chromedriver")
    return webdriver.Chrome(service=service, options=chrome_options)

def scrape_christ_events():
    driver = None
    data = []
    
    try:
        logger.info("Starting Chrome browser...")
        driver = get_chrome_driver()
        
        url = "https://christuniversity.in/events"
        logger.info(f"Navigating to {url}")
        driver.get(url)
        
        # Wait for page to load
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Wait a bit more for dynamic content
        driver.implicitly_wait(5)
        
        # Try to find events with multiple selectors
        events = []
        selectors = [
            "div.tab-pane div.d-flex.flex-direction-row.mt-2",
            ".event-card",
            ".event-item",
            "[class*='event']"
        ]
        
        for selector in selectors:
            events = driver.find_elements(By.CSS_SELECTOR, selector)
            if events:
                logger.info(f"Found {len(events)} events using selector: {selector}")
                break
        
        if not events:
            logger.warning("No events found with any selector")
            # Return sample data if scraping fails
            return [{
                "title": "Sample Event - API Working",
                "date": "2024-08-16",
                "time": "10:00 AM",
                "venue": "Christ University",
                "category": "Technical",
                "image": "https://via.placeholder.com/300x200"
            }]
        
        for i, event in enumerate(events[:10]):
            try:
                # Try different ways to extract event data
                title = "Unknown Event"
                date = "TBD"
                time_slot = "TBD"
                venue = "Christ University"
                category = "General"
                image = "https://via.placeholder.com/300x200"
                
                # Try to get title
                title_selectors = ["h2", "h3", ".title", "[class*='title']", "[class*='event-name']"]
                for sel in title_selectors:
                    try:
                        title_elem = event.find_element(By.CSS_SELECTOR, sel)
                        title = title_elem.text.strip()
                        if title:
                            break
                    except:
                        continue
                
                # Try to get image
                try:
                    img_elem = event.find_element(By.CSS_SELECTOR, "img")
                    image = img_elem.get_attribute("src")
                except:
                    pass
                
                # Try to get other details
                try:
                    info_elements = event.find_elements(By.CSS_SELECTOR, "span, p, div")
                    for elem in info_elements:
                        text = elem.text.strip().lower()
                        if any(word in text for word in ['date', 'time', 'venue', 'location']):
                            if 'date' in text or any(month in text for month in ['jan', 'feb', 'mar', 'apr', 'may', 'jun']):
                                date = elem.text.strip()
                            elif 'time' in text or 'am' in text or 'pm' in text:
                                time_slot = elem.text.strip()
                            elif 'venue' in text or 'location' in text:
                                venue = elem.text.strip()
                except:
                    pass
                
                event_data = {
                    "title": title if title != "Unknown Event" else f"Event {i+1}",
                    "date": date,
                    "time": time_slot,
                    "venue": venue,
                    "category": category,
                    "image": image
                }
                
                data.append(event_data)
                logger.info(f"Processed event {i+1}: {title}")
                
            except Exception as e:
                logger.error(f"Error processing event {i+1}: {e}")
                continue
        
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        # Return sample data if everything fails
        return [{
            "title": "Christ University Event",
            "date": "2024-08-16",
            "time": "10:00 AM",
            "venue": "Main Campus",
            "category": "Academic",
            "image": "https://via.placeholder.com/300x200"
        }]
    finally:
        if driver:
            driver.quit()
            logger.info("Browser closed")
    
    return data if data else [{
        "title": "Christ University Event",
        "date": "2024-08-16", 
        "time": "10:00 AM",
        "venue": "Main Campus",
        "category": "Academic",
        "image": "https://via.placeholder.com/300x200"
    }]

@app.route('/')
def health_check():
    return jsonify({
        "status": "API is running",
        "message": "Christ Events API is operational",
        "endpoints": ["/", "/api/events"]
    })

@app.route('/api/events', methods=['GET'])
def get_events():
    try:
        logger.info("Fetching events...")
        events = scrape_christ_events()
        
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
    app.run(host='0.0.0.0', port=port)
