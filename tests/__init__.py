import unittest
import os
import json
import re
import requests
from mock import patch, call, Mock
from betamax import Betamax
from amazon_scraper import AmazonScraper


with Betamax.configure() as config:
    config.cassette_library_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),'cassettes'))
    config.default_cassette_options['record_mode'] = 'new_episodes'

    if not os.path.exists(config.cassette_library_dir):
        os.makedirs(config.cassette_library_dir)

# use our own get function instead of requests
# this way we can cache the response for long term storage
session = requests.Session()
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
        try:
            filename = os.path.join(os.path.dirname(__file__), 'config.json')
            with open(filename,'r') as f:
                config = json.load(f)
            assert config['access_key']
            assert config['secret_key']
            assert config['associate_tag']
        except:
            raise AssertionError('''
                config.json must be created with the following format:
                    {
                        "access_key":"KEY GOES HERE",
                        "secret_key":"secret key goes here,
                        "associate_tag":"associate tag goes here"
                    }
            ''')
        config = {
            k:str(v)
            for k,v in config.iteritems()
        }
        cls.amzn = AmazonScraper(**config)

    def setUp(self):
        self.patcher = patch('requests.get', side_effect=get)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        pass

    def verify_product(self, p):
        # nothing amazon
        d = p.to_dict()
        assert 'reviews_url' in d, d
        assert 'alternatives' in d, d

    def from_asin(self, ItemId):
        p = self.amzn.lookup(ItemId=ItemId)
        self.verify_product(p)
        return p



if __name__ == '__main__':
    unittest.main()
