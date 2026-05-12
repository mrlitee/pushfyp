"""
Browser setup dan management menggunakan Selenium
"""
import time
import random

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
)
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent

from config import HEADLESS, DELAY_MIN, DELAY_MAX


def create_driver():
    """Buat instance Chrome WebDriver dengan settings anti-detection"""
    options = Options()

    if HEADLESS:
        options.add_argument("--headless=new")

    # Anti-detection settings
    ua = UserAgent()
    options.add_argument(f"--user-agent={ua.random}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=id-ID")

    # Exclude automation flags
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Remove webdriver detection
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
            """
        },
    )

    driver.implicitly_wait(10)
    return driver


def random_delay(min_sec=None, max_sec=None):
    """Delay random untuk menghindari deteksi bot"""
    min_sec = min_sec or DELAY_MIN
    max_sec = max_sec or DELAY_MAX
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)
    return delay


def wait_for_element(driver, by, value, timeout=20):
    """Tunggu elemen muncul di halaman"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        return None


def wait_and_click(driver, by, value, timeout=20):
    """Tunggu elemen lalu klik"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        # Scroll ke elemen
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.5)
        element.click()
        return True
    except (TimeoutException, ElementClickInterceptedException):
        try:
            element = driver.find_element(by, value)
            driver.execute_script("arguments[0].click();", element)
            return True
        except (NoSuchElementException, Exception):
            return False


def human_type(element, text):
    """Ketik teks seperti manusia (dengan delay antar karakter)"""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.15))
