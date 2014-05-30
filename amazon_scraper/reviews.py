import re
import requests
from bs4 import BeautifulSoup
from amazon_scraper import review_url, reviews_url, extract_review_id, dict_acceptable, retry


class Reviews(object):
    def __init__(self, ItemId=None, URL=None):
        if ItemId and not URL:
            # check for http://www.amazon.com
            if 'amazon' in ItemId:
                raise ValueError('URL passed as ASIN')

            URL = reviews_url(ItemId)

        if not URL:
            raise ValueError('Invalid review page parameters')

        self._URL = URL
        self._soup = None

    @property
    @retry()
    def soup(self):
        if not self._soup:
            r = requests.get(self._URL)
            r.raise_for_status()
            self._soup = BeautifulSoup(r.text, 'html.parser')
        return self._soup

    def __iter__(self):
        page = self
        while page:
            for id in page.ids:
                yield id
            page = Reviews(URL=page.next_page_url) if page.next_page_url else None

    @property
    def asin(self):
        span = self.soup.find('span', class_='asinReviewsSummary', attrs={'name':True})
        return unicode(span['name'])

    @property
    def url(self):
        return reviews_url(self.asin)

    @property
    def next_page_url(self):
        # lazy loading causes this to differ from the HTML visible in chrome
        anchor = self.soup.find('a', text=re.compile(ur'next', flags=re.I))
        if anchor:
            return unicode(anchor['href'])
        return None

    @property
    def ids(self):
        return [
            extract_review_id(anchor['href'])
            for anchor in self.soup.find_all('a', text=re.compile(ur'permalink', flags=re.I))
        ]

    @property
    def urls(self):
        return [
            review_url(id)
            for id in self.ids
        ]

    def to_dict(self):
        d = {
            k:getattr(self, k)
            for k in dir(self)
            if dict_acceptable(self, k, blacklist=['soup', '_URL', '_soup'])
        }
        return d
