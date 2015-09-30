==============
Amazon Scraper
==============

A Hybrid Web scraper / API client. Supplements the standard Amazon API with web
scraping functionality to get extra data. Specifically, product reviews.

Uses the `Amazon Simple Product API <https://pypi.python.org/pypi/python-amazon-simple-product-api/>`_
to provide API accessible data. API search functions are imported directly into
the amazon_scraper module.

Parameters are in the same style as the Amazon Simple Product API, which in
turn uses Bottlenose style parameters. Hence the non-Pythonic parameter names (ItemId).


The AmazonScraper constructor will pass 'args' and 'kwargs' to `Bottlenose <https://github.com/lionheart/bottlenose>`_ (via Amazon Simple Product API).
Bottlenose supports AWS regions, queries per second limiting, query caching and other nice features. Please view Bottlenose' API for more information on this.

The latest version of python-amazon-simple-product-api (1.5.0 at time of writing), doesn't support these arguemnts, only Region.
If you require these, please use the latest code from their repository with the following command::

    pip install git+https://github.com/yoavaviram/python-amazon-simple-product-api.git#egg=python-amazon-simple-product-api


Caveat
======

Amazon continually try and keep scrapers from working, they do this by:

* A/B testing (randomly receive different HTML).
* Huge numbers of HTML layouts for the same product categories.
* Changing HTML layouts.
* Moving content inside iFrames.

Amazon have resorted to moving more and more content into iFrames which this scraper can't handle.
I envisage a time where most data will be inaccessible without more complex logic.

I've spent a long time trying to get these scrapers working and it's a never ending battle.
I don't have the time to continually keep up the pace with Amazon.
If you are interested in improving Amazon Scraper, please let me know (creating an issue is fine).
Any help is appreciated.


Installation
============

::

    pip install amazon_scraper


Dependencies
============

* `python-amazon-simple-product-api <https://pypi.python.org/pypi/python-amazon-simple-product-api/>`_
* `requests <http://docs.python-requests.org/en/latest/>`_
* `beautifulsoup4 <http://www.crummy.com/software/BeautifulSoup/>`_
* `xmltodict <https://github.com/martinblech/xmltodict>`_
* `python-dateutil <https://dateutil.readthedocs.org/en/latest/>`_


Examples
========

All Products All The Time
~~~~~~~~~~~~~~~~~~~~~~~~~
Create an API instance::

    >>> from amazon_scraper import AmazonScraper
    >>> amzn = AmazonScraper("put your access key", "secret key", "and associate tag here")


The creation function accepts 'kwargs' which are passed to 'bottlenose.Amazon' constructor::

    >>> from amazon_scraper import AmazonScraper
    >>> amzn = AmazonScraper("put your access key", "secret key", "and associate tag here", Region='UK', MaxQPS=0.9, Timeout=5.0)


Search::

    >>> from __future__ import print_function
    >>> import itertools
    >>> for p in itertools.islice(amzn.search(Keywords='python', SearchIndex='Books'), 5):
    >>>     print(p.title)
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
    >>>     print(p.title)
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
    >>>     print(alt.title, alt.binding)
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


Review API
~~~~~~~~~~
View lists of reviews::

    >>> p = amzn.lookup(ItemId='B0051QVF7A')
    >>> rs = p.reviews()
    >>> rs.asin
    B0051QVF7A
    >>> # print the reviews on this first page
    >>> rs.ids
    ['R3MF0NIRI3BT1E', 'R3N2XPJT4I1XTI', 'RWG7OQ5NMGUMW', 'R1FKKJWTJC4EAP', 'RR8NWZ0IXWX7K', 'R32AU655LW6HPU', 'R33XK7OO7TO68E', 'R3NJRC6XH88RBR', 'R21JS32BNNQ82O', 'R2C9KPSEH78IF7']
    >>> rs.url
    http://www.amazon.com/product-reviews/B0051QVF7A/ref=cm_cr_pr_top_sort_recent?&sortBy=bySubmissionDateDescending
    >>> # by iterating over the reviews object we get access to reviews on ALL pages
    >>> for r in rs.brief_reviews:
    >>>     print(r.id)
    'R3MF0NIRI3BT1E'
    'R3N2XPJT4I1XTI'
    'RWG7OQ5NMGUMW'
    ...

View detailed reviews::
    >>> rs = amzn.reviews(ItemId='B0051QVF7A')
    >>> for r in rs.full_reviews():
    >>>     print(r.id)
    'R3MF0NIRI3BT1E'
    'R3N2XPJT4I1XTI'
    'RWG7OQ5NMGUMW'
    ...

Quickly get a list of all reviews on a review page using the `all_reviews` property.
This uses the brief reviews provided on the review page to avoid downloading each review separately. As such, some information
may not be accessible::

    >>> p = amzn.lookup(ItemId='B0051QVF7A')
    >>> rs = p.reviews()
    >>> all_reviews_on_page = list(rs)
    >>> len(all_reviews_on_page)
    10
    >>> r = all_reviews_on_page[0]
    >>> r.title
    'Fantastic device - pick your Kindle!'
    >>> fr = r.full_review()
    >>> fr.title
    'Fantastic device - pick your Kindle!'

By ASIN/ItemId::

    >>> rs = amzn.reviews(ItemId='B0051QVF7A')
    >>> rs.asin
    B0051QVF7A
    >>> rs.ids
    ['R3MF0NIRI3BT1E', 'R3N2XPJT4I1XTI', 'RWG7OQ5NMGUMW', 'R1FKKJWTJC4EAP', 'RR8NWZ0IXWX7K', 'R32AU655LW6HPU', 'R33XK7OO7TO68E', 'R3NJRC6XH88RBR', 'R21JS32BNNQ82O', 'R2C9KPSEH78IF7']


For individual reviews use the `review` method::

    >>> review_id = 'R3MF0NIRI3BT1E'
    >>> r = amzn.review(Id=review_id)
    >>> r.id
    R3MF0NIRI3BT1E
    >>> r.asin
    B00492CIC8
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


User Reviews API
~~~~~~~~~~~~~~~~~~
This package also supports getting reviews written by a specific user.

Get reviews that a single author has created::

    >>> ur = amzn.user_reviews(Id="A2W0GY64CJSV5D")
    >>> ur.brief_reviews
    >>> ur.name
    >>> fr = list(ur.brief_reviews)[0].full_review()


Get reviews for a user, from a review object

    >>> r = amzn.review(Id="R3MF0NIRI3BT1E")
    >>> # we can get the reviews directly, or via the API with a URL or ID
    >>> ur = r.user_reviews()
    >>> ur = amzn.user_reviews(URL=r.author_reviews_url)
    >>> ur = amzn.user_reviews(Id=r.author_id)
    >>> ur.brief_reviews
    >>> ur.name


Iterate over the current page's reviews::

    >>> ur = amzn.user_reviews(Id="A2W0GY64CJSV5D")
    >>> for r in ur.brief_reviews:
    >>>     print(r.id)


Iterate over all author reviews::

    >>> ur = amzn.user_reviews(Id="A2W0GY64CJSV5D")
    >>> for r in ur:
    >>>     print(r.id)



Authors
=======

 * `Adam Griffiths <https://github.com/adamlwgriffiths>`_
 * `Greg Rehm <https://github.com/hahnicity>`_
