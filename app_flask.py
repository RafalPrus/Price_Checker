import time
from datetime import datetime
import threading
from bs4 import BeautifulSoup
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from config import email_sender, password_sender
import smtplib
import json
import os
import cloudscraper


DATA_FILE = "data/tracked_links.json"


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        data = {key: value for key, value in sorted(data.items())}
        json.dump(data, f)


app = Flask(__name__)
app.config["SECRET_KEY"] = "my_secret_key"
tracked_links = load_data()


def check_link_changes(url):
    try:
        domain_to_scrap_symulator = ["wrangler.com", "zalando.pl"]

        for domain, scraper in Domains.DOMAIN_TO_SCRAPER.items():
            if domain in url:
                if domain in domain_to_scrap_symulator:
                    r = Checker.scrap_symulator(url)
                else:
                    r = requests.get(url)
                r.raise_for_status()
                content = scraper(r)
                return content
            else:
                return False

        # If no matching domain found
        print("Ta witryna nie jest obsługiwana...")
        r = requests.get(url)
        r.raise_for_status()

    except Exception as e:
        print(f"Error checking link {url}: {e}")
        return None


class Checker:
    @staticmethod
    def check_answear_com(source):
        content = BeautifulSoup(source.content, "html.parser")
        return " ".join(
            content.find(
                "div", {"class": "ProductCard__priceWrapper__Tyf2d"}
            ).text.split()
        )

    @staticmethod
    def check_leecooper(source):
        content = BeautifulSoup(source.content, "html.parser")
        return " ".join(
            content.find("div", {"class": "projector_price_subwrapper"}).text.split()
        )

    @staticmethod
    def check_ewozki(source):
        content = BeautifulSoup(source.content, "html.parser")
        return " ".join(content.find("div", {"class": "price-flex"}).text.split())

    @staticmethod
    def check_wrangler(source):
        content = BeautifulSoup(source.content, "html.parser")
        return " ".join(content.find("div", {"class": "prices"}).text.split())

    @staticmethod
    def check_zalando(source):
        content = BeautifulSoup(source.content, "html.parser")
        return " ".join(
            content.find("div", {"class": "_0xLoFW u9KIT8 vSgP6A"}).text.split()
        )

    @staticmethod
    def scrap_symulator(url):
        scraper = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "windows", "desktop": True}
        )
        return scraper.get(url)


def track_links():
    while True:
        iteration = load_data().copy()
        for url, data in iteration.items():
            content = check_link_changes(url)
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


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        print(request.form.get("url"))
        if url:
            if Domains.domain_validator(url):
                tracked_links = load_data()
                tracked_links[url] = {
                    "content": check_link_changes(url),
                    "changed": False,
                    "check_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                save_data(tracked_links)
                return redirect(url_for("index"))
            else:
                print("Ta strona nie jest obsługiwana!")
                flash("Niedozwolona nazwa, wybierz inną!")
                tracked_links = load_data()
                return render_template("index.html", tracked_links=tracked_links)
    tracked_links = load_data()
    return render_template("index.html", tracked_links=tracked_links)


@app.route("/delete/<path:url>")
def delete(url):
    tracked_links = load_data()
    if url in tracked_links:
        del tracked_links[url]
        save_data(tracked_links)
    return redirect(url_for("index"))


def send_email(
    url,
    email_sender,
    password_sender,
    old_content,
    new_content,
    subject="Cena się zmieniła!!",
    body="Cena produktu uległa zmianie: \n",
):
    email = email_sender
    password = password_sender
    body = (
        body
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


class Domains:
    DOMAIN_TO_SCRAPER = {
        "answear.com": Checker.check_answear_com,
        "leecooper": Checker.check_leecooper,
        "ewozki.eu": Checker.check_ewozki,
        "wrangler.com": Checker.check_wrangler,
        "zalando.pl": Checker.check_zalando,
    }

    @classmethod
    def domain_validator(cls, url):
        for domain, scraper in Domains.DOMAIN_TO_SCRAPER.items():
            if domain in url:
                return True
        return False


if __name__ == "__main__":
    tracking_thread = threading.Thread(target=track_links, daemon=True)
    tracking_thread.start()
    app.run(debug=True, host="0.0.0.0")
