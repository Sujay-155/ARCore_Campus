from flask import Flask, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import traceback
import os

# Initialize Flask App
app = Flask(__name__)
CORS(app)  # Enable CORS for requests from your Unity app

def scrape_christ_events():
    """Scrape events from Christ University Events Page"""
    chrome_options = Options()
    # These arguments are essential for running in a Linux container like Azure's
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        # Use ChromeDriverManager to automatically handle driver installation
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"Failed to create Chrome driver with ChromeDriverManager: {e}")
        # Fallback: try to use system chromedriver if available
        try:
            driver = webdriver.Chrome(options=chrome_options)
        except Exception as e2:
            print(f"Failed to create Chrome driver without service: {e2}")
            raise e2
    
    try:
        url = "https://christuniversity.in/events"
        driver.get(url)
        
        # Wait for the initial event containers to be present on the page
        wait = WebDriverWait(driver, 20) # Increased wait time for cloud environment
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.tab-pane div.d-flex.flex-direction-row.mt-2")))
        
        # Scroll down to load all dynamically loaded events
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_scrolls = 10 # Limit scrolls to prevent infinite loops
        
        while scroll_attempts < max_scrolls:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2) # Allow time for new events to load
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                scroll_attempts += 1 # Increment if no new content is loaded
            else:
                scroll_attempts = 0 # Reset if new content was loaded
            last_height = new_height
        
        # Find all event elements after scrolling
        events = driver.find_elements(By.CSS_SELECTOR, "div.tab-pane div.d-flex.flex-direction-row.mt-2")
        data = []
        
        # Process up to 10 events to keep API response time reasonable
        for event in events[:10]:
            try:
                # Scrape event image URL
                try:
                    img = event.find_element(By.CSS_SELECTOR, ".event-img img").get_attribute("src")
                except:
                    img = "" # Fallback if no image is found
                
                # Scrape date, time, and venue from info spans
                info_spans = event.find_elements(By.CSS_SELECTOR, ".icon-info div span:nth-child(2)")
                date = info_spans[0].text.strip() if len(info_spans) > 0 else "Date not specified"
                time_slot = info_spans[1].text.strip() if len(info_spans) > 1 else "Time not specified"
                venue = info_spans[2].text.strip() if len(info_spans) > 2 else "Venue not specified"
                
                # Scrape event title
                try:
                    title = event.find_element(By.CSS_SELECTOR, "h2").text.strip()
                except:
                    title = "Event Title Not Found"
                
                # Scrape event category/department
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
                # Log error for a specific event card but continue processing others
                print(f"Error processing an event card: {e}")
                continue
        
        return data
        
    finally:
        # Ensure the browser is closed even if errors occur
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
        # Return a server error response if the scraping function fails
        return jsonify({
            "success": False,
            "error": str(e),
            "trace": traceback.format_exc(),
            "events": []
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify the API is running"""
    return jsonify({"status": "healthy", "message": "Events API is running"})

# This block is used for local testing. On Azure, Gunicorn will run the 'app' object directly.
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
