import copy
import importlib

import os
import re
from zulip_bots.bots.converter import utils

from typing import Any, Dict, List

import sympy

import requests
import logging
import re
import urllib
from zulip_bots.lib import Any
import wikipedia
from bs4 import BeautifulSoup
from urllib.request import urlopen
from googlesearch import search

import copy
import importlib

import os
from zulip_bots.bots.converter import utils

from typing import List
from typing import Optional, Any, Dict

# match a single element and optional count, like Na2
ELEMENT_CLAUSE = re.compile("([A-Z][a-z]?)([0-9]*)")

def parse_compound(compound):
    assert "(" not in compound, "This parser doesn't grok subclauses"
    return {el: (int(num) if num else 1) for el, num in ELEMENT_CLAUSE.findall(compound)}

def balance_eqn(reactants, products):
    lhs_strings = reactants
    lhs_compounds = [parse_compound(compound) for compound in lhs_strings]

    rhs_strings = products
    rhs_compounds = [parse_compound(compound) for compound in rhs_strings]

    els = sorted(set().union(*lhs_compounds, *rhs_compounds))
    els_index = dict(zip(els, range(len(els))))

    # Build matrix to solve
    w = len(lhs_compounds) + len(rhs_compounds)
    h = len(els)
    A = [[0] * w for _ in range(h)]
    # load with element coefficients
    for col, compound in enumerate(lhs_compounds):
        for el, num in compound.items():
            row = els_index[el]
            A[row][col] = num
    for col, compound in enumerate(rhs_compounds, len(lhs_compounds)):
        for el, num in compound.items():
            row = els_index[el]
            A[row][col] = -num   # invert coefficients for RHS

    # Solve using Sympy for absolute-precision math
    A = sympy.Matrix(A)
    # find first basis vector == primary solution
    coeffs = A.nullspace()[0]
    # find least common denominator, multiply through to convert to integer solution
    coeffs *= sympy.lcm([term.q for term in coeffs])
    reactants = []
    products = []
    print(coeffs)
    ans = ""
    for i in range(len(lhs_strings)):
        if coeffs[i] == 0:
            reactants.append(lhs_strings[i])
    for i in range(len(rhs_strings)):
        if coeffs[i + len(lhs_strings)] == 0:
            products.append(rhs_strings[i])
    coeffs = list(coeffs)
    if len(reactants) > 0:
        ans += balance_eqn(reactants, products)
        for i in reactants:
            lhs_strings.remove(i)
            coeffs.remove(0)
        for i in products:
            rhs_strings.remove(i)
            coeffs.remove(0)
    lhs = " + ".join(["{} {}".format(coeffs[i], s) if coeffs[i] > 0 else '' for i, s in enumerate(lhs_strings)])
    rhs = " + ".join(["{} {}".format(coeffs[i], s) if coeffs[i] > 0 else '' for i, s in enumerate(rhs_strings, len(lhs_strings))])

    if len(ans) > 0:
        S = ans.split("->")
        lhs += " + " + S[0]
        rhs += " + " +  S[1]
        print(S)
    return ("{} -> {}\n".format(lhs, rhs))


Eqn_Hash = {}

def load_equations():
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    f = open(os.path.join(__location__, 'equations.txt'));
    Lines = f.readlines()
    for line in Lines:
        x = (line.strip())
        x = x.split(" ")
        Eqn_Hash[x[0]] = x[1]

class Atom(object):
    def usage(self) -> str:
        return '''
               This plugin allows users to .
               '''
    def handle_message(self, message: Dict[str, str], bot_handler: Any) -> None:
        bot_response = get_bot_response(message, bot_handler)
        bot_handler.send_reply(message, bot_response)


def get_bot_wiki_response(query):
    help_text = 'Please enter your search term after {}'
    new_content = 'Search term: ' + query + '\n'
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


    if len(data.json()['query']['search']) == 0:
        new_content = 'I am sorry. The search term you provided is not found :slightly_frowning_face:'
    else:
        search_string = data.json()['query']['search'][0]['title'].replace(' ', '_')

        new_content += wikipedia.summary(search_string, sentences=2)
    return new_content + "\n"

def get_bot_response(message: Dict[str, str], bot_handler: Any) -> str:
    content = message['content']
    words = content.split()
    print(words)
    if words[0] == "products":
        load_equations()
        compounds = []
        for i in range(len(words)):
            if i % 2 == 1:
                compounds.append(words[i])
        compounds.sort()
        init_compounds = list(compounds)
        return_answer = "The following equations were used to arrive at the final product\n"
        reaction = "-1"
        max_entropy = 0
        while reaction != "0":
            reaction = "0"
            reactants = []
            products = []
            for i in range(1 << len(compounds)):
                if bin(i).count('1') >= 2 and bin(i).count('1') <= 5:
                    S = ""
                    tem_reactants = []
                    for j in range(len(compounds)):
                        if ((i >> j) & 1) == 1:
                            S += compounds[j] + '+'
                            tem_reactants.append(compounds[j])
                    if S in Eqn_Hash.keys():
                        Temp = Eqn_Hash[S].split("+")
                        cur_entropy = int(Temp[len(Temp) - 1])
                        if max_entropy < cur_entropy:
                            reaction = Eqn_Hash[S]
                            reactants = tem_reactants
                            products = Temp
                            products.pop()
            for i in reactants:
                compounds.remove(i)
            for i in products:
                compounds.append(i)
            if len(products) > 0:
                return_answer += balance_eqn(reactants, products)
            compounds.sort()
        return_answer += "\nThe final product is \n"
        return_answer += balance_eqn(init_compounds, compounds)
        return return_answer
    if words[0] == "add":
        reactants = []
        products = []
        entropy = int(words[len(words) - 1])
        i = 1
        while i < len(words):
            if words[i] == "=":
                break
            if (i & 1) == 1:
                reactants.append(words[i])
            i += 1
        j = i + 1
        while j < len(words) - 1:
            if ((j - i) & 1) == 1:
                products.append(words[j])
            j += 1
        reactants.sort()
        products.sort()
        R = ""
        for i in reactants:
            R += i + '+'
        P = ""
        for i in products:
            P += i + '+'
        P += str(entropy)
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        f = open(os.path.join(__location__, 'equations.txt'), "a");
        f.write("\n" + R + " " + P)
        return "Successfully added the reaction"
    if words[0] == "explain_products":
        compounds = []
        return_answer = ""
        for i in range(len(words)):
            if i != 0:
                compounds.append(words[i])
        return_answer += "\nHere are some facts about the compounds\n"
        for i in compounds:
            return_answer += get_bot_wiki_response(i)
        return return_answer
    else:

        compounds = []
        return_answer = ""
        for i in range(len(words)):
                compounds.append(words[i])
        return_answer += "\nAnswer:\n"
        query = ''
        for i in compounds:
            query += i + ' '
        query += ' chemistry wikipedia'

        for i in search(query, tld="com", num=10, stop=1, pause=2):
            store = i
            break

        html = urlopen(store)
        print(store)
        title = BeautifulSoup(html, 'html.parser').find("title").text
        title = title[:-12]
        print(title)
        return get_bot_wiki_response(title)

handler_class = Atom


