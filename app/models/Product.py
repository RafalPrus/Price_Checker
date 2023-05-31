from app.models.domain import Domain
from flask import flash


class SingleProduct:

    def __init__(self):
        self._url: None

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        if Domain.domain_validator(url):
            self._url = url
        else:
            flash("We are sorry, this store is not supported.")



