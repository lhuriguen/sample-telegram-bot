import json
import logging
import os

import falcon
import requests


TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'


class Resource(object):

    def on_get(self, req, resp):
        resp.body = '{"message": "Hello world!"}'
        resp.status = falcon.HTTP_200


class GetMeResource(object):

    def on_get(self, req, resp):
        result = requests.get(BASE_URL + 'getMe')
        resp.status = str(result.status_code) + ' ' + result.reason
        resp.content_type = result.headers['content-type']
        resp.body = result.text


class SetWebhookResource(object):

    def on_get(self, req, resp):
        params = {'url': req.get_param('url', True)}
        result = requests.get(BASE_URL + 'setWebhook', params=params)
        resp.status = str(result.status_code) + ' ' + result.reason
        resp.content_type = result.headers['content-type']
        resp.body = result.text


class WebhookResource(object):

    def on_post(self, req, resp):
        if req.content_length in (None, 0):
            # Nothing to do
            return

        # Read the request body.
        body = req.stream.read()
        if not body:
            raise falcon.HTTPBadRequest('Empty request body',
                                        'A valid JSON document is required.')

        logging.info('request body:')
        logging.info(body)

        try:
            content = json.loads(body.decode('utf-8'))

        except (ValueError, UnicodeDecodeError):
            raise falcon.HTTPError(falcon.HTTP_753,
                                   'Malformed JSON',
                                   'Could not decode the request body. The '
                                   'JSON was incorrect or not encoded as '
                                   'UTF-8.')

        update_id = content.get('update_id')
        message = content.get('message')
        message_id = message.get('message_id')
        date = message.get('date')
        text = message.get('text')
        user_from = message.get('from')
        chat = message['chat']
        chat_id = chat['id']

        if not text:
            logging.info('no text')
            return

        resp.body = json.dumps({'message': text})
