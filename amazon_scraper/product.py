from __future__ import absolute_import
try:
    import urlparse
except:
    import urllib.parse as urlparse
import urllib
import json
import re
import xmltodict
from bs4 import BeautifulSoup
from amazon_scraper import (
    get,
    product_url,
    extract_asin,
    reviews_url,
    strip_html_tags,
    dict_acceptable,
    retry,
    html_parser,
    amazon_base,
)

if 'unicode' not in dir(globals()['__builtins__']):
    unicode = str


class Product(object):
    def __init__(self, api, product):
        self.api = api
        self.product = product
        self._soup = None

    def __getattr__(self, name):
        """
        Allow direct access to the product object
        """
        return getattr(self.product, name)

    @property
    @retry()
    def soup(self):
        # lazily load the soup
        # otherwise we will slow down simple operations
        if not self._soup:
            r = get(self.url, self.api)
            self._soup = BeautifulSoup(r.text, html_parser)
        return self._soup

    @property
    def url(self):
        return product_url(self.asin)

    @property
    def alternatives(self):
        # TODO: there are FAR more versions hidden behind API calls
        # it would be nice to get them all

        # kindle
        tag = self.soup.find('table', class_='twisterMediaMatrix')
        if tag:
            asins = set([
                extract_asin(anchor['href'])
                for anchor in tag.find_all('a', href=re.compile(r'/dp/'))
            ])
            if self.asin in asins:
                asins.remove(self.asin)
            return list(asins)

        # paperback
        tag = self.soup.find('div', id='MediaMatrix')
        if tag:
            asins = set([
                extract_asin(anchor['href'])
                for anchor in tag.find_all('a', href=re.compile(r'/dp/'))
            ])
            if self.asin in asins:
                asins.remove(self.asin)
            return list(asins)

        return []

    @property
    def reviews_url(self):
        # we could use the asin to directly make a review url
        # but some products actually use the ISBN for the review url
        # and the ASIN version would fail
        # so we'll get the url given to us, and get the asin/isbn from that
        try:
            # the variable has changed in python simple product api, sigh
            item = getattr(self.product, 'item', None)
            if not item:
                item = getattr(self.product, 'parsed_response', None)

            url = unicode(item['CustomerReviews']['IFrameURL'])

            p = urlparse.urlparse(url)
            q = urlparse.parse_qs(p.query)
            asin = q['asin'][0]
        except Exception as e:
            asin = self.asin

        reviews = reviews_url(asin)

        return reviews

    def reviews(self):
        return self.api.reviews(ItemId=self.asin)

    @property
    def author_bio(self):
        tag = self.soup.find('div', class_='mainContent')
        if tag:
            text = strip_html_tags(unicode(tag))
            if text:
                return text
        return None

    @property
    def author_page_url(self):
        tag = self.soup.find('div', class_='author_page_link')
        if tag:
            a = tag.find('a', href=re.compile(r'/e/', flags=re.I))
            if a:
                link = unicode(a['href'])
                link = urlparse.urljoin(amazon_base, link)
                return link
        return None

    @property
    def ratings(self):
        ratings = [0, 0, 0, 0, 0]
        reviews_div = self.soup.find('div', class_='reviews')
        if reviews_div:
            for rating, rating_class in [
                (4, 'histoRowfive'),
                (3, 'histoRowfour'),
                (2, 'histoRowthree'),
                (1, 'histoRowtwo'),
                (0, 'histoRowone'),
            ]:
                rating_div = reviews_div.find('div', class_=rating_class)
                if rating_div:
                    # no ratings means this won't exist
                    tag = rating_div.find('div', class_='histoCount')
                    if tag:
                        value = tag.string
                        value = value.replace(',', '')
                        ratings[rating] = int(value)
            return ratings

        table = self.soup.find('table', id='histogramTable')
        if table:
            for rating, row in zip([4, 3, 2, 1, 0], table.find_all('tr', class_='a-histogram-row')):
                # get the third td tag
                children = [child for child in row.find_all('td', recursive=False)]
                td = children[2]
                data = td.find('span', class_=False)
                if data:
                    # number could have , in it which fails during int conversion
                    value = data.string
                    value = value.replace(',', '')
                    ratings[rating] = int(value)
            return ratings

        return ratings

    @property
    def supplemental_text(self):
        # get all the known text blobs
        # remove any found in editorial reviews
        result = []

        # kindle
        # http://www.amazon.com/dp/1593080050
        tag = self.soup.find('div', id='postBodyPS')
        if tag:
            text = strip_html_tags(unicode(tag))
            if text:
                result.append(text)

        # paperbacks
        # http://www.amazon.com/dp/1568822812
        tag = self.soup.find('div', id='bookDescription_feature_div')
        if tag:
            tag = tag.find('div', class_=None)
            text = strip_html_tags(unicode(tag))
            if text:
                result.append(text)

        # extract from the javascript code that updates the iframe
        # http://www.amazon.com/dp/1491268727
        tag = self.soup.find('script', text=re.compile(r'bookDescEncodedData', flags=re.I))
        if tag:
            match = re.search(r'bookDescEncodedData\s=\s"(?P<description>[^",]+)', tag.text)
            if match:
                text = match.group('description')
                text = urllib.unquote(text)
                text = strip_html_tags(text)
                if text:
                    result.append(text)

        # http://www.amazon.com/dp/1616611359
        for tag in self.soup.find_all('div', class_='productDescriptionWrapper'):
            text = unicode(tag)
            text = strip_html_tags(text)
            if text:
                result.append(text)

        # android apps
        # http://www.amazon.com/dp/B008A1I0SU
        tag = self.soup.find('div', class_='mas-product-description-wrapper')
        if tag:
            sub_tag = tag.find('div', class_='content')
            if sub_tag:
                tag = sub_tag
            text = strip_html_tags(unicode(tag))
            if text:
                result.append(text)

        # amazon instant video
        # http://www.amazon.com/dp/B004C0YS5C
        # older method
        tag = self.soup.find('div', class_='prod-synopsis')
        if tag:
            text = strip_html_tags(unicode(tag))
            if text:
                result.append(text)
        # newer method
        tag = self.soup.find('div', class_='dv-simple-synopsis')
        if tag:
            text = strip_html_tags(unicode(tag))
            if text:
                result.append(text)

        # http://www.amazon.com/dp/B0006FUAD6
        tag = self.soup.find('div', id=re.compile('feature-bullets', flags=re.I))
        if tag:
            tags = map(unicode, tag.find_all('span'))
            text = strip_html_tags(u''.join(tags))
            if text:
                result.append(text)

        # http://www.amazon.com/dp/B00DHF39KS
        tag = self.soup.find('div', class_='aplus')
        if tag:
            text = strip_html_tags(unicode(tag))
            if text:
                result.append(text)

        return result

    def to_dict(self):
        d = {}
        # print the object as an xml string, parse the string to a dict
        # good times!
        # this hack brought to you by the letters: X, M, L and by the
        # words: Bad, and Design
        d = xmltodict.parse(self.product.to_string())
        d = json.loads(json.dumps(d))

        # filter our the top level crap which includes AWS keys etc
        d = {'Item': d['Item']}

        # add the python properties
        d.update({
            k: getattr(self.product, k)
            for k in dir(self.product)
            if dict_acceptable(self.product, k, blacklist=['browse_nodes', 'api'])
        })

        # add our own properties
        d.update({
            k: getattr(self, k)
            for k in dir(self)
            if dict_acceptable(self, k, blacklist=['soup', 'api', 'ratings', 'reviews'])
        })
        return d
