import logging
import sys
from wsgiref import simple_server

import falcon
import orders


api = application = falcon.API()

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# Resources
getme = orders.GetMeResource()
set_webhook = orders.SetWebhookResource()
webhook = orders.WebhookResource()

# Routes
api.add_route('/me', getme)
api.add_route('/set_webhook', set_webhook)
api.add_route('/webhook', webhook)

if __name__ == '__main__':
    httpd = simple_server.make_server('127.0.0.1', 8000, api)
    httpd.serve_forever()
