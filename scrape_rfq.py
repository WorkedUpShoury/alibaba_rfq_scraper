import logging
import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def setup_driver():
    options = Options()
    options.add_argument('--disable-gpu')
    return webdriver.Chrome(options=options)

def extract_card_data(card, scraping_date):
    try:
        title_el = card.find_element(By.CLASS_NAME, "brh-rfq-item__subject-link")
        title = title_el.text.strip()
        rfq_url = title_el.get_attribute("href") or ""
        rfq_id = rfq_url.split("p=")[1].split("&")[0] if "p=" in rfq_url else ""

        inquiry_time = card.find_element(By.CLASS_NAME, "brh-rfq-item__publishtime").text.replace("Date Posted", "").replace(":", "").strip()
        quotes_left = card.find_element(By.CLASS_NAME, "brh-rfq-item__quote-left").text.replace("Quotes Left", "").strip()

        qty_num = card.find_element(By.CLASS_NAME, "brh-rfq-item__quantity-num").text
        qty_unit = card.find_element(By.CLASS_NAME, "brh-rfq-item__quantity-num").find_element(By.XPATH, './following-sibling::span').text
        quantity_required = f"{qty_num} {qty_unit}"

        country = card.find_element(By.CLASS_NAME, "brh-rfq-item__country").text.replace("Posted in:", "").strip()
        buyer_name = card.find_element(By.CSS_SELECTOR, ".brh-rfq-item__other-info .text").text.strip()

        try:
            buyer_image = card.find_element(By.CSS_SELECTOR, ".img-con img").get_attribute("src")
        except:
            buyer_image = ""

        tag_texts = [
            tag.text.strip().lower()
            for tag in card.find_elements(By.CSS_SELECTOR, ".brh-rfq-item__buyer-tag .next-tag-body")
        ]

        email_confirmed = "Yes" if "email confirmed" in tag_texts else "No"
        experienced_buyer = "Yes" if "experienced buyer" in tag_texts else "No"
        complete_order = "Yes" if "complete order via rfq" in tag_texts else "No"
        typical_replies = "Yes" if "typical replies" in tag_texts else "No"
        interactive_user = "Yes" if "interactive user" in tag_texts else "No"

        inquiry_url = "https:" + rfq_url if rfq_url.startswith("//") else rfq_url

        return {
            "RFQ ID": rfq_id,
            "Title": title,
            "Buyer Name": buyer_name,
            "Buyer Image": buyer_image,
            "Inquiry Time": inquiry_time,
            "Quotes Left": quotes_left,
            "Country": country,
            "Quantity Required": quantity_required,
            "Email Confirmed": email_confirmed,
            "Experienced Buyer": experienced_buyer,
            "Complete Order via RFQ": complete_order,
            "Typical Replies": typical_replies,
            "Interactive User": interactive_user,
            "Inquiry URL": inquiry_url,
            "Inquiry Date": scraping_date,
            "Scraping Date": scraping_date
        }
    except Exception as e:
        logging.warning(f"Error parsing card: {e}")
        return None

def scrape_rfq_site(base_url, max_pages=10):
    driver = setup_driver()
    logging.info(f"Opening URL: {base_url}")
    driver.get(base_url)

    WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "next-row-no-padding"))
    )

    data = []
    page = 1
    scraping_date = datetime.today().strftime("%d-%m-%Y")

    while page <= max_pages:
        logging.info(f"Scraping page {page}...")
        cards = driver.find_elements(By.CLASS_NAME, "next-row-no-padding")

        if not cards:
            logging.warning("No RFQ cards found.")
            break

        for card in cards:
            record = extract_card_data(card, scraping_date)
            if record:
                data.append(record)

        try:
            next_btn = driver.find_element(By.CLASS_NAME, "next")
            class_attr = next_btn.get_attribute("class") or ""
            if "disabled" in class_attr:
                logging.info("Reached last page.")
                break
            next_btn.click()
            page += 1
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "next-row-no-padding"))
            )
        except Exception as e:
            logging.warning(f"Pagination failed: {e}")
            break

    driver.quit()

    df = pd.DataFrame(data)
    df = df.drop_duplicates(subset=["RFQ ID", "Title"])
    output_file = "rfq_output.csv"
    df.to_csv(output_file, index=False)
    logging.info(f"Scraping complete. File saved as {output_file}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python scraper.py <RFQ_URL>")
    else:
        scrape_rfq_site(sys.argv[1])
