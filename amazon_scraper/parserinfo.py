from dateutil import parser

class GermanParserInfo(parser.parserinfo):
    MONTHS = [('Jan', 'Januar'),
              ('Feb', 'Febraur'),
              ('Mär', 'März'),
              ('Apr', 'April'),
              ('Mai', 'Mai'),
              ('Jun', 'Juni'),
              ('Jul', 'Juli'),
              ('Aug', 'August'),
              ('Sep', 'September'),
              ('Okt', 'Oktober'),
              ('Nov', 'November'),
              ('Dez', 'Dezember')]