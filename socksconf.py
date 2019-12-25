import requests
from lxml.html import fromstring
from itertools import cycle


def get_socks():
    url = 'https://free-proxy-list.net'
    response = requests.get(url)
    parser = fromstring(response.text)
    _socks = set()

    for elem in parser.xpath('//tbody/tr')[:10]:
        if elem.xpath('.//td[7][contains(text(),"yes")]'):
            proxy = ":".join([elem.xpath('.//td[1]/text()')[0], elem.xpath('.//td[2]/text()')[0]])
            _socks.add(proxy)
    return _socks


def proxy_checker(socks = set()):
    socks_pool = cycle(socks)
    url = 'https://httpbin.org/ip'
    socks_list = set()
    counter = 0
    print('\n\nChecking proxies...')

    for i in range(1, 11):
        proxy = next(socks_pool)
        try:
            response = requests.get(url, proxies={"http": proxy, "https": proxy}, timeout=7)
            if response.status_code == 200:
                socks_list.add(proxy)
                counter+=1
                print('\r[*] {}/10 proxy is clear'.format(counter), end='')
        except:
            pass
    if counter > 0:
        return socks_list
    else:
        print('\n\n[X] No one proxy is clear. Try later')
        exit()