from __future__ import absolute_import
import unittest
from itertools import islice
from tests import AmazonTestCase
import amazon_scraper


class ProductTestCase(AmazonTestCase):
    def test_asin(self):
        self.from_asin(ItemId='B00FLIJJSA')

    def test_product(self):
        from amazon_scraper.product import Product
        p = self.amzn.api.lookup(ItemId='B00FLIJJSA')
        p = Product(self.amzn, p)
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
        p = self.from_asin(ItemId='B00FLIJJSA')
        assert(sum(p.ratings) > 0)

    def test_1589944666(self):
        # Call of Cthulhu boardgame
        # http://www.amazon.com/dp/1589944666
        p = self.from_asin(ItemId='1589944666')
        assert(sum(p.ratings) > 0)

    @unittest.skip("Need to find product that exhibits this behavior")
    def test_parent(self):
        p = self.amzn.lookup(ItemId='0933635869')
        # parent should be 7th edition 1568821816
        result = p.parentAsin
        expected = '1568821816'
        assert result == expected, (result, expected)

    def test_alternatives_media_matrix(self):
        p = self.amzn.lookup(ItemId='1497344824')
        result = set(p.alternatives)
        expected = set(['B00JDKVW46', '0554320738', '1482998750', 'B001CJXD48', 'B00J3GRX02', '0441444822'])
        assert result == expected, (result, expected)

    def test_alternatives_twisterMediaMatrix(self):
        p = self.amzn.lookup(ItemId='B00G3L7YT0')
        result = set(p.alternatives)
        expected = set(['0425256863', 'B00FLY3XP4'])
        assert result == expected, (result, expected)

    @unittest.skip("Unavailable items aren't handled yet")
    def test_unavailable_to_api(self):
        #p = self.amzn.lookup(ItemId='B00IKFMDMA')
        pass

    @unittest.skip("Author bio is now missing")
    def test_0575081570_author_bio(self):
        # has multiple editorial reviews, second onwards not available from API
        # has author bio not available from API
        p = self.amzn.lookup(ItemId='0575081570')
        expected = u'H. P. Lovecraft was born in 1890 in Providence'
        assert p.author_bio[:len(expected)] == expected, p.author_bio

    @unittest.skip("Author page url is now missing")
    def test_0575081570_author_page_url(self):
        p = self.amzn.lookup(ItemId='0575081570')
        expected = 'http://www.amazon.com/H.P.-Lovecraft/e/B000AQ40D2'
        assert p.author_page_url[:len(expected)] == expected, p.author_page_url

    def test_non_english(self):
        self.from_asin(ItemId='B00ELPO6WS')

    def test_no_reviews(self):
        p = self.from_asin(ItemId='B00ELPO6WS')
        assert(isinstance(p.ratings, list))

    def test_ratings_reviews_tag(self):
        p = self.from_asin(ItemId='B007V8RQC4')
        assert(sum(p.ratings) > 0)

    def test_ratings_amazon_instant(self):
        p = self.from_asin(ItemId='B00FGN2HZW')
        assert(sum(p.ratings) > 0)

    @unittest.skip("Text now hidden in iFrame")
    def test_supplemental_text_frankenstein(self):
        # Frankenstein
        p = self.from_asin(ItemId='1593080050')
        text = '\n'.join(p.supplemental_text)
        expected = u'Our confusion of creator and created'
        assert expected in text, (expected, text)

    def test_supplemental_text_strange_songs(self):
        # Strange Songs
        p = self.from_asin(ItemId='1568822812')
        text = '\n'.join(p.supplemental_text)
        expected = u'Strange Songs can be heard across time and space'
        assert expected in text, (expected, text)

    @unittest.skip("Text now hidden in iFrame")
    def test_supplemental_text_awoken(self):
        # Awoken
        p = self.from_asin(ItemId='1491268727')
        text = '\n'.join(p.supplemental_text)
        expected = u'Serra Elinsen lives in Trotwood Ohio'
        assert expected in text, (expected, text)
        expected = u'Andromeda Slate, the self-proclaimed most ordinary girl in America'
        assert expected in text, (expected, text)

    @unittest.skip("Text now hidden in iFrame")
    def test_supplemental_text_boardgames(self):
        # Elder Sign
        p = self.from_asin(ItemId='1616611359')
        text = '\n'.join(p.supplemental_text)
        expected = u'Elder Sign is a fast-paced, cooperative dice game'
        assert expected in text, (expected, text)

    @unittest.skip('No reliable way to get this without getting a lot of other crap')
    def test_supplemental_text_android(self):
        # Call of Cthulhu: The Wasted Land
        p = self.from_asin(ItemId='B008A1I0SU')
        text = '\n'.join(p.supplemental_text)
        expected = u'Call of Cthulhu was originally the title of a novella'
        assert expected in text, (expected, text)

    def test_supplemental_text_amazon_instant(self):
        # South Park: Coon vs. Coon & Friends
        p = self.from_asin(ItemId='B004C0YS5C')
        text = '\n'.join(p.supplemental_text)
        expected = u'Coon and Friends find themselves at the mercy of Cartman'
        assert expected in text, (expected, text)

    @unittest.skip("Text now hidden in iFrame")
    def test_supplemental_toys(self):
        # Cthulhu Mini Plush
        p = self.from_asin(ItemId='B0006FUAD6')
        text = '\n'.join(p.supplemental_text)
        expected = u'This absolutely adorable'
        assert expected in text, (expected, text)

    def test_supplemental_text_pc_game(self):
        # Wolfenstein: New Order
        p = self.from_asin(ItemId='B00DHF39KS')
        text = '\n'.join(p.supplemental_text)
        expected = u'Europe, 1960. The Nazis turned the tide of the war'
        assert expected in text, (expected, text)

    @unittest.skip("Text now hidden in iFrame")
    def test_supplemental_text_atrocity_archives(self):
        # Atrocity Archives
        p = self.from_asin(ItemId='0441016685')
        text = '\n'.join(p.supplemental_text)
        expected = u'This dark, funny blend of SF and horror reads like James Bond'
        assert expected in text, (expected, text)

    def test_iteration_14(self):
        # test #14
        p = self.amzn.lookup(ItemId='B00BGO0Q9O')
        assert p.title
        assert p.ratings

        rs = self.amzn.reviews(URL=p.reviews_url)
        for r in islice(rs, 50):
            assert r.id

    def test_iteration_15(self):
        # test #15
        for p in islice(self.amzn.search(Keywords='python', SearchIndex='Books'), 50):
            assert p.title

    def test_reviews(self):
        p = self.amzn.lookup(ItemId='B00BGO0Q9O')
        assert p.title
        assert p.ratings

        rs = p.reviews()
        for r in islice(rs, 50):
            assert r.id


if __name__ == '__main__':
    unittest.main()
