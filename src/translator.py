import sys
import re

import html
import urllib.request
import urllib.parse

import random


class Translator():
    def __init__(self, from_="auto", to_="auto"):
        self._agent = {
            'User-Agent': "Mozilla/4.0 (compatible;MSIE 6.0;Windows NT 5.1;SV1;.NET CLR 1.1.4322;.NET CLR 2.0.50727;.NET CLR 3.0.04506.30)"}
        self._base_link = "http://translate.google.com/m?tl=%s&sl=%s&q=%s"
        self._from = from_
        self._to = to_

    def sleep_time(self):
        return random.randrange(250, 500, 10) / 1000

    def translate(self, text):
        """
            Returns the translation using google translate
            you must shortcut the language you define
            (French = fr, English = en, Spanish = es, etc...)
            if not defined it will detect it or use english by default
            Example:
            print(translate("salut tu vas bien?", "en"))
            hello you alright?
        """

        self.sleep_time()
        quoted = urllib.parse.quote(text)

        link = self._base_link % (self._to, self._from, quoted)
        request = urllib.request.Request(link, headers=self._agent)
        raw_data = urllib.request.urlopen(request).read()

        data = raw_data.decode("utf-8")

        expr = re.compile(r'(?s)class="(?:t0|result-container)">(.*?)<')

        re_result = expr.findall(data)

        if (len(re_result) == 0):
            result = ""
        else:
            result = html.unescape(re_result[0])

        return(result)
