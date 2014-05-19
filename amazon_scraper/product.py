import urlparse
import json
import re
import xmltodict
import requests
from bs4 import BeautifulSoup
from amazon_scraper import product_url, extract_asin, reviews_url, strip_html_tags, dict_acceptable


class Product(object):
    def __init__(self, product):
        self.product = product
        self._soup = None

    def __getattr__(self, name):
        # allow direct access to the product object
        return getattr(self.product, name)

    @property
    def soup(self):
        # lazily load the soup
        # otherwise we will slow down simple operations
        if not self._soup:
            url = product_url(self.asin)
            r = requests.get(url)
            r.raise_for_status()
            self._soup = BeautifulSoup(r.text, 'html.parser')
        return self._soup

    @property
    def alternatives(self):
        # TODO: there are FAR more versions hidden behind API calls
        # it would be nice to get them all

        # kindle
        tag = self.soup.find('table', class_='twisterMediaMatrix')
        if tag:
            asins = set([
                extract_asin(anchor['href'])
                for anchor in tag.find_all('a', href=re.compile(ur'/dp/'))
            ])
            if self.asin in asins:
                asins.remove(self.asin)
            return list(asins)

        # paperback
        tag = self.soup.find('div', id='MediaMatrix')
        if tag:
            asins = set([
                extract_asin(anchor['href'])
                for anchor in tag.find_all('a', href=re.compile(ur'/dp/'))
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
        url = str(self.product.item['CustomerReviews']['IFrameURL'])

        p = urlparse.urlparse(url)
        q = urlparse.parse_qs(p.query)
        asin = q['asin'][0]

        reviews = reviews_url(asin)

        return reviews

    @property
    def author_bio(self):
        tag = self.soup.find('div', class_='mainContent')
        if tag:
            text = strip_html_tags(str(tag))
            if text:
                return text
        return None

    @property
    def author_page_url(self):
        tag = self.soup.find('div', class_='author_page_link')
        if tag:
            a = tag.find('a', href=re.compile(r'/e/',flags=re.I))
            if a:
                link = str(a['href'])
                link = urlparse.urljoin('http://www.amazon.com', link)
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
            for rating, row in zip([4,3,2,1,0], table.find_all('tr', class_='a-histogram-row')):
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

    def to_dict(self):
        d = {}
        # print the object as an xml string, parse the string to a dict
        # good times!
        # this hack brought to you by the letters: X, M, L and by the
        # words: Bad, and Design
        #d.update(xmltodict.parse(self.product.to_string()))
        d = xmltodict.parse(self.product.to_string())
        d = json.loads(json.dumps(d))

        # filter our the top level crap which includes AWS keys etc
        d = {'Item':d['Item']}

        # add the python properties
        d.update({
            k:getattr(self.product, k)
            for k in dir(self.product)
            if dict_acceptable(self.product, k, ['browse_nodes'])
        })

        # add our own properties
        d.update({
            k:getattr(self, k)
            for k in dir(self)
            if dict_acceptable(self, k, ['soup'])
        })
        return d
