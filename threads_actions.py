"""
Modul aksi Threads: Login, Like, Repost, Comment
"""
import time
import random

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
)

from browser import (
    random_delay,
    wait_for_element,
    wait_and_click,
    human_type,
)
from config import THREADS_LOGIN_URL


def login(driver, username, password):
    """
    Login ke Threads menggunakan akun Instagram
    Returns: True jika berhasil, False jika gagal
    """
    try:
        print(f"    [→] Membuka halaman login...")
        driver.get(THREADS_LOGIN_URL)
        random_delay(3, 5)

        # Cari input username
        username_input = wait_for_element(
            driver, By.CSS_SELECTOR, 
            'input[autocomplete="username"], input[name="username"], input[type="text"]'
        )
        if not username_input:
            # Coba alternative selector
            username_input = wait_for_element(
                driver, By.XPATH, 
                '//input[@placeholder="Username, phone or email"]'
            )

        if not username_input:
            print(f"    [✗] Tidak bisa menemukan input username")
            return False

        # Ketik username
        username_input.clear()
        human_type(username_input, username)
        random_delay(1, 2)

        # Cari input password
        password_input = wait_for_element(
            driver, By.CSS_SELECTOR, 
            'input[autocomplete="current-password"], input[name="password"], input[type="password"]'
        )

        if not password_input:
            print(f"    [✗] Tidak bisa menemukan input password")
            return False

        # Ketik password
        password_input.clear()
        human_type(password_input, password)
        random_delay(1, 2)

        # Klik tombol login
        login_clicked = wait_and_click(
            driver, By.CSS_SELECTOR,
            'button[type="submit"], div[role="button"]'
        )

        if not login_clicked:
            # Tekan Enter sebagai alternatif
            password_input.send_keys(Keys.RETURN)

        random_delay(5, 8)

        # Verifikasi login berhasil
        current_url = driver.current_url
        if "login" not in current_url.lower() or "challenge" in current_url.lower():
            print(f"    [✓] Login berhasil sebagai @{username}")
            return True
        else:
            print(f"    [✗] Login gagal untuk @{username}")
            return False

    except Exception as e:
        print(f"    [✗] Error saat login: {str(e)}")
        return False


def navigate_to_post(driver, post_url):
    """
    Navigasi ke postingan Threads
    Returns: True jika berhasil
    """
    try:
        print(f"    [→] Membuka postingan...")
        driver.get(post_url)
        random_delay(3, 5)

        # Tunggu konten post muncul
        post_loaded = wait_for_element(
            driver, By.CSS_SELECTOR,
            'article, div[data-pressable-container="true"], main'
        )

        if post_loaded:
            print(f"    [✓] Postingan berhasil dimuat")
            return True
        else:
            print(f"    [!] Postingan mungkin belum sepenuhnya dimuat")
            return True  # Tetap lanjut

    except Exception as e:
        print(f"    [✗] Error navigasi: {str(e)}")
        return False


def like_post(driver):
    """
    Like postingan Threads
    Returns: True jika berhasil
    """
    try:
        print(f"    [→] Meng-like postingan...")
        random_delay(1, 3)

        # Selectors untuk tombol like di Threads
        like_selectors = [
            'svg[aria-label="Like"]',
            'svg[aria-label="Suka"]',
            '[aria-label="Like"]',
            '[aria-label="Suka"]',
            'div[role="button"] svg[fill="transparent"]',
        ]

        for selector in like_selectors:
            try:
                like_btn = driver.find_element(By.CSS_SELECTOR, selector)
                # Klik parent element jika svg
                parent = like_btn.find_element(By.XPATH, "./..")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", parent)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", parent)
                random_delay(1, 2)
                print(f"    [✓] Berhasil like postingan")
                return True
            except (NoSuchElementException, Exception):
                continue

        # Fallback: cari semua tombol dan coba klik yang like
        buttons = driver.find_elements(By.CSS_SELECTOR, 'div[role="button"]')
        for btn in buttons:
            try:
                svg = btn.find_element(By.TAG_NAME, "svg")
                aria = svg.get_attribute("aria-label") or ""
                if "like" in aria.lower() or "suka" in aria.lower():
                    driver.execute_script("arguments[0].click();", btn)
                    random_delay(1, 2)
                    print(f"    [✓] Berhasil like postingan (fallback)")
                    return True
            except Exception:
                continue

        print(f"    [!] Tidak bisa menemukan tombol like (mungkin sudah di-like)")
        return False

    except Exception as e:
        print(f"    [✗] Error saat like: {str(e)}")
        return False


