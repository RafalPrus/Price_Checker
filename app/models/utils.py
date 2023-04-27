import requests
from app.models.checker import Checker
from app.models.domain import Domain
from app.models.repositories.repositories import load_data, save_data
from datetime import datetime
import time
import smtplib
from config import email_sender, password_sender


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
        iteration = load_data().copy()
        for url, data in iteration.items():
            content = check_link_changes(url)
            # pack it into separate function for check only specific link info
            if content and content != data["content"]:
                send_email(url, email_sender, password_sender, data["content"], content)
                data["content"] = content
                data["changed"] = True
                print(f"Link {url} content has changed!")
                iteration[url] = data
            data["last_check_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if "counter" in data:
                new_data = data["counter"] + 1
                data["counter"] = new_data
            else:
                data["counter"] = 1
            save_data(iteration)
        time.sleep(2400)


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