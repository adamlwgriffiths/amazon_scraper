==============
Amazon Scraper
==============

Supplements the standard Amazon API with web scraping functionality to get
extra data.


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
    >>> r = amzon.review(id=rs.ids[0])
    >>> r.id
    R3MF0NIRI3BT1E
    >>> r.date
    2011-09-29 18:27:14+00:00
    >>> r.author
    FreeSpirit
    >>> r.text
    Real text would go here, not duplicating due for IP reasons


Authors
=======

 * `Adam Griffiths <https://github.com/adamlwgriffiths>`_
