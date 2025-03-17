import os
import pyautogui
import time
import json
import logging
import requests
import configparser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ログの設定
current_directory = os.path.dirname(os.path.abspath(__file__))
log_directory = os.path.join(current_directory, 'log')
os.makedirs(log_directory, exist_ok=True)
log_file = os.path.join(log_directory, 'process.log')
logging.basicConfig(filename=log_file, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class Scraper:
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password
        self.processed_records = set()

        self.chrome_options = Options()
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--safebrowsing-disable-download-protection')
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--allow-running-insecure-content')
        self.chrome_options.add_argument('--ignore-certificate-errors')
        self.chrome_options.add_argument('--disable-popup-blocking')

        prefs = {
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False,
            "safebrowsing.disable_download_protection": True,
            "profile.default_content_setting_values.automatic_downloads": 1,
            "profile.content_settings.exceptions.automatic_downloads.*.setting": 1
        }
        self.chrome_options.add_experimental_option("prefs", prefs)

        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=self.chrome_options)

        self.login()
        self.load_config()

    def load_config(self):
        config = configparser.ConfigParser()
        config_file = 'input.ini'

        if os.path.exists(config_file):
            config.read(config_file)
            if 'DEFAULT' in config:
                return {
                    'store_id': config['DEFAULT'].get('store_id', 'netz_sanyo'),
                    'shop_code': config['DEFAULT'].get('shop_code', '05')
                }

        return {
            'store_id': 'netz_sanyo',
            'shop_code': '05'
        }

    def send_phone_data(self, current_datetime, caller_phone_number, receiver_phone_number, call_duration=0, call_content="", call_summary=""):
        url = 'https://operation2020.jp/api/kepler_gpt'
        headers = {
            'Content-Type': 'application/json',
            'X-API-AUTH': 'd240b427b1ef22d10234c25e1a08855e'
        }

        config = self.load_config()
        store_id = config['store_id']
        shop_code = config['shop_code']

        payload = {
            "store_id": store_id,
            "shop_code": shop_code,
            "call_datetime": current_datetime,
            "call_duration": call_duration,
            "caller_phone_number": caller_phone_number,
            "receiver_phone_number": receiver_phone_number,
            "call_content": call_content,
            "call_summary": call_summary
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()

            logging.info(f"APIリクエスト成功: {response.json()}")
            return response.json()

        except requests.exceptions.RequestException as e:
            logging.error(f"APIリクエストエラー: {e}")
            return {"error": str(e)}


    def login(self):
        self.driver.get(self.url)
        time.sleep(3)
        pyautogui.write(self.username)
        pyautogui.press('tab')
        pyautogui.write(self.password)
        pyautogui.press('enter')
        time.sleep(3)

    def go_to_voicemail(self):
        try:
            self.driver.get(f"{self.url}/vm/vm.html?uid=10")
            time.sleep(5)
            mailbox_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "mbxno_input"))
            )
            mailbox_input.clear()
            mailbox_input.send_keys("89")
            
            select_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "btnSet"))
            )
            select_button.click()

            all_option = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@type='radio' and @name='hyouji' and @value='zen']"))
            )
            all_option.click()

        except NoSuchElementException as e:
            logging.error(f'Failed to find element: {e}')
        except TimeoutException as e:
            logging.error(f'Timeout waiting for element: {e}')
        finally:
            logging.info("End voicemail")

    def refresh_page(self):
        self.driver.refresh()
        time.sleep(3)

        all_option = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='radio' and @name='hyouji' and @value='zen']"))
        )
        all_option.click()

    def get_recent_records(self):
        try:
            time.sleep(5)
            
            table = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div/div[2]/form[2]/div[3]/table"))
            )
            rows = table.find_elements(By.TAG_NAME, "tr")
            
            if len(rows) > 0 and "日時" in rows[0].text:
                rows = rows[1:]
            
            records = []
            new_records_count = 0
            
            for row in rows:
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    
                    if len(cells) < 11:  # Make sure we have enough cells
                        continue
                    
                    record_data = {}
                    
                    record_data['number'] = cells[1].text.strip()
                    record_data['read'] = cells[2].text.strip()
                    record_data['recording_time'] = cells[3].text.strip()
                    record_data['recording_date_and_time'] = cells[4].text.strip()
                    record_data['caller_name'] = cells[5].text.strip()
                    record_data['caller_number'] = cells[6].text.strip()
                    record_data['dial_in_number'] = cells[7].text.strip()
                    record_data['call_line'] = cells[8].text.strip()
                    record_data['last_caller_name'] = cells[9].text.strip()
                    record_data['last_caller_number'] = cells[10].text.strip()
                    record_data['call_summary'] = f"{record_data['read']}, {record_data['call_line']}, {record_data['last_caller_name']}, {record_data['last_caller_number']}"

                    # Create a unique identifier for this record using the specified fields
                    record_id = (
                        record_data['recording_time'],
                        record_data['recording_date_and_time'],
                        record_data['caller_number'],
                        record_data['dial_in_number']
                    )
                    
                    # Check if this record has been processed before
                    if record_id not in self.processed_records:
                        # This is a new record, send it to the backend
                        self.send_phone_data(
                            record_data['recording_date_and_time'], 
                            record_data['caller_number'], 
                            record_data['dial_in_number'], 
                            record_data['recording_time'], 
                            record_data['caller_name'], 
                            record_data['call_summary']
                        )
                        
                        # Add to processed records set
                        self.processed_records.add(record_id)
                        new_records_count += 1
                        logging.info(f"New record found and sent: {record_id}")
                    else:
                        logging.info(f"Skipping already processed record: {record_id}")
                    
                    records.append(record_data)
                    
                except Exception as e:
                    logging.error(f'Error processing row: {e}')
                    continue
            
            logging.info(f"Total records extracted: {len(records)}, New records sent: {new_records_count}")
            return records

        except NoSuchElementException as e:
            logging.error(f'Failed to find table element: {e}')
            return []
        except TimeoutException as e:
            logging.error(f'Timeout waiting for table element: {e}')
            return []
        except Exception as e:
            logging.error(f'An error occurred while getting records: {e}')
            return []
        finally:
            logging.info("End get recent records")

    def end_session(self):
        self.driver.quit()