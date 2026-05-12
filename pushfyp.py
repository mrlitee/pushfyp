#!/usr/bin/env python3
"""
🚀 Push FYP Threads - Auto Engagement Tool
==========================================
Tool otomatis untuk push postingan Threads ke FYP
dengan meningkatkan engagement (like, repost, comment)
menggunakan multiple akun.

Cukup masukkan link postingan Threads!

Author: mrlitee
"""

import sys
import time
import random
import re
from datetime import datetime

from colorama import init, Fore, Style

from config import (
    get_accounts,
    get_comments,
    ENABLE_LIKE,
    ENABLE_REPOST,
    ENABLE_COMMENT,
)
from browser import create_driver, random_delay
from threads_actions import login, navigate_to_post, like_post, repost_post, comment_post

# Init colorama
init(autoreset=True)


# ===================== BANNER =====================

BANNER = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════╗
║                                                  ║
║  {Fore.WHITE}🚀 PUSH FYP THREADS - Auto Engagement Tool{Fore.CYAN}    ║
║                                                  ║
║  {Fore.YELLOW}Boost postingan Threads ke FYP secara otomatis{Fore.CYAN} ║
║  {Fore.YELLOW}dengan like, repost, dan comment multi-akun{Fore.CYAN}   ║
║                                                  ║
║  {Fore.GREEN}Author: @mrlitee{Fore.CYAN}                              ║
║  {Fore.GREEN}Version: 1.0.0{Fore.CYAN}                                ║
║                                                  ║
╚══════════════════════════════════════════════════╝
{Style.RESET_ALL}"""


# ===================== UTILITIES =====================


def validate_threads_url(url):
    """Validasi URL Threads"""
    patterns = [
        r"https?://(www\.)?threads\.net/@[\w.]+/post/[\w-]+",
        r"https?://(www\.)?threads\.net/t/[\w-]+",
    ]
    for pattern in patterns:
        if re.match(pattern, url):
            return True
    return False


def print_status(msg, status="info"):
    """Print pesan dengan warna"""
    icons = {
        "info": f"{Fore.BLUE}[ℹ]",
        "success": f"{Fore.GREEN}[✓]",
        "error": f"{Fore.RED}[✗]",
        "warning": f"{Fore.YELLOW}[!]",
        "action": f"{Fore.MAGENTA}[→]",
    }
    icon = icons.get(status, icons["info"])
    print(f"  {icon} {msg}{Style.RESET_ALL}")


def print_summary(results):
    """Print ringkasan hasil"""
    print(f"\n{Fore.CYAN}{'═' * 50}")
    print(f"  📊 RINGKASAN HASIL")
    print(f"{'═' * 50}{Style.RESET_ALL}")

    total = len(results)
    success_login = sum(1 for r in results if r["login"])
    success_like = sum(1 for r in results if r["like"])
    success_repost = sum(1 for r in results if r["repost"])
    success_comment = sum(1 for r in results if r["comment"])

    print(f"  {Fore.WHITE}Total Akun     : {total}")
    print(f"  {Fore.GREEN}Login Berhasil : {success_login}/{total}")
    if ENABLE_LIKE:
        print(f"  {Fore.GREEN}Like Berhasil  : {success_like}/{success_login}")
    if ENABLE_REPOST:
        print(f"  {Fore.GREEN}Repost Berhasil: {success_repost}/{success_login}")
    if ENABLE_COMMENT:
        print(f"  {Fore.GREEN}Comment Berhasil: {success_comment}/{success_login}")

    print(f"\n  {Fore.CYAN}{'═' * 50}{Style.RESET_ALL}")

    if success_login > 0:
        print(f"  {Fore.GREEN}🚀 Postingan berhasil di-push! Engagement +{success_like + success_repost + success_comment}")
    else:
        print(f"  {Fore.RED}❌ Tidak ada akun yang berhasil login")

    print()


# ===================== MAIN LOGIC =====================


def push_fyp(post_url):
    """
    Fungsi utama untuk push postingan ke FYP
    
    Args:
        post_url: URL postingan Threads
    """
    print(BANNER)

    # Validasi URL
    if not validate_threads_url(post_url):
        print_status("URL tidak valid! Gunakan format:", "error")
        print_status("  https://www.threads.net/@username/post/XXXXX", "info")
        print_status("  https://www.threads.net/t/XXXXX", "info")
        return

    print_status(f"Target: {post_url}", "action")
    print()

    # Load akun
    accounts = get_accounts()
    if not accounts:
        print_status("Tidak ada akun ditemukan!", "error")
        print_status("Tambahkan akun di file .env (lihat .env.example)", "info")
        return

    print_status(f"Ditemukan {len(accounts)} akun", "info")
    print_status(f"Mode: {'Like ' if ENABLE_LIKE else ''}{'Repost ' if ENABLE_REPOST else ''}{'Comment' if ENABLE_COMMENT else ''}", "info")
    print()

    # Load komentar random
    comments = get_comments()

    # Proses setiap akun
    results = []
    for idx, account in enumerate(accounts, 1):
        username = account["username"]
        password = account["password"]

        print(f"\n{Fore.YELLOW}  ┌─── Akun {idx}/{len(accounts)}: @{username} ───┐{Style.RESET_ALL}")

        result = {
            "username": username,
            "login": False,
            "like": False,
            "repost": False,
            "comment": False,
        }

        driver = None
        try:
            # Buat browser baru
            driver = create_driver()

            # Login
            if login(driver, username, password):
                result["login"] = True
                random_delay(2, 4)

                # Navigasi ke post
                if navigate_to_post(driver, post_url):

                    # Like
                    if ENABLE_LIKE:
                        result["like"] = like_post(driver)
                        random_delay(2, 4)

                    # Repost
                    if ENABLE_REPOST:
                        result["repost"] = repost_post(driver)
                        random_delay(2, 4)

                    # Comment
                    if ENABLE_COMMENT:
                        comment_text = random.choice(comments)
                        result["comment"] = comment_post(driver, comment_text)
                        random_delay(2, 4)

            else:
                print_status(f"Skip akun @{username} (login gagal)", "warning")

        except Exception as e:
            print_status(f"Error: {str(e)}", "error")

        finally:
            if driver:
                driver.quit()

        results.append(result)

        # Delay antar akun
        if idx < len(accounts):
            delay = random_delay(5, 10)
            print_status(f"Menunggu {delay:.1f}s sebelum akun berikutnya...", "info")

        print(f"{Fore.YELLOW}  └{'─' * 40}┘{Style.RESET_ALL}")

    # Print ringkasan
    print_summary(results)


# ===================== CLI =====================


def main():
    """Entry point CLI"""
    print(BANNER)

    if len(sys.argv) > 1:
        post_url = sys.argv[1]
    else:
        print(f"  {Fore.WHITE}Masukkan link postingan Threads:{Style.RESET_ALL}")
        post_url = input(f"  {Fore.GREEN}→ {Style.RESET_ALL}").strip()

    if not post_url:
        print_status("URL tidak boleh kosong!", "error")
        sys.exit(1)

    # Normalisasi URL
    if not post_url.startswith("http"):
        post_url = "https://" + post_url

    print()
    print_status(f"Waktu mulai: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "info")
    print()

    start_time = time.time()
    push_fyp(post_url)
    elapsed = time.time() - start_time

    print_status(f"Selesai dalam {elapsed:.1f} detik", "success")


if __name__ == "__main__":
    main()
