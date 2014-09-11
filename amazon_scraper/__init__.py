# -*- coding: utf-8 -*-
from __future__ import absolute_import

# load our version
from .version import __version__

import logging
import re
import urlparse
import urllib
import functools
import time
import requests
from HTMLParser import HTMLParser
from amazon.api import AmazonAPI
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

#user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36'
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.94 Safari/537.36'

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

_extract_reviews_id_regexp = re.compile(r'/product-reviews/(?P<id>[^/]+)', flags=re.I)
def extract_reviews_id(url):
    match = _extract_reviews_id_regexp.search(url)
    return str(match.group('id'))

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

def retry(retries=5, exceptions=None):
    if not exceptions:
        exceptions = (BaseException,)

    def outer(fn):
        @functools.wraps(fn)
        def decorator(*args, **kwargs):
            for attempt in range(1, retries + 1):
                try:
                    if attempt > 1:
                        log.debug('{0}({1}, {2}) - Retry attempt {3}/{4}'.format(fn.__name__, args, kwargs, attempt, retries))
                    result = fn(*args, **kwargs)
                    return result
                except BaseException as e:
                    if not isinstance(e, exceptions):
                        raise
                    if attempt >= retries:
                        log.debug('{0}({1}, {2}) - Retry limit exceeded'.format(fn.__name__, args, kwargs))
                        raise e
        return decorator
    return outer

def is_property(obj, k):
    # only accept @property decorated functions
    # these can only be detected via the __class__ object
    if hasattr(obj.__class__, k):
        if isinstance(getattr(obj.__class__, k), property):
            return True
    return False

def dict_acceptable(obj, k, blacklist=None):
    # don't store blacklisted variables
    if blacklist and k in blacklist:
        return False
    # don't store hidden variables
    if k.startswith('_'):
        return False
    return is_property(obj, k)

def rate_limit(api):
    # apply rate limiting
    # this is taken from bottlenose/api.py
    # AmazonScraper -> SimpleProductAPI -> BottleNose
    api = api.api.api
    if api.MaxQPS:
        last_query_time = api._last_query_time[0]
        if last_query_time:
                wait_time = 1 / api.MaxQPS - (time.time() - last_query_time)
                if wait_time > 0:
                    log.debug('Waiting %.3fs to call Amazon API' % wait_time)
                    time.sleep(wait_time)
        api._last_query_time[0] = time.time()

from amazon_scraper.product import Product
from amazon_scraper.reviews import Reviews
from amazon_scraper.review import Review


class AmazonScraper(object):
    def __init__(self, access_key, secret_key, associate_tag, *args, **kwargs):
        self.api = AmazonAPI(access_key, secret_key, associate_tag, *args, **kwargs)

    def reviews(self, ItemId=None, URL=None):
        return Reviews(self, ItemId, URL)

    def review(self, Id=None, URL=None):
        return Review(self, Id, URL)

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

