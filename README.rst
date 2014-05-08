==============
Amazon Scraper
==============

Supplements the standard Amazon API with web scraping functionality to get
extra data.

Uses the `Amazon Simple Product API <https://pypi.python.org/pypi/python-amazon-simple-product-api/>`_
to provide API accessible data. API search functions are imported directly into
the amazon_scraper module.


Example
=======

::

    >>> import amazon_scraper as amzn
    >>> amzn.initialise("put your access key", "secret key", "and associate tag here")
    >>> p = amzn.product(asin='B00FLIJJSA')
    >>> p.title
    Kindle, Wi-Fi, 6" E Ink Display - for international shipment
    >>> p.asin
    B0051QVF7A
    >>> rs = amzn.reviews(url=p.reviews_url)
    >>> rs.asin
    B0051QVF7A
    >>> rs.ids
    ['R3MF0NIRI3BT1E', 'R3N2XPJT4I1XTI', 'RWG7OQ5NMGUMW', 'R1FKKJWTJC4EAP', 'RR8NWZ0IXWX7K', 'R32AU655LW6HPU', 'R33XK7OO7TO68E', 'R3NJRC6XH88RBR', 'R21JS32BNNQ82O', 'R2C9KPSEH78IF7']
    >>> rs.url
    http://www.amazon.com/product-reviews/B0051QVF7A/ref=cm_cr_pr_top_sort_recent?&sortBy=bySubmissionDateDescending
    >>> r = amzon.review(id=rs.ids[0])
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
    >>> import itertools
    >>> for result in itertools.islice(amzn.search(Keywords='python', SearchIndex='Books'), 5):
    >>>     p = amzn.product(product=result)
    >>>     print p.title
    Learning Python, 5th Edition
    Python Programming: An Introduction to Computer Science 2nd Edition
    Python In A Day: Learn The Basics, Learn It Quick, Start Coding Fast (In A Day Books) (Volume 1)
    Python for Data Analysis: Data Wrangling with Pandas, NumPy, and IPython
    Python Cookbook


Authors
=======

 * `Adam Griffiths <https://github.com/adamlwgriffiths>`_
