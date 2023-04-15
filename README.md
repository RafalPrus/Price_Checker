# Price_Checker
Application for tracking price changes of specific products on submitted subpages and informing about changes on the product page via email notifications.

[![Python Version](https://img.shields.io/badge/python-3.10.6-blue.svg)](https://www.python.org/downloads/release/python-3.10.6/)


## Getting Started
To use this tool, you will need to have Python 3.6 or higher installed on your system. Once you have those installed, clone this repository by running the following command in your terminal
```bash
git clone https://github.com/RafalPrus/Price_Checker.git
```
Then, install all necessary dependencies with:
```bash
pip install -r requirements.txt
```

## Usage
To use this app you need to create file config.py with:
```bash
email_sender = 'sender_email_adress@example.com'
email_s_password = 'example'
email_recipient = 'recipient_email_adress@example.com'
email_r_password = 'example'
```

After creating the config.py file with your own data, run the app_flask.py file. To start using the program, simply enter the following address in your browser window:
http://127.0.0.1:5000

Now you can add new products whose prices you want to monitor using the "URL to track" form:
<URL form image>

The program will automatically check every hour whether the price of a given product has changed. If so, you will receive an email notification immediately to the address provided in the config.py file. Additionally, in the application window, on the right side, the information "Changed!" will be displayed, highlighting products whose prices have changed since adding the product for tracking:
<Changed! image>

Using the "details" button, you can display more information about tracking a particular product. This information includes, among others: the date the product was added for tracking, the current price, the new price (if there has been a change), and a few others:
<details_product image>

## Todo
- [ ] Add clear button for changed prodtucts
- [ ] Add clear details button
- [ ] Add button for signle force price check
- [ ] Add screenshots to the README.md that will help understand how to prepare folders with products.
- [ ] Add Polish README.md
