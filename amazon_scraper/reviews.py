from __future__ import absolute_import
import re
try:
    import urlparse
except:
    import urllib.parse as urlparse
import warnings
from bs4 import BeautifulSoup
from amazon_scraper import (
    get,
    review_url,
    reviews_url,
    extract_review_id,
    extract_reviews_asin,
    extract_reviewer_id,
    dict_acceptable,
    retry,
    process_rating,
    get_review_date,
    html_parser,
    amazon_base,
)

if 'unicode' not in dir(globals()['__builtins__']):
    unicode = str


class SubReview(object):
    """
    This object is different than the one in review.py because the reviews on the
    'reviews' page have a different HTML format. Thus we must parse them differently
    """
    def __init__(self, api, soup, Id, ItemId):
        self.soup = soup.find("div", id=Id)
        if not self.soup:
            warnings.warn(
                "We were not able to find the review HTML for {} perhaps this means "
                "that the parser is broken. File a bug".format(Id)
            )
            raise ValueError()

        self.api = api
        self._asin = ItemId
        self._id = Id
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
    def name(self):
        tag = self.soup.find('a', class_=re.compile('author'))
        if tag:
            return tag.text

    @property
    def user_id(self):
        return extract_reviewer_id(self.user_reviews_url)

    def user_reviews(self):
        return self.api.user_reviews(URL=self.user_reviews_url)

    @property
    def user_reviews_url(self):
        """
        Get the page pointing to the user's reviews
        """
        user_reviews_url = self.soup.find("a", class_=re.compile("author"))
        if user_reviews_url:
            tmp_url = urlparse.urljoin(amazon_base, user_reviews_url.attrs["href"])
            return tmp_url.replace("pdp", "cdp").replace("profile", "member-reviews")

    @property
    def date(self):
        date = self.soup.find("span", class_=re.compile("review-date"))
        if date:
            return get_review_date(date.text)

    @property
    def id(self):
        return self._id

    @property
    def rating(self):
        rating = self.soup.find("i", class_=re.compile("review-rating"))
        if rating:
            return process_rating(rating.text)

    @property
    def title(self):
        tag = self.soup.find('a', class_=re.compile('review-title'))
        if tag:
            return tag.text

    @property
    def text(self):
        tag = self.soup.find('a', class_=re.compile('review-text'))
        if tag:
            return tag.text

    @property
    def url(self):
        return self._url

    def to_dict(self):
        return {
            "asin": self.asin,
            "name": self.name,
            "user_id": self.user_id,
            "user_reviews_url": self.user_reviews_url,
            "date": self.date,
            "id": self.id,
            "rating": self.rating,
            "text": self.text,
            "title": self.title,
            "url": self.url,
        }

    def full_review(self):
        return self.api.review(self.id)


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

        self.api = api
        self._URL = URL
        self._soup = None

    @property
    @retry()
    def soup(self):
        if not self._soup:
            r = get(self.url, self.api)
            self._soup = BeautifulSoup(r.text, html_parser)
        return self._soup

    def full_reviews(self):
        page = self
        while page:
            for review_id in page.ids:
                yield self.api.review(Id=review_id)
            page = Reviews(page.api, URL=page.next_page_url) if page.next_page_url else None

    @property
    def brief_reviews(self):
        for review_id in self.ids:
            yield SubReview(self.api, self.soup, review_id, self.asin)

    def __iter__(self):
        page = self
        while page:
            for r in page.brief_reviews:
                yield r
            page = Reviews(page.api, URL=page.next_page_url) if page.next_page_url else None

    @property
    def asin(self):
        return extract_reviews_asin(self.url)

    @property
    def url(self):
        return self._URL

    @property
    def next_page_url(self):
        # lazy loading causes this to differ from the HTML visible in chrome
        anchor = self.soup.find('a', href=re.compile(r'product-reviews.*next', flags=re.I))
        if not anchor:
            for a in self.soup.find_all('a', href=re.compile(r'product-reviews', flags=re.I)):
                if 'next' in a.text.lower():
                    anchor = a
                    break
        if anchor:
            return urlparse.urljoin(amazon_base, unicode(anchor['href']))
        return None

    @property
    def ids(self):
        return [
            anchor["id"]
            for anchor in self.soup.find_all('div', class_="review")
        ]

    @property
    def urls(self):
        return [
            review_url(id)
            for id in self.ids
        ]

    def product(self):
        return self.api.product(ItemId=self.asin)

    def to_dict(self):
        d = {
            k: getattr(self, k)
            for k in dir(self)
            if dict_acceptable(self, k, blacklist=['soup', '_URL', '_soup', 'product'])
        }
        return d
