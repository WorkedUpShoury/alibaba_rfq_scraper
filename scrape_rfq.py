import logging
import json
import time
import random
import pandas as pd
from datetime import datetime
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def load_selector_config(path):
    with open(path, 'r') as file:
        return json.load(file)


def is_scraping_allowed(url):
    parsed_url = urlparse(url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    rp = RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch("*", url)
    except Exception as e:
        logging.warning(f"Could not read robots.txt: {e}")
        return False


def setup_driver():
    options = Options()
    options.add_argument('--disable-gpu')
    options.add_argument('--headless')
    options.add_argument(
        'user-agent=RFQHarvester/0.1 (Educational use only)'
    )
    return webdriver.Chrome(options=options)


def extract_card_data(card, config, date):
    try:
        title_el = card.find_element(By.CSS_SELECTOR, config["title"])
        title = title_el.text.strip()
        rfq_url = title_el.get_attribute("href") or ""
        rfq_id = rfq_url.split("p=")[1].split("&")[0] if "p=" in rfq_url else ""

        inquiry_time = card.find_element(By.CSS_SELECTOR, config["inquiry_time"]).text.strip()
        quotes_left = card.find_element(By.CSS_SELECTOR, config["quotes_left"]).text.strip()

        qty_num = card.find_element(By.CSS_SELECTOR, config["quantity_num"]).text.strip()
        qty_unit = card.find_element(By.CSS_SELECTOR, config["quantity_unit"]).text.strip()
        quantity = f"{qty_num} {qty_unit}"

        country = card.find_element(By.CSS_SELECTOR, config["country"]).text.strip()
        buyer_name = card.find_element(By.CSS_SELECTOR, config["buyer_name"]).text.strip()

        try:
            buyer_image = card.find_element(By.CSS_SELECTOR, config["buyer_image"]).get_attribute("src")
        except:
            buyer_image = ""

        tag_texts = [
            tag.text.strip().lower()
            for tag in card.find_elements(By.CSS_SELECTOR, config["buyer_tags"])
        ]

        return {
            "RFQ ID": rfq_id,
            "Title": title,
            "Buyer Name": buyer_name,
            "Buyer Image": buyer_image,
            "Inquiry Time": inquiry_time,
            "Quotes Left": quotes_left,
            "Country": country,
            "Quantity Required": quantity,
            "Email Confirmed": "Yes" if "email confirmed" in tag_texts else "No",
            "Experienced Buyer": "Yes" if "experienced buyer" in tag_texts else "No",
            "Complete Order via RFQ": "Yes" if "complete order via rfq" in tag_texts else "No",
            "Typical Replies": "Yes" if "typical replies" in tag_texts else "No",
            "Interactive User": "Yes" if "interactive user" in tag_texts else "No",
            "Inquiry URL": rfq_url,
            "Inquiry Date": date,
            "Scraping Date": date
        }
    except Exception as e:
        logging.warning(f"Error extracting data from card: {e}")
        return None


def scrape_rfq_site(url, config, max_pages=10):
    if not is_scraping_allowed(url):
        logging.error("robots.txt disallows scraping this site.")
        return

    driver = setup_driver()
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, config["card"])))

    results = []
    page = 1
    scrape_date = datetime.today().strftime("%d-%m-%Y")

    while page <= max_pages:
        logging.info(f"Scraping page {page}...")
        cards = driver.find_elements(By.CSS_SELECTOR, config["card"])
        if not cards:
            logging.warning("No cards found.")
            break

        for card in cards:
            record = extract_card_data(card, config, scrape_date)
            if record:
                results.append(record)

        time.sleep(random.uniform(1.5, 3.5))  # respectful delay

        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, config["next_button"])
            if "disabled" in next_btn.get_attribute("class"):
                logging.info("Reached final page.")
                break
            next_btn.click()
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, config["card"])))
            page += 1
        except Exception as e:
            logging.warning(f"Pagination failed: {e}")
            break

    driver.quit()
    df = pd.DataFrame(results).drop_duplicates(subset=["RFQ ID", "Title"])
    df.to_csv("rfq_output.csv", index=False)
    logging.info("Scraping complete. Data saved to rfq_output.csv")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python scraper.py <URL> <selector_config.json>")
    else:
        url = sys.argv[1]
        selector_file = sys.argv[2]
        config = load_selector_config(selector_file)
        scrape_rfq_site(url, config)
