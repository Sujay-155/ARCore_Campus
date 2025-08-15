from flask import Flask, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import traceback

app = Flask(__name__)
CORS(app)

def scrape_christ_events():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # This simplified line is more robust for a Docker environment
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        url = "https://christuniversity.in/events"
        driver.get(url)
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.tab-pane div.d-flex.flex-direction-row.mt-2")))
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
        events = driver.find_elements(By.CSS_SELECTOR, "div.tab-pane div.d-flex.flex-direction-row.mt-2")
        data = []
        for event in events[:10]:
            try:
                img = event.find_element(By.CSS_SELECTOR, ".event-img img").get_attribute("src")
            except:
                img = ""
            info_spans = event.find_elements(By.CSS_SELECTOR, ".icon-info div span:nth-child(2)")
            date = info_spans[0].text.strip() if len(info_spans) > 0 else ""
            time_slot = info_spans[1].text.strip() if len(info_spans) > 1 else ""
            venue = info_spans[2].text.strip() if len(info_spans) > 2 else ""
            try:
                title = event.find_element(By.CSS_SELECTOR, "h2").text.strip()
            except:
                title = "Event Title"
            try:
                dept = event.find_element(By.CSS_SELECTOR, ".poppins-medium.rounded-pill.p-2.dep").text.strip()
            except:
                dept = "General"
            data.append({"title": title, "date": date, "time": time_slot, "venue": venue, "category": dept, "image": img})
        return data
    finally:
        driver.quit()

@app.route('/api/events', methods=['GET'])
def get_events():
    try:
        events = scrape_christ_events()
        return jsonify({"success": True, "count": len(events), "events": events})
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "trace": traceback.format_exc(), "events": []}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Events API is running"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
