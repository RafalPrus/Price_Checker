import time
from datetime import datetime
import threading
from bs4 import BeautifulSoup
import requests
from flask import Flask, render_template, request, redirect, url_for
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
        json.dump(data, f)



app = Flask(__name__)
tracked_links = load_data()



def check_link_changes(url):
    try:
        if 'wrangler.com' in url:
            r = scrap_wrangler(url)
            r.raise_for_status()
        else:
            r = requests.get(url)
            r.raise_for_status()
        if 'answear.com' in url:
            content = check_answear_com(r)
        elif 'leecooper' in url:
            content = check_leecooper(r)
        elif 'ewozki.eu' in url:
            content = check_ewozki(r)
        elif 'wrangler.com' in url:
            content = check_wrangler(r)

        return content

    except Exception as e:
        print(f"Error checking link {url}: {e}")
        return None

def check_answear_com(source):
    content = BeautifulSoup(source.content, "html.parser")
    return content.find('div', {'class': 'ProductCard__priceWrapper__Tyf2d'}).text

def check_leecooper(source):
    content = BeautifulSoup(source.content, "html.parser")
    return content.find('div', {'class': 'product_info'}).text

def check_ewozki(source):
    content = BeautifulSoup(source.content, "html.parser")
    return content.find('div', {'class': 'price-available'}).text

def check_wrangler(source):
    content = BeautifulSoup(source.content, "html.parser")
    return content.find('div', {'class': 'pdp-detail'}).text


def scrap_wrangler(url):
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    return scraper.get(url)


def track_links():
    while True:
        iteration = load_data().copy()
        for url, data in iteration.items():
            content = check_link_changes(url)
            if content and content != data["content"]:
                send_email(url, email_sender, password_sender, content, data["content"])
                data["content"] = content
                data["changed"] = True
                print(f"Link {url} content has changed!")
                iteration[url] = data
            data['last_check_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if 'counter' in data:
                new_data = data['counter'] + 1
                data['counter'] = new_data
            else:
                data['counter'] = 1
            save_data(iteration)
        time.sleep(600)



@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        if url:
            tracked_links = load_data()
            tracked_links[url] = {"content": check_link_changes(url), "changed": False, 'check_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            save_data(tracked_links)
            return redirect(url_for("index"))
    tracked_links = load_data()
    return render_template("index.html", tracked_links=tracked_links)


@app.route("/delete/<path:url>")
def delete(url):
    tracked_links = load_data()
    if url in tracked_links:
        del tracked_links[url]
        save_data(tracked_links)
    return redirect(url_for("index"))

def send_email(url, email_sender, password_sender, old_content, new_content, subject='Link się zmienił!', body='Jakiś link się zmienił'):
    print('----------------1  w email! --------------------')
    email = email_sender
    password = password_sender
    body = body + f'Poprzednie wartosci: \n' + old_content + f'\nNowe wartości: \n' + new_content
    msg = f'Subject: {subject}\n\n{body}\n{url}'.encode('UTF-8')
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(email, password)
    server.sendmail(email, email, msg)
    server.quit()




if __name__ == "__main__":
    tracking_thread = threading.Thread(target=track_links, daemon=True)
    tracking_thread.start()
    app.run(debug=True, host='0.0.0.0')
