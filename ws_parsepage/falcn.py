import falcon

from .test import Resource
from .pricetracker import PriceTracker

api = application = falcon.API()

test = Resource()
api.add_route('/test', test)

pt = PriceTracker()
api.add_route('/pt', pt)
