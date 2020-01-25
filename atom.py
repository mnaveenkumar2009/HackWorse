import requests
import logging
import re
import urllib
from zulip_bots.lib import Any
import wikipedia

from typing import Optional, Any, Dict

class Atom(object):
    '''
    This plugin facilitates searching for chemical agents, chemistry reactions, etc.
    '''

    META = {
        'name': 'Atom',
        'description': 'Chemistry, simplified.',
    }

    def usage(self) -> str:
        return '''
            This plugin facilitates searching for chemical agents, chemistry reactions, etc.
    '''

    def handle_message(self, message: Dict[str, str], bot_handler: Any) -> None:
        bot_response = self.get_bot_wiki_response(message, bot_handler)
        bot_handler.send_reply(message, bot_response)

    def get_bot_wiki_response(self, message: Dict[str, str], bot_handler: Any) -> Optional[str]:
        '''This function prints information related to the requested topic.'''

        help_text = 'Please enter your search term after {}'

        # Checking if the link exists.
        query = message['content']
        query += ' chemistry'
        if query == '':
            return help_text.format(bot_handler.identity().mention)

        query_wiki_url = 'https://en.wikipedia.org/w/api.php'
        query_wiki_params = dict(
            action='query',
            list='search',
            srsearch=query,
            format='json'
        )
        try:
            data = requests.get(query_wiki_url, params=query_wiki_params)

        except requests.exceptions.RequestException:
            logging.error('broken link')
            return 'Uh-Oh ! Sorry ,couldn\'t process the request right now.:slightly_frowning_face:\n' \
                   'Please try again later.'

        # Checking if the bot accessed the link.
        if data.status_code != 200:
            logging.error('Page not found.')
            return 'Uh-Oh ! Sorry ,couldn\'t process the request right now.:slightly_frowning_face:\n' \
                   'Please try again later.'

        new_content = 'Search term: ' + query + '\n'

        if len(data.json()['query']['search']) == 0:
            new_content = 'I am sorry. The search term you provided is not found :slightly_frowning_face:'
        else:
            search_string = data.json()['query']['search'][0]['title'].replace(' ', '_')

            new_content += wikipedia.summary(search_string, sentences=2)
        return new_content

handler_class = Atom
