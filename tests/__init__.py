import unittest
import os
import json
from amazon_scraper import AmazonScraper

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

    def verify_product(self, p):
        # nothing amazon
        d = p.to_dict()
        assert 'reviews_url' in d, d
        assert 'alternatives' in d, d

    def from_asin(self, ItemId):
        p = self.amzn.lookup(ItemId=ItemId)
        self.verify_product(p)



if __name__ == '__main__':
    unittest.main()
