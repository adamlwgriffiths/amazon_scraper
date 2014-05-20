==============
Amazon Scraper
==============

A Hybrid Web scraper / API client. Supplements the standard Amazon API with web
scraping functionality to get extra data. Specifically, product reviews.

Uses the `Amazon Simple Product API <https://pypi.python.org/pypi/python-amazon-simple-product-api/>`_
to provide API accessible data. API search functions are imported directly into
the amazon_scraper module.

Parameters are kept the same are in the same style as the underlying API, which in
turn uses Bottlenose style parameters. Hence the non-Pythonic parameter names (ItemId).


Installation
============

::

    pip install amazon_scraper


Example
=======

Create::

    >>> from amazon_scraper import AmazonScraper
    >>> amzn = AmazonScraper("put your access key", "secret key", "and associate tag here")


Search::

    >>> import itertools
    >>> for p in itertools.islice(amzn.search(Keywords='python', SearchIndex='Books'), 5):
    >>>     print p.title
    Learning Python, 5th Edition
    Python Programming: An Introduction to Computer Science 2nd Edition
    Python In A Day: Learn The Basics, Learn It Quick, Start Coding Fast (In A Day Books) (Volume 1)
    Python for Data Analysis: Data Wrangling with Pandas, NumPy, and IPython
    Python Cookbook


Lookup by ASIN/ItemId::

    >>> p = amzn.lookup(ItemId='B00FLIJJSA')
    >>> p.title
    Kindle, Wi-Fi, 6" E Ink Display - for international shipment
    >>> p.url
    http://www.amazon.com/Kindle-Wi-Fi-Ink-Display-international/dp/B0051QVF7A/ref=cm_cr_pr_product_top


Batch Lookups::

    >>> for p in amzn.lookup(ItemId='B0051QVF7A,B007HCCNJU,B00BTI6HBS'):
    >>>     print p.title
    Kindle, Wi-Fi, 6" E Ink Display - for international shipment
    Kindle, 6" E Ink Display, Wi-Fi - Includes Special Offers (Black)
    Kindle Paperwhite 3G, 6" High Resolution Display with Next-Gen Built-in Light, Free 3G + Wi-Fi - Includes Special Offers


By URL::

    >>> p = amzn.lookup(URL='http://www.amazon.com/Kindle-Wi-Fi-Ink-Display-international/dp/B0051QVF7A/ref=cm_cr_pr_product_top')
    >>> p.title
    Kindle, Wi-Fi, 6" E Ink Display - for international shipment
    >>> p.asin
    B0051QVF7A


Product Ratings::

    >>> p = amzn.lookup(ItemId='B00FLIJJSA')
    >>> p.ratings
    [8, 4, 6, 4, 13]


Alternative Bindings::

    >>> p = amzn.lookup(ItemId='B000GRFTPS')
    >>> p.alternatives
    ['B00IVM5X7E', '9163192993', '0899669433', 'B00IPXPQ9O', '1482998742', '0441444814', '1497344824']
    >>> for asin in p.alternatives:
    >>>     alt = amzn.lookup(ItemId=asin)
    >>>     print alt.title, alt.binding
    The King in Yellow Kindle Edition
    The King in Yellow Unknown Binding
    King in Yellow Hardcover
    The Yellow Sign Audible Audio Edition
    The King in Yellow MP3 CD
    THE KING IN YELLOW Mass Market Paperback
    The King in Yellow Paperback


Supplemental text not available via the API::

    >>> p = amzn.lookup(ItemId='0441016685')
    >>> p.supplemental_text
    [u"Bob Howard is a computer-hacker desk jockey ... ", u"Lovecraft\'s Cthulhu meets Len Deighton\'s spies ... ", u"This dark, funny blend of SF and ... "]


View lists of reviews::

    >>> p = amzn.lookup(ItemId='B0051QVF7A')
    >>> rs = amzn.reviews(URL=p.reviews_url)
    >>> rs.asin
    B0051QVF7A
    >>> rs.ids
    ['R3MF0NIRI3BT1E', 'R3N2XPJT4I1XTI', 'RWG7OQ5NMGUMW', 'R1FKKJWTJC4EAP', 'RR8NWZ0IXWX7K', 'R32AU655LW6HPU', 'R33XK7OO7TO68E', 'R3NJRC6XH88RBR', 'R21JS32BNNQ82O', 'R2C9KPSEH78IF7']
    >>> rs.url
    http://www.amazon.com/product-reviews/B0051QVF7A/ref=cm_cr_pr_top_sort_recent?&sortBy=bySubmissionDateDescending


By ASIN/ItemId::

    >>> rs = amzn.reviews(ItemId='B0051QVF7A')
    >>> rs.asin
    B0051QVF7A
    >>> rs.ids
    ['R3MF0NIRI3BT1E', 'R3N2XPJT4I1XTI', 'RWG7OQ5NMGUMW', 'R1FKKJWTJC4EAP', 'RR8NWZ0IXWX7K', 'R32AU655LW6HPU', 'R33XK7OO7TO68E', 'R3NJRC6XH88RBR', 'R21JS32BNNQ82O', 'R2C9KPSEH78IF7']


Individual reviews::

    >>> r = amzn.review(Id=rs.ids[0])
    >>> r.id
    R3MF0NIRI3BT1E
    >>> r.url
    http://www.amazon.com/review/R3MF0NIRI3BT1E
    >>> r.date
    2011-09-29 18:27:14+00:00
    >>> r.author
    FreeSpirit
    >>> r.text
    Having been a little overwhelmed by the choices between all the new Kindles ... <snip>


By URL::

    >>> r = amzn.review(URL='http://www.amazon.com/review/R3MF0NIRI3BT1E')
    >>> r.id
    R3MF0NIRI3BT1E


Authors
=======

 * `Adam Griffiths <https://github.com/adamlwgriffiths>`_
