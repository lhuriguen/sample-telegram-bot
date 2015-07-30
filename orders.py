import json
import logging
import os

import falcon
import requests

from weather import get_weather


TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'


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

    def send_message(self, chat_id, text, reply_id):
        if not text:
            logging.error('no text specified')
            return
        params = {'chat_id': str(chat_id),
                  'text': text.encode('utf-8'),
                  'reply_to_message_id': str(reply_id), }
        result = requests.get(BASE_URL + 'sendMessage', params=params)
        # Log the contents of the response.
        logging.info(result.text)

    def on_post(self, req, resp):
        if req.content_length in (None, 0):
            # Nothing to do
            return

        # Read the request body.
        body = req.stream.read()
        if not body:
            raise falcon.HTTPBadRequest('Empty request body',
                                        'A valid JSON document is required.')

        try:
            content = json.loads(body.decode('utf-8'))

        except (ValueError, UnicodeDecodeError):
            raise falcon.HTTPError(falcon.HTTP_753,
                                   'Malformed JSON',
                                   'Could not decode the request body. The '
                                   'JSON was incorrect or not encoded as '
                                   'UTF-8.')

        # Log the contents of the request.
        logging.info(content)

        update_id = content['update_id']
        message = content['message']
        message_id = message.get('message_id')
        date = message.get('date')
        text = message.get('text')
        fr = message.get('from')
        sender = fr.get('first_name', 'stranger')
        chat = message['chat']
        chat_id = chat['id']

        if 'location' in message:
            # Get the user's location.
            latitude = message.get('location')['latitude']
            longitude = message.get('location')['longitude']
            logging.info("Location: {}, {}".format(latitude, longitude))
            w = get_weather(latitude, longitude)
            if w:
                text = ('{}\nTemperature: {} ºC\n'
                        'Humidity: {}%\nPressure: {} hPa').format(
                        w.description, w.temperature, w.humidity, w.pressure)
                self.send_message(chat_id, text, message_id)
            else:
                self.send_message(
                    chat_id,
                    'I cannot find weather information for that location.',
                    message_id)
            return

        if not text:
            logging.info('no text')
            return

        if text.startswith('/'):
            if text == '/hello':
                self.send_message(
                    chat_id, 'Hello {0}'.format(sender), message_id)
            elif text == '/weather':
                self.send_message(
                    chat_id, 'Please share your location with me!', message_id)
