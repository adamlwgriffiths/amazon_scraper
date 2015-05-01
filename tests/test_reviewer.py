from __future__ import absolute_import

from tests import AmazonTestCase


class ReviewerTestCase(AmazonTestCase):
    def test_parse_reviews_on_page(self):
        r = self.amzn.review(Id="R3MF0NIRI3BT1E")
        assert "author_reviews_url" in r.to_dict()
        reviewer = self.amzn.reviewer(r.to_dict()["author_reviews_url"])
        all_reviews = reviewer.parse_reviews_on_page()
        keys = ["asin", "author", "author_reviews_url", "date", "id", "rating", "text", "title", "url"]
        for review in all_reviews:
            review_dict = review.to_dict()
            assert "rating" in review_dict
            assert 0.2 <= review_dict["rating"] <= 1.0
            for k, v in review_dict.iteritems():
                assert k in keys, k
                assert v  # Assert our values are non-null

    def test_next_page_url(self):
        r = self.amzn.review(Id="R3MF0NIRI3BT1E")
        assert "author_reviews_url" in r.to_dict()
        reviewer = self.amzn.reviewer(r.to_dict()["author_reviews_url"])
        next_page_url = reviewer.next_page_url
        assert "page=2" in next_page_url
        reviewer = self.amzn.reviewer(next_page_url)
        next_page_url = reviewer.next_page_url
        assert "page=3" in next_page_url

    def test_next_page_url_with_no_next(self):
        reviewer = self.amzn.reviewer(
            "http://www.amazon.com/gp/cdp/member-reviews/A2HX6HJ51UEROW/ref=cm_cr_pr_pdp?ie=UTF8"
        )
        next_page_url = reviewer.next_page_url
        assert next_page_url is None

    def test_reviewer_with_null_constructor_input(self):
        self.assertRaises(ValueError, self.amzn.reviewer, None)

    def test_reviewer_with_profile_url(self):
        self.assertRaises(
            ValueError,
            self.amzn.reviewer,
            "http://www.amazon.com/gp/pdb/profile/A2HX6HJ51UEROW/ref=cm_cr_pr_pdp?ie=UTF8"
        )
