# -*- coding: utf-8 -*-

import requests


def get_html(url):
    retry_count = 5
    for i in range(retry_count):
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code != 200:
                continue
            html = resp.content.decode('utf-8')
            return html
        except:
            continue
    return None
