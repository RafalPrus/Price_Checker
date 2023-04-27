from app.controllers.index_controller import (
    index_controller,
    check_on_demand_controller,
    delete_product_controller,
)
import threading
from flask import Flask
from app.models.repositories.repositories import load_data
from app.models.utils import track_links
from config import secret_key

app = Flask(__name__, template_folder="app/views/templates")
app.config["SECRET_KEY"] = secret_key
tracked_links = load_data()


@app.route("/", methods=["GET", "POST"])
def index():
    return index_controller()


@app.route("/delete/<path:url>")
def delete_product(url):
    return delete_product_controller((url))


@app.route("/check/<path:url>")
def check_on_demand(url):
    return check_on_demand_controller(url)


if __name__ == "__main__":
    tracking_thread = threading.Thread(target=track_links, daemon=True)
    tracking_thread.start()
    app.run(debug=True, host="0.0.0.0")
