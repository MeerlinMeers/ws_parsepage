#!/usr/bin/env python3

import falcon
import json
import urllib.request
import urllib.parse
import re


def fetchpage(url, params, headers=None):
    if headers is None:
        headers = {}
    print(url, params, headers)
    data = urllib.parse.urlencode(params)
    data = data.encode('utf-8')
    r = urllib.request.urlopen(url, data, 100)
    return (r)


class PriceTrackerError(Exception):
    """Base class for errors in the :mod:`googlemaps` module.
    
    Methods of the :class:`GoogleMaps` raise this when something goes wrong.
     
    """
    #: See http://code.google.com/apis/maps/documentation/geocoding/index.html#StatusCodes
    #: for information on the meaning of these status codes.
    G_GEO_SUCCESS = 200

    _STATUS_MESSAGES = {
        G_GEO_SUCCESS: 'G_GEO_SUCCESS',
    }

    def __init__(self, status, url=None, response=None):
        """Create an exception with a status and optional full response.
        
        :param status: Either a ``G_GEO_`` code or a string explaining the 
         exception.
        :type status: int or string
        :param url: The query URL that resulted in the error, if any.
        :type url: string
        :param response: The actual response returned from Google, if any.
        :type response: dict 
        
        """
        Exception.__init__(self, status)  # Exception is an old-school class
        self.status = status
        self.response = response
        self.url = url

    @property
    def __str__(self):
        """Return a string representation of this :exc:`GoogleMapsError`."""
        if self.status in self._STATUS_MESSAGES:
            if self.response is not None and 'responseDetails' in self.response:
                retval = 'Error %d: %s' % (self.status, self.response['responseDetails'])
            else:
                retval = 'Error %d: %s' % (self.status, self._STATUS_MESSAGES[self.status])
        else:
            retval = str(self.status)
        return retval

    @property
    def __unicode__(self):
        """Return a unicode representation of this :exc:`GoogleMapsError`."""
        return str(self.__str__, 'utf-8')


class PriceTracker(object):
    _ENXA_URL = '''http://www.enxa.de/index.php?art_id=65ce3fa3f597af77c3a319a07903955c&action=search_result_rechner'''
    _ENXA_POSTING_VALUES = {
        'oelsorte': '4',
        'plz': '77654',
        'liter': '3000',
        'lieferstellen': '1',
        'express': ''
    }

    def on_get(self, req, resp):
        resp.content_type = 'application/json'
        resp.body = json.dumps(self.getResult())
        resp.status = falcon.HTTP_200

    def getResult(self):
        resp = fetchpage(self._ENXA_URL, self._ENXA_POSTING_VALUES)
        print(resp.status)
        if resp.status != 200:
            raise PriceTrackerError("Page not found")
        page = resp.read().decode('latin_1')
        print(len(page))
        #        print(page)
        p1 = self.extractPriceFromPage(page, "Gesamtpreis.*?Brutto:.*?(\d{2,4})[,.](\d{2})")
        p2 = self.extractPriceFromPage(page,
                                       "Angebote vom (\d{1,2})\. (Januar|Februar|M&auml;rz|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember) (\d{4})")
        a = {'price': p1, 'date': p2}
        return a

    def __init__(self):
        #self.getResult()
        print(self.getResult())

    def extractPriceFromPage(self, data, reString):
        #print(data)
        result = re.search(reString, data, re.S | re.I)
        if result:
            price = result.group(1) + "." + result.group(2)  # Gesamtbetrag brutto
            price = price.replace("&auml;", "ä")
            print(price)
            return price
        else:
            print("error")
            return "error"


if __name__ == "__main__":
    pt = PriceTracker()
