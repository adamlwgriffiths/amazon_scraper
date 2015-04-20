from __future__ import absolute_import
import unittest
import os
from tests import AmazonTestCase

class ReviewsTestCase(AmazonTestCase):
    def test_parse_reviews_on_page(self):
        p = self.amzn.lookup(ItemId="B0051QVF7A")
        revs = self.amzn.reviews(URL=p.reviews_url)
        all_reviews = revs.parse_reviews_on_page()
        assert len(all_reviews), 10

        # Ensure all review ids are represented
        revs_ids = set(revs.ids)
        all_reviews_ids = set([dict_.to_dict()["id"] for dict_ in all_reviews])
        assert revs_ids == all_reviews_ids

        # Ensure everything is found properly we don't really care about values though
        for dict_ in all_reviews:
            assert None not in dict_.to_dict().values()

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
        assert r.author == u'FreeSpirit', r.author
        assert r.asin == 'B00492CIC8', rs.asin
        r.to_dict()

    def test_review_url(self):
        r = self.amzn.review(URL='http://www.amazon.com/review/R3MF0NIRI3BT1E')
        r.to_dict()
        assert r.asin == 'B00492CIC8', r.asin

    def test_review_R2OD03CRAU7EDV(self):
        r = self.amzn.review(Id='R2OD03CRAU7EDV')
        assert r.author == u'anonymous', r.author
        assert r.asin == '1568821484', r.asin
        r.to_dict()

    def test_review_RI3ARYEHW5DT5(self):
        r = self.amzn.review(Id='RI3ARYEHW5DT5')
        assert r.author == u'anonymous', r.author
        assert r.asin == '1568821484', r.asin
        r.to_dict()

    def test_reviews_(self):
        # test for issue #1
        url = 'http://www.amazon.com/product-reviews/B00008MOQA/ref=cm_cr_pr_top_sort_recent?&sortBy=bySubmissionDateDescending'
        r = self.amzn.reviews(URL=url)
        assert r.asin == 'B00008MOQA', r.asin


if __name__ == '__main__':
    unittest.main()
