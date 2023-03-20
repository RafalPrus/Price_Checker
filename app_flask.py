import time
import threading
from bs4 import BeautifulSoup
import requests
from flask import Flask, render_template, request, redirect, url_for
from config import email_sender, password_sender
import smtplib
import json
import os

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
        r = requests.get(url)
        r.raise_for_status()
        content = BeautifulSoup(r.text, "html.parser").find_all()
        for line in content:
            if 'cena' in line.text.lower():
                if 'pln' or 'zł' in line.text.lower():
                    if 'podobne' or 'powiązane' or 'dla ciebie' not in line.text.lower():
                        content = line.text
                        break
        return content

    except Exception as e:
        print(f"Error checking link {url}: {e}")
        return None


def track_links():
    while True:
        for url, data in tracked_links.items():
            content = check_link_changes(url)
            if content and content != data["content"]:
                data["content"] = content
                data["changed"] = True
                send_email(url, email_sender, password_sender)
                print(f"Link {url} content has changed!")
                save_data(tracked_links)
        time.sleep(15)



@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        if url:
            tracked_links[url] = {"content": check_link_changes(url), "changed": False}
            save_data(tracked_links)
            return redirect(url_for("index"))
    return render_template("index.html", tracked_links=tracked_links)


@app.route("/delete/<path:url>")
def delete(url):
    if url in tracked_links:
        del tracked_links[url]
    return redirect(url_for("index"))

def send_email(url, email_sender, password_sender, subject='Link się zmienił!', body='Jakiś link się zmienił', to_email=email_sender):
   from_email = email_sender
   password = password_sender


   msg = f'Subject: {subject}\n\n{body}\n{url}'.encode('UTF-8')
   server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
   server.login(from_email, password)
   server.sendmail(from_email, to_email, msg)
   server.quit()



if __name__ == "__main__":
    tracking_thread = threading.Thread(target=track_links, daemon=True)
    tracking_thread.start()
    app.run(debug=True)
