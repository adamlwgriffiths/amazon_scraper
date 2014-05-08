import unittest
import os
import json
import amazon_scraper

class BaseTestCase(unittest.TestCase):

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
        amazon_scraper.initialise(**config)

    def process_product(self, asin):
        p = amazon_scraper.product(asin=asin)
        p.to_dict()
