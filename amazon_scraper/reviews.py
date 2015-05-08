from __future__ import absolute_import
import re
from urlparse import urljoin
import warnings

import requests
from bs4 import BeautifulSoup

from amazon_scraper import (
    review_url,
    reviews_url,
    extract_review_id,
    dict_acceptable,
    retry,
    rate_limit,
    extract_reviews_id,
    user_agent,
    get_review_date,
)


class SubReview(object):
    """
    This object is different than the one in review.py because the reviews on the
    'reviews' page have a different HTML format. Thus we must parse them differently
    """
    def __init__(self, reviews_soup, review_id, product_asin):
        self.soup = reviews_soup.find("div", id=review_id)
        if not self.soup:
            warnings.warn(
                "We were not able to find the review HTML for {} perhaps this means "
                "that the parser is broken. File a bug".format(review_id)
            )
            raise ValueError()

        self._asin = product_asin
        self._author = None
        self._author_reviews_url = None
        self._date = None
        self._rating = None
        self._text = None
        self._title = None
        self._id = review_id
        self._url = review_url(self._id)

    def _parse_generic_property(self, var, tag, regex_term):
        if not var:
            tmp = self.soup.find(tag, class_=re.compile(regex_term))
            if tmp:
                var = tmp.text
            else:
                var = tmp
        return var

    @property
    def asin(self):
        return self._asin

    @property
    def author(self):
        return self._parse_generic_property(self._author, "a", "author")

    @property
    def author_reviews_url(self):
        """
        Get the page pointing to the author's reviews
        """
        if not self._author_reviews_url:
            author_reviews_url = self.soup.find("a", class_=re.compile("author"))
            if author_reviews_url:
                tmp_url = urljoin("http://amazon.com", author_reviews_url.attrs["href"])
                self._author_reviews_url = tmp_url.replace("pdp", "cdp").replace("profile", "member-reviews")
            else:
                self._author_reviews_url = author_reviews_url
        return self._author_reviews_url

    @property
    def date(self):
        if not self._date:
            date = self.soup.find("span", class_=re.compile("review-date"))
            if date:
                self._date = get_review_date(date.text)
            else:
                self._date = date
        return self._date

    @property
    def id(self):
        return self._id

    @property
    def rating(self):
        if not self._rating:
            rating = self.soup.find("i", class_=re.compile("review-rating"))
            if rating:
                # normalize this to what we do in the Review class
                self._rating = int(rating.text) / 5.0
            else:
                self._rating = rating
        return self._rating

    @property
    def title(self):
        return self._parse_generic_property(self._title, "a", "review-title")

    @property
    def text(self):
        return self._parse_generic_property(self._text, "span", "review-text")

    @property
    def url(self):
        return self._url

    def to_dict(self):
        return {
            "asin": self.asin,
            "author": self.author,
            "author_reviews_url": self.author_reviews_url,
            "date": self.date,
            "id": self.id,
            "rating": self.rating,
            "text": self.text,
            "title": self.title,
            "url": self.url,
        }


class Reviews(object):
    def __init__(self, api, ItemId=None, URL=None):
        self._asin = None
        if ItemId and not URL:
            # check for http://www.amazon.com
            if 'amazon' in ItemId:
                raise ValueError('URL passed as ASIN')

            URL = reviews_url(ItemId)
        elif not URL and not ItemId:
            raise ValueError('Invalid review page parameters. Input a URL or a valid ASIN!')
        elif URL and 'product-reviews' not in URL:  # If product-reviews is in the url it's probably a valid product review page. Let it be.
            # cleanup the url
            URL = reviews_url(extract_reviews_id(URL))

        self._asin = re.search(r"\/product-reviews\/(\w+)\/", URL).groups()[0]
        self._all_reviews = []
        self.api = api
        self._URL = URL
        self._soup = None

    @property
    def all_reviews(self):
        if self._all_reviews:
            return self._all_reviews

        for review_id in self.ids:
            try:
                review = SubReview(self.soup, review_id, self.asin)
            except ValueError:
                continue
            self._all_reviews.append(review)
        return self._all_reviews

    @property
    @retry()
    def soup(self):
        if not self._soup:
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
        return self._asin

    @property
    def url(self):
        return self._URL

    @property
    def next_page_url(self):
        # lazy loading causes this to differ from the HTML visible in chrome
        anchor = self.soup.find('a', href=re.compile(r'next'))
        if anchor:
            return urljoin("http://www.amazon.com", unicode(anchor['href']))
        return None

    @property
    def ids(self):
        return [
            anchor["id"]
            for anchor in self.soup.find_all('div', class_="a-section review")
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
