from flask import request, url_for, redirect, flash, render_template
from app.models.domain import Domain
from app.models.repositories.repositories import load_data, save_data
from app.models.utils import create_product, check_link_changes


def index_controller():
    tracked_links = load_data()
    if request.method == "POST":
        url = request.form.get("url")
        if url:
            if Domain.domain_validator(url):
                updated_links = create_product(tracked_links, url)
                save_data(updated_links)
                return redirect(url_for("index"))
            else:
                flash("Niedozwolona nazwa, wybierz inną!")
                return render_template("index.html", tracked_links=tracked_links)
    return render_template("index.html", tracked_links=tracked_links)


def check_on_demand_controller(url):
    check_link_changes(url)
    # Have to add new function for compare only specific link with data from check_link_changes
    return redirect(url_for("index"))


def delete_product_controller(url):
    tracked_links = load_data()
    if url in tracked_links:
        del tracked_links[url]
        save_data(tracked_links)
    return redirect(url_for("index"))