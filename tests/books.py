import unittest
from tests import BaseTestCase

class BookTestCase(BaseTestCase):

    def test_B00FLIJJSA(self):
        self.process_product(asin='B00FLIJJSA')


if __name__ == '__main__':
    unittest.main()
