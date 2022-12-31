import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse, parse_qs, urljoin
from typing import Optional
from unsafe.utils.strings import ua
import json
import random
import string
import re


class Crawler:
    def __init__(self):
        ...

    def _string_generator(self, size=7, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def _filter_result(self, link: str):
        try:
            if link.startswith('/url?'):
                o = urlparse(link, 'http')
                link = parse_qs(o.query)['q'][0]
            o = urlparse(link, 'http')
            if o.netloc and 'google' not in o.netloc:
                return link
        except Exception:
            ...

    def browser_search(self, query: str, timeout: int = 10, proxy: Optional[str] = None):
        res = []
        if proxy:
            google = requests.get(
                f'https://google.com/search?q={query}', timeout=timeout, proxies={"http": proxy, "https": proxy})
            bing = requests.get(
                f'https://www.bing.com/search?q={query}', timeout=timeout, proxies={"http": proxy, "https": proxy})
            ask = requests.get(
                f'https://www.ask.com/web?q={query}', timeout=timeout, proxies={"http": proxy, "https": proxy})
        else:
            google = requests.get(
                f'https://google.com/search?q={query}', timeout=timeout)
            bing = requests.get(
                f'https://www.bing.com/search?q={query}', timeout=timeout)
            ask = requests.get(
                f'https://www.ask.com/web?q={query}', timeout=timeout)

        soup = bs(google.text, "html.parser")
        try:
            anchors = soup.find(id='search').findAll('a')
        except AttributeError:
            gbar = soup.find(id='gbar')
            if gbar:
                gbar.clear()
            anchors = soup.findAll('a')
        for i in anchors:
            if self._filter_result(i["href"]):
                res.append(self._filter_result(i["href"]))
            else:
                pass
        ######################
        if "There are no results for" not in bing.text:
            soup = bs(bing.text,  "html.parser")
            try:
                anchors = soup.find(id='b_results').findAll("a")
                for i in anchors:
                    res.append(i["href"])
            except:
                ...
        ######################
        soup = bs(ask.text,  "html.parser")
        try:
            anchors = soup.find(
                attrs={"class": "PartialSearchResults-results"}).findAll("a")
            for i in anchors:
                res.append(i["href"])
        except:
            ...
        ######################
        return list(set(res))

    def _link_extractor(self, source):
        before_result = []
        result = []
        for i in source.split('\n'):
            try:
                regexed = re.search(
                    r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()!@:%_\+.~#?&\/\/=]*)", i)
                if regexed:
                    before_result.append(regexed)
            except:
                pass
        for i in before_result:
            result.append(i.group())
        return result

    def _phone_extractor(self, source: str):
        before_result = []
        result = []
        for i in source.split('\n'):
            i = i.replace("۱", "1")
            i = i.replace("۲", "2")
            i = i.replace("۳", "3")
            i = i.replace("۴", "4")
            i = i.replace("۵", "5")
            i = i.replace("۶", "6")
            i = i.replace("۷", "7")
            i = i.replace("۸", "8")
            i = i.replace("۹", "9")
            i = i.replace("۰", "0")
            try:
                regexed = re.search(
                    r"(\+|00)[1-9][0-9 \-\(\)\.]{7,32}", i)
                if regexed:
                    before_result.append(regexed)
            except:
                pass
        for i in before_result:
            result.append(i.group())
        return result

    def _username_extractor(self, source: str):
        before_result = []
        result = []
        for i in source.split('\n'):
            try:
                regexed = re.search(
                    r"(?<![\w@])@([\w@]+(?:[.!][\w@]+)*)", i)
                if regexed:
                    before_result.append(regexed)
            except:
                pass
        for i in before_result:
            result.append(i.group())
        return result

    def _email_extractor(self, source: str):
        before_result = []
        result = []
        for i in source.split('\n'):
            try:
                regexed = re.search(
                    r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", i)
                if regexed:
                    before_result.append(regexed)
            except:
                pass
        for i in before_result:
            result.append(i.group())
        return result

    def crawl_page(self, url: str, timeout: int = 10, proxy: Optional[str] = None, proxies: Optional[list] = None):
        """
        Crawling a Page and Extract Phone, Email, Usernames and Other Links.
        """
        if "http://" in url:
            url = url.replace("http://", "")
        elif "https://" in url:
            url = url.replace("https://", "")
        else:
            ...
        url = "http://" + url
        domain_name = urlparse(url).netloc
        if proxy:
            proxies = {"http": proxy, "https": proxy}
        elif proxies:
            p = random.choice(proxies)
            proxies = {"http": p, "https": p}
        else:
            r = requests.get(url, timeout=timeout)
            return {
                "links": self._link_extractor(r.text),
                "phones": self._phone_extractor(r.text),
                "usernames": self._username_extractor(r.text),
                "emails": self._email_extractor(r.text)
            }
        r = requests.get(url, timeout=timeout, proxies=proxies)
        return {
            "links": self._link_extractor(r.text),
            "phones": self._phone_extractor(r.text),
            "usernames": self._username_extractor(r.text),
            "emails": self._email_extractor(r.text)
        }

    def _get_all_forms(self, url):
        """Given a `url`, it returns all forms from the HTML content"""
        soup = bs(requests.get(url).content, "html.parser")
        return soup.find_all("form")

    def _get_form_details(self, form):
        """
        This function extracts all possible useful information about an HTML `form`
        """
        details = {}
        # get the form action (target url)
        action = form.attrs.get("action", "").lower()
        # get the form method (POST, GET, etc.)
        method = form.attrs.get("method", "get").lower()
        # get all the input details such as type and name
        inputs = []
        for input_tag in form.find_all("input"):
            input_type = input_tag.attrs.get("type", "text")
            input_name = input_tag.attrs.get("name")
            inputs.append({"type": input_type, "name": input_name})
        # put everything to the resulting dictionary
        details["action"] = action
        details["method"] = method
        details["inputs"] = inputs
        return details

    def _submit_form(self, form_details, url, value):
        """
        Submits a form given in `form_details`
        Params:
            form_details (list): a dictionary that contain form information
            url (str): the original URL that contain that form
            value (str): this will be replaced to all text and search inputs
        Returns the HTTP Response after form submission
        """
        # construct the full URL (if the url provided in action is relative)
        target_url = urljoin(url, form_details["action"])
        # get the inputs
        inputs = form_details["inputs"]
        data = {}
        for input in inputs:
            # replace all text and search values with `value`
            if input["type"] == "text" or input["type"] == "search":
                input["value"] = value
            input_name = input.get("name")
            input_value = input.get("value")
            if input_name and input_value:
                # if input name and value are not None,
                # then add them to the data of form submission
                data[input_name] = input_value

        if form_details["method"] == "post":
            return requests.post(target_url, data=data)
        else:
            # GET request
            return requests.get(target_url, params=data)

    def xss_scanner(self, url: str, js_script: str = "<Script>alert('hi')</scripT>"):
        """
        Given a `url`, it return all XSS vulnerable forms and 
        returns True if any is vulnerable, False otherwise
        """
        # get all the forms from the URL
        forms = self._get_all_forms(url)
        # returning value
        is_vulnerable = False
        # iterate over all forms
        for form in forms:
            form_details = self._get_form_details(form)
            content = self._submit_form(
                form_details, url, js_script).content.decode()
            if js_script in content:
                is_vulnerable = True
        return {
            "is_vulnerable": is_vulnerable,
            "form_detail": form_details
        }
