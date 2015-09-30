from __future__ import absolute_import
import unittest
from itertools import islice
from tests import AmazonTestCase


class SearchTestCase(AmazonTestCase):
    def test_search(self):
        for p in islice(self.amzn.search(Keywords='python', SearchIndex='Books'), 5):
            self.verify_product(p)

    def test_search_n(self):
        results = list(self.amzn.search_n(5, Keywords='python', SearchIndex='Books'))
        assert len(results), 5
        for p in results:
            self.verify_product(p)

    def test_lookup(self):
        p = self.amzn.lookup(ItemId='B0051QVF7A')
        self.verify_product(p)

    def test_lookup_multiple(self):
        for p in self.amzn.lookup(ItemId='B0051QVF7A,B00FLIJJSA'):
            self.verify_product(p)

    def test_similarity_lookup(self):
        for p in self.amzn.similarity_lookup(ItemId='B0051QVESA,B005DOK8NW'):
            self.verify_product(p)


if __name__ == '__main__':
    unittest.main()
