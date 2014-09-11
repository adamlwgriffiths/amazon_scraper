from __future__ import absolute_import
import re
import requests
from bs4 import BeautifulSoup
from amazon_scraper import review_url, reviews_url, extract_review_id, dict_acceptable, retry, rate_limit, extract_reviews_id, user_agent


class Reviews(object):
    def __init__(self, api, ItemId=None, URL=None):
        if ItemId and not URL:
            # check for http://www.amazon.com
            if 'amazon' in ItemId:
                raise ValueError('URL passed as ASIN')

            URL = reviews_url(ItemId)
        else:
            if URL:
                # cleanup the url
                URL = reviews_url(extract_reviews_id(URL))                
        if not URL:
            raise ValueError('Invalid review page parameters')

        self.api = api
        self._URL = URL
        self._soup = None

    @property
    @retry()
    def soup(self):
        if not self._soup:
            rate_limit(self.api)
            r = requests.get(self._URL, headers={'User-Agent':user_agent}, verify=False)
            r.raise_for_status()
            # fix #1
            # 'html.parser' has trouble with http://www.amazon.com/product-reviews/B00008MOQA/ref=cm_cr_pr_top_sort_recent?&sortBy=bySubmissionDateDescending
            # it sometimes doesn't find the asin span
            #self._soup = BeautifulSoup(r.text, 'html.parser')
            self._soup = BeautifulSoup(r.text, 'html5lib')
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