def repost_post(driver):
    """
    Repost/quote postingan Threads
    Returns: True jika berhasil
    """
    try:
        print(f"    [→] Meng-repost postingan...")
        random_delay(1, 3)

        # Selectors untuk tombol repost
        repost_selectors = [
            'svg[aria-label="Repost"]',
            'svg[aria-label="Repost ulang"]',
            '[aria-label="Repost"]',
            '[aria-label="Repost ulang"]',
        ]

        for selector in repost_selectors:
            try:
                repost_btn = driver.find_element(By.CSS_SELECTOR, selector)
                parent = repost_btn.find_element(By.XPATH, "./..")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", parent)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", parent)
                random_delay(2, 3)

                # Klik opsi "Repost" di menu popup
                repost_option_selectors = [
                    '//span[contains(text(), "Repost")]',
                    '//div[contains(text(), "Repost")]',
                    '//span[contains(text(), "Repost ulang")]',
                ]

                for opt_selector in repost_option_selectors:
                    try:
                        opt = driver.find_element(By.XPATH, opt_selector)
                        driver.execute_script("arguments[0].click();", opt)
                        random_delay(1, 2)
                        print(f"    [✓] Berhasil repost postingan")
                        return True
                    except NoSuchElementException:
                        continue

                print(f"    [✓] Repost diklik (menu mungkin berbeda)")
                return True

            except (NoSuchElementException, Exception):
                continue

        # Fallback
        buttons = driver.find_elements(By.CSS_SELECTOR, 'div[role="button"]')
        for btn in buttons:
            try:
                svg = btn.find_element(By.TAG_NAME, "svg")
                aria = svg.get_attribute("aria-label") or ""
                if "repost" in aria.lower():
                    driver.execute_script("arguments[0].click();", btn)
                    random_delay(2, 3)
                    # Klik Repost di popup
                    try:
                        repost_opt = driver.find_element(
                            By.XPATH, '//span[contains(text(), "Repost")]'
                        )
                        driver.execute_script("arguments[0].click();", repost_opt)
                    except Exception:
                        pass
                    print(f"    [✓] Berhasil repost postingan (fallback)")
                    return True
            except Exception:
                continue

        print(f"    [!] Tidak bisa menemukan tombol repost")
        return False

    except Exception as e:
        print(f"    [✗] Error saat repost: {str(e)}")
        return False


def comment_post(driver, comment_text):
    """
    Komen pada postingan Threads
    Returns: True jika berhasil
    """
    try:
        print(f"    [→] Menambahkan komentar...")
        random_delay(1, 3)

        # Klik tombol reply/comment terlebih dahulu
        comment_btn_selectors = [
            'svg[aria-label="Reply"]',
            'svg[aria-label="Balas"]',
            'svg[aria-label="Comment"]',
            '[aria-label="Reply"]',
            '[aria-label="Balas"]',
            '[aria-label="Comment"]',
        ]

        comment_clicked = False
        for selector in comment_btn_selectors:
            try:
                comment_btn = driver.find_element(By.CSS_SELECTOR, selector)
                parent = comment_btn.find_element(By.XPATH, "./..")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", parent)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", parent)
                comment_clicked = True
                random_delay(2, 4)
                break
            except (NoSuchElementException, Exception):
                continue

        if not comment_clicked:
            # Fallback: cari button dengan svg reply
            buttons = driver.find_elements(By.CSS_SELECTOR, 'div[role="button"]')
            for btn in buttons:
                try:
                    svg = btn.find_element(By.TAG_NAME, "svg")
                    aria = svg.get_attribute("aria-label") or ""
                    if "reply" in aria.lower() or "balas" in aria.lower() or "comment" in aria.lower():
                        driver.execute_script("arguments[0].click();", btn)
                        comment_clicked = True
                        random_delay(2, 4)
                        break
                except Exception:
                    continue

        if not comment_clicked:
            print(f"    [!] Tidak bisa menemukan tombol komentar")
            return False

        # Cari text area untuk menulis komentar
        textarea_selectors = [
            'div[contenteditable="true"]',
            'div[role="textbox"]',
            'textarea',
            'p[data-placeholder]',
        ]

        textarea = None
        for selector in textarea_selectors:
            try:
                textarea = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                if textarea:
                    break
            except TimeoutException:
                continue

        if not textarea:
            print(f"    [!] Tidak bisa menemukan area komentar")
            return False

        # Ketik komentar
        textarea.click()
        time.sleep(0.5)
        human_type(textarea, comment_text)
        random_delay(1, 2)

        # Klik tombol post/kirim
        post_btn_selectors = [
            '//div[contains(text(), "Post")]',
            '//span[contains(text(), "Post")]',
            '//div[contains(text(), "Balas")]',
            '//span[contains(text(), "Balas")]',
            '//button[contains(text(), "Post")]',
            '//div[@role="button"][contains(., "Post")]',
        ]

        for selector in post_btn_selectors:
            try:
                post_btn = driver.find_element(By.XPATH, selector)
                driver.execute_script("arguments[0].click();", post_btn)
                random_delay(2, 3)
                print(f"    [✓] Berhasil komentar: '{comment_text}'")
                return True
            except (NoSuchElementException, Exception):
                continue

        # Fallback: Ctrl+Enter untuk post
        textarea.send_keys(Keys.CONTROL + Keys.RETURN)
        random_delay(2, 3)
        print(f"    [✓] Komentar dikirim (via Ctrl+Enter): '{comment_text}'")
        return True

    except Exception as e:
        print(f"    [✗] Error saat komentar: {str(e)}")
        return False
