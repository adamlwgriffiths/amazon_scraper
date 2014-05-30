# -*- coding: utf-8 -*-
from __future__ import absolute_import
import re
import urlparse
import urllib
import functools
import time
from HTMLParser import HTMLParser
from amazon.api import AmazonAPI
from bs4 import BeautifulSoup


_extract_asin_regexp = re.compile(r'/dp/(?P<asin>[^/]+)')
def extract_asin(url):
    match = _extract_asin_regexp.search(url)
    return str(match.group('asin'))

def product_url(asin):
    url = 'http://www.amazon.com/dp/{asin}'
    return url.format(asin=asin)

def add_affiliate(url, affiliate):
    return add_query(url, tag=affiliate)

def reviews_url(asin):
    url = 'http://www.amazon.com/product-reviews/{asin}/ref=cm_cr_pr_top_sort_recent?&sortBy=bySubmissionDateDescending'
    return url.format(asin=asin)

def review_url(id):
    url = 'http://www.amazon.com/review/{id}'
    return url.format(id=id)

_process_rating_regexp = re.compile(r'([\d\.]+) out of [\d\.]+ stars', flags=re.I)
def process_rating(text):
    """The rating normalised to 1.0
    """
    rating_match = _process_rating_regexp.search(text)
    return float(rating_match.group(1)) / 5.0

_extract_review_id_regexp = re.compile(r'/review/(?P<id>[^/]+)', flags=re.I)
def extract_review_id(url):
    match = _extract_review_id_regexp.search(url)
    return str(match.group('id'))

_price_regexp = re.compile(ur'(?P<price>[$£][\d,\.]+)', flags=re.I)
def extract_price(text):
    match = _price_regexp.search(text)
    price = match.group('price')
    price = re.sub(ur'[$£,]', u'', price)
    price = float(price)
    return price

def add_query(url, **kwargs):
    scheme, netloc, path, query_string, fragment = urlparse.urlsplit(url)
    query_params = urlparse.parse_qs(query_string)
    # remove any existing value of 'key'
    keys = kwargs.keys()
    query_params = dict(filter(lambda x: x[0] not in keys, query_params.iteritems()))
    query_params.update(kwargs)
    query_string = urllib.urlencode(query_params, doseq=True)
    return urlparse.urlunsplit((scheme, netloc, path, query_string, fragment))

def strip_html_tags(html):
    if html:
        soup = BeautifulSoup(html)
        text = soup.findAll(text=True)
        text = u'\n'.join(text).strip()
        return text
    return None

def retry(retries=5, delay=1.2, exceptions=None):
    original_delay = delay
    delay_increment = 1.0
    # store in a list so our closure can access it
    delay = [delay]
    if not exceptions:
        exceptions = (BaseException,)

    def outer(fn):
        @functools.wraps(fn)
        def decorator(*args, **kwargs):
            for attempt in range(1, retries + 1):
                try:
                    if attempt > 1:
                        print '{0}({1}, {2}) - Retry attempt {3}/{4}'.format(fn.__name__, args, kwargs, attempt, retries)
                    result = fn(*args, **kwargs)
                    # reset our delay on a success
                    delay[0] = original_delay
                    return result
                except BaseException as e:
                    if not isinstance(e, exceptions):
                        raise
                    if attempt >= retries:
                        print '{0}({1}, {2}) - Retry limit exceeded'.format(fn.__name__, args, kwargs)
                        raise e
                    time.sleep(delay[0])
                    # wait longer next time
                    delay[0] += delay_increment  * attempt
        return decorator
    return outer

"""
def strip_html_tags(html):
    class MLStripper(HTMLParser):
        def __init__(self):
            self.reset()
            self.fed = []

        @property
        def type(self):
            if self.fed:
                return type(self.fed[0])
            return None
            
        def handle_starttag(self, tag, attrs):
            if self.type:
                if tag == self.type('br'):
                    self.fed.append(self.type('\n'))
            HTMLParser.handle_starttag(self, tag, attrs)

        def handle_startendtag(self, tag, attrs):
            if self.type:
                if tag == self.type('br'):
                    self.fed.append(self.type('\n'))
            HTMLParser.handle_startendtag(self, tag, attrs)

        def handle_data(self, d):
            t = self.type or type(d)
            self.fed.append(t(d))

        def handle_entityref(self, name):
            self.fed.append('&%s;' % name)

        def get_data(self):
            data = ''
            if self.type:
                data = self.type(' ').join(self.fed)
                data = re.sub(ur'( )+', self.type(' '), data)
            return data

    s = MLStripper()
    # unescape any html chars
    # ie: in the blurb for http://www.amazon.com/dp/1491268727
    # the word unicode ' in R'lyeh (R&#x2019;lyeh) gets stripped unless we escape it first
    html = s.unescape(html)
    s.feed(html)
    #Shrink multiple \n into paragraph spacing.
    data = s.get_data()
    data = data.split(s.type('\n'))
    data = map(lambda d: d.strip(), data)
    data = filter(bool, data)
    return s.type('\n\n').join(data).strip()
"""

def is_property(obj, k):
    # only accept @property decorated functions
    # these can only be detected via the __class__ object
    if hasattr(obj.__class__, k):
        if isinstance(getattr(obj.__class__, k), property):
            return True
    return False

def dict_acceptable(obj, k, blacklist=None):
    if blacklist and k in blacklist:
        return False
    return is_property(obj, k)


from amazon_scraper.product import Product
from amazon_scraper.reviews import Reviews
from amazon_scraper.review import Review


class AmazonScraper(object):
    def __init__(self, access_key, secret_key, associate_tag, *args, **kwargs):
        self.api = AmazonAPI(access_key, secret_key, associate_tag, *args)

    def reviews(self, ItemId=None, URL=None):
        return Reviews(ItemId, URL)

    def review(self, Id=None, URL=None):
        return Review(Id, URL)

    def lookup(self, URL=None, **kwargs):
        if URL:
            kwargs['ItemId'] = extract_asin(URL)

        result = self.api.lookup(**kwargs)
        if isinstance(result, (list, tuple)):
            result = [Product(p) for p in result]
        else:
            result = Product(result)
        return result

    def similarity_lookup(self, **kwargs):
        for p in self.api.similarity_lookup(**kwargs):
            yield Product(p)

    def browse_node_lookup(self, **kwargs):
        return self.api.browse_node_lookup(**kwargs)

    def search(self, **kwargs):
        for p in self.api.search(**kwargs):
            yield Product(p)

    def search_n(self, n, **kwargs):
        for p in self.api.search_n(n, **kwargs):
            yield Product(p)

