import unittest
from tests import BaseTestCase

class BookTestCase(BaseTestCase):

    def test_1589944666(self):
        self.process_product(asin='1589944666')


if __name__ == '__main__':
    unittest.main()
