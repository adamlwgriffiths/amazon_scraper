# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
import re
try:
    import urlparse
except:
    import urllib.parse as urlparse
import urllib
import functools
import time
import requests
import warnings
from amazon.api import AmazonAPI
import dateutil.parser
from bs4 import BeautifulSoup
from .version import __version__  # load our version

if 'unicode' not in dir(globals()['__builtins__']):
    unicode = str

# stop warnings about unused variable
__version__

log = logging.getLogger(__name__)

# fix #1
# 'html.parser' has trouble with http://www.amazon.com/product-reviews/B00008MOQA/ref=cm_cr_pr_top_sort_recent?&sortBy=bySubmissionDateDescending
# it sometimes doesn't find the asin span
html_parser = 'html.parser'
#html_parser = 'html5lib'

#user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36'
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.94 Safari/537.36'

amazon_base = 'http://www.amazon.com'

_extract_asin_regexp = re.compile(r'/dp/(?P<asin>[^/]+)')
_process_rating_regexp = re.compile(r'([\d\.]+) out of [\d\.]+ stars', flags=re.I)
_extract_reviews_asin_regexp = re.compile(r'/product-reviews/(?P<asin>[^/]+)', flags=re.I)
_extract_review_id_regexp = re.compile(r'/review/(?P<id>[^/]+)', flags=re.I)
_extract_reviewer_id_regexp = re.compile(r'/member-reviews/(?P<id>[^/]+)', flags=re.I)
_price_regexp = re.compile(r'(?P<price>[$£][\d,\.]+)', flags=re.I)


def extract_asin(url):
    try:
        match = _extract_asin_regexp.search(url)
        return str(match.group('asin'))
    except:
        warnings.warn('Error matching ASIN in URL {}'.format(url))
        raise


def product_url(asin):
    url = '{base}/dp/{asin}'
    return url.format(base=amazon_base, asin=asin)


def add_affiliate(url, affiliate):
    return add_query(url, tag=affiliate)


def reviews_url(asin):
    url = '{base}/product-reviews/{asin}/ref=cm_cr_pr_top_sort_recent?&sortBy=bySubmissionDateDescending'
    return url.format(base=amazon_base, asin=asin)


def review_url(id):
    url = '{base}/review/{id}'
    return url.format(base=amazon_base, id=id)


def reviewer_url(id):
    url = '{base}/gp/cdp/member-reviews/{id}'
    return url.format(base=amazon_base, id=id)


def process_rating(text):
    """The rating normalised to 1.0
    """
    try:
        rating_match = _process_rating_regexp.search(text)
        return float(rating_match.group(1)) / 5.0
    except:
        warnings.warn('Error processing rating for text "{}"'.format(text))
        raise


def extract_reviews_asin(url):
    try:
        match = _extract_reviews_asin_regexp.search(url)
        return str(match.group('asin'))
    except:
        warnings.warn('Error matching reviews ASIN in URL {}'.format(url))
        raise


def extract_review_id(url):
    try:
        match = _extract_review_id_regexp.search(url)
        return str(match.group('id'))
    except:
        warnings.warn('Error matching review ID in URL {}'.format(url))
        raise


def extract_reviewer_id(url):
    try:
        match = _extract_reviewer_id_regexp.search(url)
        return str(match.group('id'))
    except:
        warnings.warn('Error matching review ID in URL {}'.format(url))
        raise


def extract_price(text):
    try:
        match = _price_regexp.search(text)
        price = match.group('price')
        price = re.sub(r'[$£,]', u'', price)
        price = float(price)
        return price
    except:
        warnings.warn('Error extracting price in text "{}"'.format(text))
        raise


def add_query(url, **kwargs):
    scheme, netloc, path, query_string, fragment = urlparse.urlsplit(url)
    query_params = urlparse.parse_qs(query_string)
    # remove any existing value of 'key'
    keys = kwargs.keys()
    query_params = dict(filter(lambda x: x[0] not in keys, query_params.iteritems()))
    query_params.update(kwargs)
    query_string = urllib.urlencode(query_params, doseq=True)
    return urlparse.urlunsplit((scheme, netloc, path, query_string, fragment))


def get_review_date(raw_date):
    string = unicode(raw_date)
    # 2011-11-07T05:50:41Z
    date = dateutil.parser.parse(string)
    return date


def strip_html_tags(html):
    if html:
        soup = BeautifulSoup(html, html_parser)
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


def get(url, api):
    rate_limit(api)
    # verify=False ignores SSL errors
    r = requests.get(url, headers={'User-Agent': user_agent}, verify=False)
    r.raise_for_status()
    return r


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
    bn = api.bottlenose
    if bn.MaxQPS:
        last_query_time = bn._last_query_time[0]
        if last_query_time:
            wait_time = 1 / bn.MaxQPS - (time.time() - last_query_time)
            if wait_time > 0:
                log.debug('Waiting %.3fs to call Amazon API' % wait_time)
                time.sleep(wait_time)
        bn._last_query_time[0] = time.time()

# This schema of imports is non-standard and should change. It will require some re-ordering of
# functions inside the package though.
from amazon_scraper.product import Product
from amazon_scraper.reviews import Reviews
from amazon_scraper.review import Review
from amazon_scraper.user_reviews import UserReviews


class AmazonScraper(object):

    def __init__(self, access_key, secret_key, associate_tag, *args, **kwargs):
        self.api = AmazonAPI(access_key, secret_key, associate_tag, *args, **kwargs)

    def reviews(self, ItemId=None, URL=None):
        return Reviews(self, ItemId, URL)

    def review(self, Id=None, URL=None):
        return Review(self, Id, URL)

    def user_reviews(self, Id=None, URL=None):
        return UserReviews(self, Id, URL)

    def lookup(self, URL=None, **kwargs):
        if URL:
            kwargs['ItemId'] = extract_asin(URL)

        result = self.amazon_simple_api.lookup(**kwargs)
        if isinstance(result, (list, tuple)):
            result = [Product(self, p) for p in result]
        else:
            result = Product(self, result)
        return result

    def similarity_lookup(self, **kwargs):
        for p in self.amazon_simple_api.similarity_lookup(**kwargs):
            yield Product(self, p)

    def browse_node_lookup(self, **kwargs):
        return self.amazon_simple_api.browse_node_lookup(**kwargs)

    def search(self, **kwargs):
        for p in self.amazon_simple_api.search(**kwargs):
            yield Product(self, p)

    def search_n(self, n, **kwargs):
        for p in self.amazon_simple_api.search_n(n, **kwargs):
            yield Product(self, p)

    @property
    def amazon_simple_api(self):
        return self.api

    @property
    def bottlenose(self):
        return self.api.api
