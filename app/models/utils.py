import os

import requests
from app.models.checker import Checker
from app.models.domain import Domain
from app.models.repositories.repositories import load_data, save_data
from datetime import datetime
import time
import smtplib

from config import email_sender, password_sender, shop_images_location


def check_link_changes(url: str):
    try:
        domain_to_scrap_symulator = ["wrangler.com", "zalando.pl"]
        for domain, scraper in Domain.DOMAIN_TO_SCRAPER.items():
            if domain in url:
                if domain in domain_to_scrap_symulator:
                    response = Checker.scrap_symulator(url)
                else:
                    response = requests.get(url)
                response.raise_for_status()
                content = scraper(response)
                return content
            else:
                return False

    except Exception as e:
        print(f"Error while checking link {url}: {e}")
        return False



def track_links():
    while True:
        tracking_data = load_data().copy()
        for url, data in tracking_data.items():
            new_content = check_link_changes(url)
            # pack it into separate function for check only specific link info
            data["last_check_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data = compare_data(url, data, new_content)
            data = count_loops(data)
            save_data(tracking_data)
        time.sleep(2400)

def track_separate_link(url):
    tracking_data = load_data().copy()
    new_content = check_link_changes(url)
    tracking_data[url] = compare_data(url, tracking_data[url], new_content)
    tracking_data[url] = count_loops(tracking_data[url])
    save_data(tracking_data)

def compare_data(url, data, new_content=None):
    if new_content and new_content != data["content"]:
        send_email(url, email_sender, password_sender, data["content"], new_content)
        data["content"] = new_content
        data["changed"] = True
        print(f"Link {url} content has changed!")
    return data

def clear_changed_status(url):
    tracking_data = load_data().copy()
    tracking_data[url]["changed"] = False
    save_data(tracking_data)

def count_loops(data):
    if "counter" in data:
        new_data = data["counter"] + 1
        data["counter"] = new_data
    else:
        data["counter"] = 1

    return data


def send_email(
    url: str,
    email: str,
    password: str,
    old_content: str,
    new_content: str,
    subject: str = "Cena się zmieniła!!",
):
    body = (
        "Cena produktu uległa zmianie: \n"
        + f"\nPoprzednie wartosci: \n"
        + old_content
        + f"\n\nNowe wartości: \n\n"
        + new_content
    )
    msg = f"Subject: {subject}\n\n{body}\n{url}".encode("UTF-8")
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(email, password)
    server.sendmail(email, email, msg)
    server.quit()


def create_product(file: dict, new_url: str):
    file[new_url] = {
        "content": check_link_changes(new_url),
        "changed": False,
        "check_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    return file


def load_images():
    images = os.listdir(shop_images_location)
    return images
