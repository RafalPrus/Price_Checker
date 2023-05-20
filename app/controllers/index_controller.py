from flask import request, url_for, redirect, flash, render_template
from app.models.domain import Domain
from app.models.repositories.repositories import load_data, save_data
from app.models.utils import create_product, track_separate_link, clear_changed_status, load_images


def index_controller():
    tracked_links = load_data()
    images = load_images()
    if request.method == "POST":
        url = request.form.get("url")
        if url:
            if Domain.domain_validator(url):
                updated_links = create_product(tracked_links, url)
                save_data(updated_links)
                return redirect(url_for("index"))
            else:
                flash("We are sorry, this store is not supported.")
                return render_template("index.html", tracked_links=tracked_links)
    return render_template("index.html", tracked_links=tracked_links, images=images)


def check_on_demand_controller(url):
    track_separate_link(url)
    return redirect(url_for("index"))

def clear_on_demand_controller(url):
    clear_changed_status(url)
    return redirect(url_for("index"))


def delete_product_controller(url):
    tracked_links = load_data()
    if url in tracked_links:
        del tracked_links[url]
        save_data(tracked_links)
    return redirect(url_for("index"))
