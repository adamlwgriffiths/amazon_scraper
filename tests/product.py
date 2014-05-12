import unittest
import os
import json
from tests import AmazonTestCase
import amazon_scraper


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

    def test_call_through(self):
        p = self.amzn.lookup(ItemId='B00FLIJJSA')
        assert p.asin == 'B00FLIJJSA', p.asin
        assert isinstance(p.price_and_currency, tuple), p.price_and_currency

    def test_reviews_url(self):
        p = self.amzn.lookup(ItemId='B00FLIJJSA')
        assert p.reviews_url == amazon_scraper.reviews_url('B00FLIJJSA'), p.reviews_url

    def test_B00FLIJJSA(self):
        # Kindle book
        self.from_asin(ItemId='B00FLIJJSA')

    def test_1589944666(self):
        # Call of Cthulhu boardgame
        # http://www.amazon.com/dp/1589944666
        self.from_asin(ItemId='1589944666')

    @unittest.skip("Need to find product that exhibits this behavior")
    def test_parent(self):
        p = self.amzn.lookup(ItemId='0933635869')
        # parent should be 7th edition 1568821816
        p.parentAsin
        assert result == expected, (result, expected)

    def test_alternatives_media_matrix(self):
        p = self.amzn.lookup(ItemId='1497344824')
        result = set(p.alternatives)
        expected = set(['9163192993', 'B00IVM5X7E', 'B00IPXPQ9O', '0899669433', '1482998742', '0441444814'])
        #expected = set(['9163192993', 'B00IVM5X7E', 'B00IPXPQ9O', '0899669433', '1482998742', '0441444814', 'B00IKFMDMA', 'B00J3GRX02'])
        assert result == expected, (result, expected)

    def test_alternatives_twisterMediaMatrix(self):
        p = self.amzn.lookup(ItemId='B00G3L7YT0')
        result = set(p.alternatives)
        expected = set(['0425256863',])
        assert result == expected, (result, expected)

    @unittest.skip("Unavailable items aren't handled yet")
    def test_unavailable_to_api(self):
        p = self.amzn.lookup(ItemId='B00IKFMDMA')

    def test_0575081570(self):
        # has multiple editorial reviews, second onwards not available from API
        # has author bio not available from API
        p = self.amzn.lookup(ItemId='0575081570')

        #print ''
        #print p.soup
        #print ''

        expected = u'H. P. Lovecraft was born in 1890 in Providence'
        assert p.author_bio[:len(expected)] == expected, p.author_bio
        expected = 'http://www.amazon.com/H.P.-Lovecraft/e/B000AQ40D2'
        assert p.author_page_url[:len(expected)] == expected, p.author_page_url


if __name__ == '__main__':
    unittest.main()
