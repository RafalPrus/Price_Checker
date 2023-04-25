import time
from datetime import datetime
import threading
from bs4 import BeautifulSoup
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from repositories import load_data, save_data
from config import email_sender, password_sender, secret_key
import smtplib
import cloudscraper





app = Flask(__name__)
app.config["SECRET_KEY"] = secret_key
tracked_links = load_data()



def check_link_changes(url: str):
    try:
        domain_to_scrap_symulator = ["wrangler.com", "zalando.pl"]

        for domain, scraper in Domains.DOMAIN_TO_SCRAPER.items():
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
        print(f'typ wozki: ')
        print(type(source))
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
    tracked_links = load_data()
    if request.method == "POST":
        url = request.form.get("url")
        if url:
            if Domains.domain_validator(url):
                create_product(tracked_links, url)
                save_data(tracked_links)
                return redirect(url_for("index"))
            else:
                flash("Niedozwolona nazwa, wybierz inną!")
                return render_template("index.html", tracked_links=tracked_links)
    return render_template("index.html", tracked_links=tracked_links)

def create_product(file: dict, new_url: str):
    file[new_url] = {
        "content": check_link_changes(new_url),
        "changed": False,
        "check_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


@app.route("/delete/<path:url>")
def delete_product(url):
    tracked_links = load_data()
    if url in tracked_links:
        del tracked_links[url]
        save_data(tracked_links)
    return redirect(url_for("index"))

@app.route("/check/<path:url>")
def check_on_demand(url):
    check_link_changes(url)
    # Have to add new function for compare only specific link with data from check_link_changes
    return redirect(url_for("index"))


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


class Domains:
    DOMAIN_TO_SCRAPER = {
        "answear.com": Checker.check_answear_com,
        "leecooper": Checker.check_leecooper,
        "ewozki.eu": Checker.check_ewozki,
        "wrangler.com": Checker.check_wrangler,
        "zalando.pl": Checker.check_zalando,
    }

    @classmethod
    def domain_validator(cls, url: str):
        for domain, scraper in Domains.DOMAIN_TO_SCRAPER.items():
            if domain in url:
                return True
        return False


if __name__ == "__main__":
    tracking_thread = threading.Thread(target=track_links, daemon=True)
    tracking_thread.start()
    app.run(debug=True, host="0.0.0.0")
