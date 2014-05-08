import unittest
import os
from tests import AmazonTestCase

class SearchTestCase(AmazonTestCase):
    def test_reviews(self):
        p = self.amzn.product(ItemId='B0051QVF7A')
        rs = self.amzn.reviews(URL=p.reviews_url)
        rs.to_dict()
        assert len(list(rs.ids))

    def test_reviews_asin(self):
        rs = self.amzn.reviews(ItemId='B0051QVF7A')
        rs.to_dict()
        assert len(list(rs.ids))

    def test_reviews_url(self):
        rs = self.amzn.reviews(URL='http://www.amazon.com/Kindle-Wi-Fi-Ink-Display-international/product-reviews/B0051QVF7A/ref=cm_cr_dp_see_all_btm?ie=UTF8&showViewpoints=1&sortBy=bySubmissionDateDescending')
        rs.to_dict()

    def test_review(self):
        p = self.amzn.product(ItemId='B0051QVF7A')
        rs = self.amzn.reviews(URL=p.reviews_url)
        r = self.amzn.review(Id=rs.ids[0])
        r.to_dict()

    def test_review_id(self):
        r = self.amzn.review(Id='R3MF0NIRI3BT1E')
        r.to_dict()

    def test_reivew_url(self):
        r = self.amzn.review(URL='http://www.amazon.com/review/R3MF0NIRI3BT1E')
        r.to_dict()


if __name__ == '__main__':
    unittest.main()
