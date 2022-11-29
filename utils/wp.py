import requests
import threading
import time
import json
import random
from unsafe.utils.strings import wp_plugins
from unsafe.exceptions import NotWordpress, SiteNotFound, UsersFileNotFound, NotFoundData

plugins_list = []
counter = 0


class Wordpress:

    def __init__(self):
        pass

    def wp_checker(self, domain: str):
        if 'http://' in domain:
            domain = domain.replace('http://', '')
        elif 'https://' in domain:
            domain = domain.replace('https://', '')
        else:
            domain = domain
        try:
            t = requests.get("http://"+domain)
            if '/wp-content/' in t.text or '/wp-contents/' in t.text or '/wp-includes/' in t.text:
                return True
            s = requests.get("http://"+domain+"/wp-content/plugins/")
            if s.history:
                return False
        except requests.exceptions.ConnectionError:
            return False
        if s.status_code == 404 or s.status_code == 500 or 299 < s.status_code < 305:
            return False
        elif s.status_code == 403 or 199 < s.status_code < 299:
            return True
        return True

    def get_user(self, domain: str):
        try:
            if 'http://' in domain:
                domain = domain.replace('http://', '')
            elif 'https://' in domain:
                domain = domain.replace('https://', '')
            else:
                domain = domain
            if not self.wp_checker(domain):
                raise NotWordpress(domain)
        except:
            pass
        try:
            r = requests.get("https://"+domain+'/wp-json/wp/v2/users/').text
            j = json.loads(r)
            Count = len(j) - 1
            users_list = []
            cn = 0
            User = ''
            for Val in j:
                Split = '\n'
                if Count == cn:
                    Split = ''
                U = j[cn]['slug']
                if not U == '':
                    User += U+Split
                cn += 1
            if User == '':
                raise NotFoundData
            return User.split()
        except json.decoder.JSONDecodeError:
            raise NotWordpress(domain)
        except requests.exceptions.ConnectionError:
            raise SiteNotFound(domain)
        except KeyError:
            raise UsersFileNotFound
        except Exception as e:
            raise e

    def send_request(self, plugins: list, url: str, timeout: int, proxy: list | str = None):
        global plugins_list
        global counter

        if proxy and type(proxy) == list:
            prx = random.choice(proxy)
            proxies = {"https": f"{prx}", "http": f"{prx}"}
        elif proxy and type(proxy) == str:
            proxies = {"https": f"{proxy}", "http": f"{proxy}"}
        else:
            proxies = {}
        for plus in plugins:
            counter += 1
            try:
                if proxies == {}:
                    r = requests.get(
                        f"http://{url}/wp-content/plugins/{plus}/", timeout=timeout)
                else:
                    r = requests.get(
                        f"http://{url}/wp-content/plugins/{plus}/", timeout=timeout, proxies=proxies)
                if r.status_code == 200:
                    plugins_list.append(r.url)
                else:
                    pass
            except (requests.exceptions.ProxyError, requests.exceptions.ConnectTimeout):
                pass
            except Exception as e:
                raise e

    def plugin_scanner(self, url: str, timeout: int = 3, workers: int = 3, proxy: list | str = None):
        if not self.wp_checker(url):
            raise NotWordpress(url)
        if 'http://' in url:
            url = url.replace('http://', '')
        elif 'https://' in url:
            url = url.replace('https://', '')
        else:
            url = url

        if workers == 1:
            t = threading.Thread(target=self.send_request, args=(
                wp_plugins, url, timeout, proxy))
            t.start()
            t.join()
        elif workers == 2:
            t = threading.Thread(target=self.send_request, args=(
                wp_plugins[0:400], url, timeout, proxy))
            t.start()
            t2 = threading.Thread(target=self.send_request, args=(
                wp_plugins[400:799], url, timeout, proxy))
            t2.start()
            t2.join()
            t.join()

        elif workers == 3:
            t = threading.Thread(target=self.send_request, args=(
                wp_plugins[0:266], url, timeout, proxy))
            t.start()
            t2 = threading.Thread(target=self.send_request, args=(
                wp_plugins[266:532], url, timeout, proxy))
            t2.start()
            t3 = threading.Thread(target=self.send_request, args=(
                wp_plugins[532:799], url, timeout, proxy))
            t3.start()
            t3.join()
            t.join()

        elif workers == 4:
            t = threading.Thread(target=self.send_request, args=(
                wp_plugins[0:200], url, timeout, proxy))
            t.start()
            t2 = threading.Thread(target=self.send_request, args=(
                wp_plugins[200:400], url, timeout, proxy))
            t2.start()
            t3 = threading.Thread(target=self.send_request, args=(
                wp_plugins[400:600], url, timeout, proxy))
            t3.start()
            t4 = threading.Thread(target=self.send_request, args=(
                wp_plugins[600:799], url, timeout, proxy))
            t4.start()
            t4.join()
            t.join()

        elif workers == 5:
            t = threading.Thread(target=self.send_request, args=(
                wp_plugins[0:160], url, timeout, proxy))
            t.start()
            t2 = threading.Thread(target=self.send_request, args=(
                wp_plugins[160:320], url, timeout, proxy))
            t2.start()
            t3 = threading.Thread(target=self.send_request, args=(
                wp_plugins[320:480], url, timeout, proxy))
            t3.start()
            t4 = threading.Thread(target=self.send_request, args=(
                wp_plugins[480:640], url, timeout, proxy))
            t4.start()
            t5 = threading.Thread(target=self.send_request, args=(
                wp_plugins[640:799], url, timeout, proxy))
            t5.start()
            t5.join()
            t.join()

        global plugins_list
        if plugins_list == []:
            raise NotFoundData

        else:
            return plugins_list
