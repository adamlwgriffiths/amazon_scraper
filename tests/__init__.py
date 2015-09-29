from __future__ import absolute_import
import unittest
import os
import json
import re
import requests
from mock import patch, call, Mock
from amazon_scraper import AmazonScraper
from amazon_scraper.product import Product


session = requests.Session()

#use_cassette = False
use_cassette = True

if use_cassette:
    from betamax import Betamax
    with Betamax.configure() as config:
        config.cassette_library_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'cassettes'))
        config.default_cassette_options['record_mode'] = 'new_episodes'

        if not os.path.exists(config.cassette_library_dir):
            os.makedirs(config.cassette_library_dir)

    # use our own get function instead of requests
    # this way we can cache the response for long term storage
    cassette_re = re.compile(r'[^a-z0-9]+', flags=re.I)

    def get(*args, **kwargs):
        '''Intercepts calls to requests.get and redirects them to use BetaMax
        '''
        global session
        # use the url as the cassette
        cassette = args[0]
        cassette = cassette_re.sub('', cassette)
        with Betamax(session).use_cassette(cassette):
            return session.get(*args, **kwargs)


class AmazonTestCase(unittest.TestCase):
    amzn = None

    @classmethod
    def setUpClass(cls):
        config = {}
        try:
            config['access_key'] = os.environ['AWS_ACCESS_KEY_ID']
            config['secret_key'] = os.environ['AWS_SECRET_ACCESS_KEY']
            config['associate_tag'] = os.environ['AWS_ASSOCIATE_TAG']
        except:
            raise AssertionError('''
                The following environment variables must be set:
                        "AWS_ACCESS_KEY_ID"
                        "AWS_SECRET_ACCESS_KEY"
                        "AWS_ASSOCIATE_TAG"
            ''')
        cls.amzn = AmazonScraper(MaxQPS=0.5, **config)

    def setUp(self):
        if use_cassette:
            self.patcher = patch('requests.get', side_effect=get)
            self.patcher.start()

    def tearDown(self):
        if use_cassette:
            self.patcher.stop()

    def verify_product(self, p):
        # nothing amazon
        assert type(p) == Product
        d = p.to_dict()
        assert 'reviews_url' in d, d
        assert 'alternatives' in d, d

    def from_asin(self, ItemId):
        p = self.amzn.lookup(ItemId=ItemId)
        self.verify_product(p)
        return p


if __name__ == '__main__':
    unittest.main()
