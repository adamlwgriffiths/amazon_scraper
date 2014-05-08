import urlparse
import json
import xmltodict
from amazon_scraper import amazon_api, extract_asin, reviews_url, dict_acceptable


class Product(object):
    def __init__(self, product):
        self.product = product

    def __getattr__(self, name):
        # allow direct access to the product object
        try:
            return super(Product, self).__getattr__(name)
        except AttributeError:
            # try the api object
            return getattr(self.__dict__['product'], name)

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
            if dict_acceptable(self, k)
        })
        return d
