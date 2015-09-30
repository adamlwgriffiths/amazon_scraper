from __future__ import absolute_import
import re
try:
    import urlparse
except:
    import urllib.parse as urlparse
from bs4 import BeautifulSoup
from amazon_scraper import (
    get,
    review_url,
    extract_review_id,
    extract_reviewer_id,
    process_rating,
    strip_html_tags,
    dict_acceptable,
    retry,
    get_review_date,
    html_parser,
    amazon_base,
)

if 'unicode' not in dir(globals()['__builtins__']):
    unicode = str


class Review(object):
    def __init__(self, api, Id=None, URL=None):
        if Id and not URL:
            if 'amazon' in Id:
                raise ValueError('URL passed as ID')

            URL = review_url(Id)

        if not URL:
            raise ValueError('Invalid review page parameters')

        self.api = api
        self._URL = URL
        self._id = extract_review_id(URL)
        self._soup = None

    @property
    @retry()
    def soup(self):
        if not self._soup:
            r = get(self.url, self.api)
            self._soup = BeautifulSoup(r.text, html_parser)
        return self._soup

    @property
    def id(self):
        #anchor = self.soup.find('a', attrs={'name': True}, text=False)
        #id_ = unicode(anchor['name'])
        #return id_
        return self._id

    @property
    def asin(self):
        tag = self.soup.find('abbr', class_='asin')
        asin = unicode(tag.string)
        return asin

    @property
    def url(self):
        return review_url(self.id)

    @property
    def title(self):
        tag = self.soup.find('span', class_='summary')
        title = unicode(tag.string)
        return title.strip()

    @property
    def rating(self):
        """The rating of the product normalised to 1.0
        """
        for li in self.soup.find_all('li', class_='rating'):
            # get the second string
            string = next(li.stripped_strings).lower()
            if 'overall:' not in string:
                continue

            img = li.find('img')
            rating = unicode(img['title'])
            return process_rating(rating)

    @property
    def date(self):
        abbr = self.soup.find('abbr', class_='dtreviewed')
        return get_review_date(abbr["title"])

    @property
    def user(self):
        vcard = self.soup.find('span', class_='reviewer vcard')
        if vcard:
            tag = vcard.find(class_='fn')
            if tag:
                user = unicode(tag.string)
                return user
        return None

    @property
    def user_id(self):
        url = self.user_reviews_url
        if url:
            return extract_reviewer_id(url)

    def user_reviews(self):
        url = self.user_reviews_url
        if url:
            return self.api.user_reviews(URL=url)

    @property
    def user_reviews_url(self):
        vcard = self.soup.find('span', class_='reviewer vcard')
        if vcard:
            anchor = vcard.find('a', href=re.compile(r'/pdp/'))
            if anchor:
                path = anchor.attrs['href']
                path = path.replace('/pdp/', '/cdp/')
                path = path.replace('/profile/', '/member-reviews/')
                return urlparse.urljoin(amazon_base, path)

    @property
    def text(self):
        tag = self.soup.find('span', class_='description')
        return strip_html_tags(unicode(tag))

    def product(self):
        return self.api.product(ItemId=self.asin)

    def to_dict(self):
        d = {
            k: getattr(self, k)
            for k in dir(self)
            if dict_acceptable(self, k, blacklist=['soup', '_URL', '_soup'])
        }
        return d
