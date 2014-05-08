import unittest
import os
import json
from tests import AmazonTestCase


class ProductTestCase(AmazonTestCase):
    def test_asin(self):
        self.from_asin(ItemId='B00FLIJJSA')

    def test_product(self):
        from amazon_scraper.product import Product
        p = self.amzn.api.lookup(ItemId='B00FLIJJSA')
        p = Product(p)
        p.to_dict()

    def test_url(self):
        p = self.amzn.lookup(URL='http://www.amazon.com/Kindle-Wi-Fi-Ink-Display-international/dp/B0051QVF7A/ref=cm_cr_pr_product_top')
        p.to_dict()

    def test_B00FLIJJSA(self):
        # Kindle book
        self.from_asin(ItemId='B00FLIJJSA')

    def test_1589944666(self):
        # Call of Cthulhu boardgame
        # http://www.amazon.com/dp/1589944666
        self.from_asin(ItemId='1589944666')


if __name__ == '__main__':
    unittest.main()
