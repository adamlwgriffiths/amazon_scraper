import unittest
import os
import json
from tests import AmazonTestCase


class ProductTestCase(AmazonTestCase):
    def test_asin(self):
        pass

    def test_product(self):
        pass

    def test_url(self):
        pass

    def test_B00FLIJJSA(self):
        # Kindle book
        self.from_asin(ItemId='B00FLIJJSA')

    def test_1589944666(self):
        # Call of Cthulhu boardgame
        # http://www.amazon.com/dp/1589944666
        self.from_asin(ItemId='1589944666')


if __name__ == '__main__':
    unittest.main()
