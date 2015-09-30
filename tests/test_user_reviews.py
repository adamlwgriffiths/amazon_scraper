from __future__ import absolute_import
import unittest
from itertools import islice
from tests import AmazonTestCase


class UserReviewsTestCase(AmazonTestCase):
    def test_brief_reviews(self):
        r = self.amzn.review(Id="R3MF0NIRI3BT1E")
        assert "user_reviews_url" in r.to_dict()
        reviewer = self.amzn.user_reviews(URL=r.user_reviews_url)

        for review in islice(reviewer.brief_reviews, 20):
            assert review.id

    def test_brief_reviews_match(self):
        r = self.amzn.review(Id="R3MF0NIRI3BT1E")
        assert "user_reviews_url" in r.to_dict()
        reviewer = self.amzn.user_reviews(URL=r.user_reviews_url)

        for review in islice(reviewer.brief_reviews, 5):
            print review.id
            assert review.id
            fr = review.full_review()
            assert fr.id == review.id, (fr.id, review.id)
            assert fr.asin == review.asin, (fr.asin, review.asin)
            assert fr.rating == review.rating, (fr.rating, review.rating)
            assert fr.user_id == review.user_id, (fr.user_id, review.user_id)

    def test_next_page_url(self):
        r = self.amzn.review(Id="R3MF0NIRI3BT1E")
        assert "user_reviews_url" in r.to_dict()
        reviewer = self.amzn.user_reviews(URL=r.user_reviews_url)
        next_page_url = reviewer.next_page_url
        assert "page=2" in next_page_url
        reviewer = self.amzn.user_reviews(URL=next_page_url)
        next_page_url = reviewer.next_page_url
        assert "page=3" in next_page_url

    def test_reviewer_id(self):
        reviewer = self.amzn.user_reviews(Id="A2HX6HJ51UEROW")
        assert reviewer.id == "A2HX6HJ51UEROW"
        next_page_url = reviewer.next_page_url
        assert next_page_url is None

    def test_next_page_url_with_no_next(self):
        reviewer = self.amzn.user_reviews(URL="http://www.amazon.com/gp/cdp/member-reviews/A2HX6HJ51UEROW/ref=cm_cr_pr_pdp?ie=UTF8")
        next_page_url = reviewer.next_page_url
        assert next_page_url is None

    def test_reviewer_with_null_constructor_input(self):
        with self.assertRaises(Exception):
            self.amzn.user_reviews()

    def test_reviewer_with_profile_url(self):
        with self.assertRaises(Exception):
            self.amzn.user_reviews(URL="http://www.amazon.com/gp/pdb/profile/A2HX6HJ51UEROW/ref=cm_cr_pr_pdp?ie=UTF8")

    def test_reviewer_reviews_iteration(self):
        r = self.amzn.review(Id="R3MF0NIRI3BT1E")
        reviewer = r.user_reviews()
        for rev in islice(reviewer.brief_reviews, 50):
            assert rev.id

    def test_reviewer_iterable(self):
        r = self.amzn.review(Id="R3MF0NIRI3BT1E")
        reviewer = r.user_reviews()
        for rev in islice(reviewer, 50):
            assert rev.id

    def test_reviewer_url(self):
        r = self.amzn.review(Id="R3MF0NIRI3BT1E")
        reviewer = self.amzn.user_reviews(URL=r.user_reviews_url)
        assert reviewer


if __name__ == '__main__':
    unittest.main()
