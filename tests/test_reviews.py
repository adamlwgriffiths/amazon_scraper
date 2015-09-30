from __future__ import absolute_import
import unittest
from itertools import islice
from tests import AmazonTestCase


class ReviewsTestCase(AmazonTestCase):
    def test_all_reviews(self):
        asin = "B0051QVF7A"
        p = self.amzn.lookup(ItemId=asin)
        revs = self.amzn.reviews(URL=p.reviews_url)
        all_reviews = list(revs.brief_reviews)
        assert len(all_reviews), 10

        # Ensure all review ids are represented
        revs_ids = set(revs.ids)
        all_reviews_ids = set(map(lambda r: r.id, all_reviews))
        assert revs_ids == all_reviews_ids

        # Ensure everything is found properly we don't really care about values though
        for r in all_reviews:
            assert r.asin == asin

    def test_reviews(self):
        p = self.amzn.lookup(ItemId='B0051QVF7A')
        revs = self.amzn.reviews(URL=p.reviews_url)
        revs.to_dict()
        assert len(list(revs.ids))
        assert revs.asin == 'B0051QVF7A', revs.asin

    def test_reviews_asin(self):
        rs = self.amzn.reviews(ItemId='B0051QVF7A')
        rs.to_dict()
        assert len(list(rs.ids))
        assert rs.asin == 'B0051QVF7A', rs.asin

    def test_reviews_url(self):
        rs = self.amzn.reviews(URL='http://www.amazon.com/Kindle-Wi-Fi-Ink-Display-international/product-reviews/B0051QVF7A/ref=cm_cr_dp_see_all_btm?ie=UTF8&showViewpoints=1&sortBy=bySubmissionDateDescending')
        rs.to_dict()

    def test_review_id(self):
        r = self.amzn.review(Id='R3MF0NIRI3BT1E')
        assert r.user == u'FreeSpirit', r.user
        assert r.asin == 'B00492CIC8', r.asin
        r.to_dict()

    def test_review_url(self):
        r = self.amzn.review(URL='http://www.amazon.com/review/R3MF0NIRI3BT1E')
        r.to_dict()
        assert r.asin == 'B00492CIC8', r.asin

    def test_review_R2OD03CRAU7EDV(self):
        # an anonymous review
        r = self.amzn.review(Id='R2OD03CRAU7EDV')
        assert r.user == u'anonymous', r.user
        assert r.asin == '1568821484', r.asin
        assert r.user_reviews_url is None, r.user_reviews_url
        r.to_dict()

    def test_review_RI3ARYEHW5DT5(self):
        r = self.amzn.review(Id='RI3ARYEHW5DT5')
        assert r.user == u'anonymous', r.user
        assert r.asin == '1568821484', r.asin
        r.to_dict()

    def test_reviews_1(self):
        # test for issue #1
        url = 'http://www.amazon.com/product-reviews/B00008MOQA/ref=cm_cr_pr_top_sort_recent?&sortBy=bySubmissionDateDescending'
        r = self.amzn.reviews(URL=url)
        assert r.asin == 'B00008MOQA', r.asin

    def test_by_item_id(self):
        rs = self.amzn.reviews(ItemId='B0051QVF7A')
        for r in islice(rs, 50):
            assert r.id

    def test_by_url(self):
        p = self.amzn.lookup(ItemId='B0051QVF7A')
        rs = self.amzn.reviews(URL=p.reviews_url)

        for r in islice(rs, 50):
            assert r.id

    def test_by_subreview_to_review(self):
        p = self.amzn.lookup(ItemId='B0051QVF7A')
        rs = self.amzn.reviews(URL=p.reviews_url)

        for r in islice(rs, 50):
            full = r.full_review()
            assert full.id == r.id


if __name__ == '__main__':
    unittest.main()
