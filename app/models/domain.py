from app.models.checker import Checker


class Domain:
    DOMAIN_TO_SCRAPER = {
        "answear.com": Checker.check_answear_com,
        "leecooper": Checker.check_leecooper,
        "ewozki.eu": Checker.check_ewozki,
        "wrangler.com": Checker.check_wrangler,
        "zalando.pl": Checker.check_zalando,
    }

    @classmethod
    def domain_validator(cls, url: str):
        for domain, scraper in Domain.DOMAIN_TO_SCRAPER.items():
            if domain in url:
                return True
        return False
