from bs4 import BeautifulSoup
import cloudscraper


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
        print(f"typ wozki: ")
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
