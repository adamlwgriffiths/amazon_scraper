from __future__ import absolute_import
import re
from urlparse import urljoin

from bs4 import BeautifulSoup
import requests

from amazon_scraper import (
    get_review_date,
    retry,
    review_url,
    user_agent,
)

RATINGS_MAPPING = {
    "1.0 out of 5 stars": 0.2,
    "2.0 out of 5 stars": 0.4,
    "3.0 out of 5 stars": 0.6,
    "4.0 out of 5 stars": 0.8,
    "5.0 out of 5 stars": 1.0
}


class ReviewerListedReview(object):
    """
    Because individual reviews on the reviewer's list of reviews are difficult to parse we need to
    sift out most of the information needed in the main Reviewer class and then send it here when
    we find the HTML we need.
    """
    def __init__(self, soup, asin, author, id_, reviewer_profile_url):
        self._asin = asin
        self._author = author
        self._date = None
        self._id = id_
        self._rating = None
        self._text = None
        self._title = None
        self._soup = soup
        self._review_url = None
        self._reviewer_profile_url = reviewer_profile_url

    @property
    def asin(self):
        return self._asin

    @property
    def author(self):
        return self._author

    @property
    def author_reviews_url(self):
        return self._reviewer_profile_url

    @property
    def date(self):
        if not self._date:
            date_tag = self._soup.find("nobr")
            self._date = get_review_date(date_tag.text)
        return self._date

    @property
    def id(self):
        return self._id

    @property
    def rating(self):
        if not self._rating:
            rating_tag = self._soup.find("img", attrs={"title": re.compile("out of 5 stars")})
            self._rating = RATINGS_MAPPING[rating_tag.attrs["title"]]
        return self._rating

    @property
    def soup(self):
        return self._soup

    @property
    def text(self):
        if not self._text:
            self._text = self._soup.find("div", class_="reviewText").text
        return self._text

    @property
    def title(self):
        if not self._title:
            self._title = self._soup.find("b").text
        return self._title

    @property
    def url(self):
        if not self._review_url:
            self._review_url = review_url(self._id)
        return self._review_url

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


class Reviewer(object):
    """
    Scrape reviews from a specific reviewer given the URL of all of their
    amazon reviews

    :param url: A url pointing to the reviewer's cdp/member-reviews list
    """
    def __init__(self, URL):
        if not (isinstance(URL, str) or isinstance(URL, unicode)):
            raise ValueError(
                "Our url {} cannot be of type {}. It must be a string".
                format(URL, type(URL))
            )
        if "cdp/member-reviews" not in URL:
            raise ValueError(
                "We cannot parse reviews that are not on a users' cdp/member-reviews page"
            )
        self._all_reviews = []
        self._author = None
        self._next_page_url = None
        self._url = URL
        self._soup = None

    @property
    @retry()
    def soup(self):
        if not self._soup:
            r = requests.get(self.url, headers={"User-Agent": user_agent})
            r.raise_for_status()
            self._soup = BeautifulSoup(r.text, "html5lib")
        return self._soup

    @property
    def author(self):
        if not self._author:
            # This feels fragile but a text search didnt work unfortunately
            author_tag = self.soup.find("b", class_="h1")
            # rstrip the author text just to be safe
            self._author = re.search(r"Written by\s*(.+)\s\n", author_tag.text).groups()[0].rstrip()
        return self._author

    @property
    def next_page_url(self):
        def check_for_next_page(tag):
            if not tag:
                self._next_page_url = None
            else:
                self._next_page_url = urljoin("http://amazon.com", tag.attrs["href"])

        if not self._next_page_url:
            generic_page_regex = re.compile(r"page=(\d{1,})")
            current_page = generic_page_regex.search(self.url)
            if not current_page:  # We are either on page 1 or there is no review pagination
                # Look for page 2. If there is none then there are no more review pages
                second_page = self.soup.find("a", attrs={"href": re.compile(r"page=2")})
                check_for_next_page(second_page)
            else:  # We are on some page > 1
                page_number = int(current_page.groups()[0])
                next_page = self.soup.find(
                    "a", attrs={"href": re.compile(r"page={}".format(page_number + 1))}
                )
                check_for_next_page(next_page)
        return self._next_page_url

    @property
    def reviewer_id(self):
        return re.search(self.url, "member-reviews\/([A-Z0-9]+)\/").groups()[0]

    @property
    def url(self):
        return self._url

    @property
    def all_reviews(self):
        """
        Parse all reviews created by the reviewer on the specific page.

        There seem to be two HTML 'chunks' for a review. One is a part that includes the
        review id and all other relevant information for the review like rating, title, and
        text. The other is the product description which ends up above the actual review
        information. We must parse both of these parts.

        The product information is parsed for its asin, and then the review part is found
        and then sent to the `ReviewerListedReview` object for further parsing.
        """
        if self._all_reviews:
            return self._all_reviews

        # First get all review ids on the page
        ids = self.soup.find_all("a", attrs={"name": re.compile(r"[A-Z0-9]{13}")})
        for id_ in ids:
            id_str  = id_.attrs["name"]
            review_soup = id_.findParent()
            asin_regex = re.compile(r"dp\/([A-Z0-9]{10})")
            # Get the soup of the full review (Item photo and description included) and get the
            # product's asin
            full_review_soup = review_soup.findParent().findParent()
            asin_tag = full_review_soup.find("a", attrs={"href": asin_regex})
            asin = asin_regex.search(asin_tag.attrs["href"]).groups()[0]
            # Now get the review
            self._all_reviews.append(ReviewerListedReview(review_soup, asin, self.author, id_str, self.url))
        return self._all_reviews
