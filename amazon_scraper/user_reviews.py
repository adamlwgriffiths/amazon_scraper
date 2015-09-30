from __future__ import absolute_import
import re
try:
    import urlparse
except:
    import urllib.parse as urlparse
from bs4 import BeautifulSoup
from amazon_scraper import (
    get,
    get_review_date,
    retry,
    review_url,
    reviewer_url,
    extract_asin,
    extract_reviewer_id,
    html_parser,
    process_rating,
    amazon_base,
)

if 'unicode' not in dir(globals()['__builtins__']):
    unicode = str


class UserReviewsSubReview(object):
    """
    Because individual reviews on the reviewer's list of reviews are difficult to parse we need to
    sift out most of the information needed in the main UserReview class and then send it here when
    we find the HTML we need.
    """
    def __init__(self, api, reviewer, soup, id):
        self.api = api
        self._soup = soup
        self._reviewer = reviewer
        self._id = id

    @property
    def asin(self):
        asin_tag = self.soup.find('a', href=re.compile(r'dp/([^/]+)'))
        return extract_asin(asin_tag.attrs['href'])

    @property
    def author(self):
        return self._reviewer.author

    @property
    def author_reviews_url(self):
        return self._reviewer.url

    @property
    def author_id(self):
        return extract_reviewer_id(self._reviewer.url)

    @property
    def date(self):
        #date_tag = self.soup.find('nobr')
        date_tag = self.soup.find(class_='review-date')
        return get_review_date(date_tag.text)

    @property
    def id(self):
        return self._id

    @property
    def rating(self):
        rating_tag = self.soup.find('img', title=re.compile(r'out of \d stars'))
        return process_rating(rating_tag.attrs['title'])

    @property
    def soup(self):
        return self._soup

    @property
    def text(self):
        return self.soup.find('div', class_='reviewText').text

    @property
    def title(self):
        return self.soup.find('b').text

    @property
    def url(self):
        return review_url(self._id)

    def full_review(self):
        return self.api.review(Id=self.id)

    def to_dict(self):
        return {
            'asin': self.asin,
            'author': self.author,
            'author_id': self.author_id,
            'author_reviews_url': self.author_reviews_url,
            'date': self.date,
            'id': self.id,
            'rating': self.rating,
            'text': self.text,
            'title': self.title,
            'url': self.url,
        }


class UserReviews(object):
    """
    Scrape reviews from a specific reviewer given the URL of all of their
    amazon reviews

    :param url: A url pointing to the reviewer's cdp/member-reviews list
    """
    def __init__(self, api, Id=None, URL=None):
        if Id and not URL:
            URL = reviewer_url(Id)
        elif URL and not Id:
            Id = extract_reviewer_id(URL)

        if not Id and not URL:
            raise ValueError('Must provide either an Id or a URL')

        if 'cdp/member-reviews' not in URL:
            raise ValueError('We cannot parse reviews that are not on a users "cdp/member-reviews" page')

        self.api = api
        self._id = Id
        self._url = URL
        self._soup = None

    @property
    @retry()
    def soup(self):
        if not self._soup:
            r = get(self.url, self.api)
            self._soup = BeautifulSoup(r.text, html_parser)
        return self._soup

    @property
    def name(self):
        # This feels fragile but a text search didnt work unfortunately
        author_tag = self.soup.find('b', class_='h1')
        match = re.search(r'written by\s*(?P<name>.+)\s\n', author_tag.text, flags=re.I)
        if match:
            return match.group('name').strip()

    @property
    def next_page_url(self):
        match = re.search(r'[\?&]page=(?P<page>[\d]+)', self.url)
        page_number = 1
        if match:
            page_number = int(match.group('page'))
        page_number += 1
        next_page_tag = self.soup.find('a', href=re.compile(r'page=\d+'), text=page_number)

        if next_page_tag:
            return urlparse.urljoin(amazon_base, next_page_tag.attrs['href'])

    @property
    def id(self):
        return extract_reviewer_id(self.url)

    @property
    def url(self):
        return self._url

    @property
    def brief_reviews(self):
        """Parse all reviews created by the reviewer on the specific page.
        """
        ids = self.soup.find_all('a', attrs={'name': re.compile(r'/review/[^/]+')})
        for id_tag in ids:
            id_ = id_tag.attrs['name']
            soup = id_tag.findParent('tr', valign='top')
            yield UserReviewsSubReview(self.api, self, soup, id_)

    def ids(self):
        # First get all review ids on the page
        ids = self.soup.find_all('a', attrs={'name': re.compile(r'/review/[^/]+')})
        for id_tag in ids:
            yield id_tag.attrs['name']

    def __iter__(self):
        page = self
        while page:
            for r in page.brief_reviews:
                yield r
            page = self.api.user_reviews(URL=page.next_page_url) if page.next_page_url else None

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
        }
