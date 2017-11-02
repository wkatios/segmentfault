#coding=utf-8
#__author__=katios

import time
import copy
import urllib
import requests
from bs4 import BeautifulSoup

from elasticsearch import Elasticsearch
from elasticsearch import helpers

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def get_tag(page_num):
    result = requests.get('http://segmentfault.com/tags/all?page=%s'%page_num)
    return result.content

def process_tag(content):
    soup = BeautifulSoup(content,'lxml')
    sections = soup.find_all('section')
    info = {}
    values = []
    for section in sections:
        tag = section.div.h2.a.text
        tag_instruction = section.div.p.text
        follows = section.div.div.strong.text
        url = 'https://segmentfault.com'+section.div.h2.a['href']
        info['url'] = urllib.unquote(url)
        info['tag'] = tag
        info['tag_instruction'] = tag_instruction
        info['follows'] = int(follows)
        deepcopy_info = copy.deepcopy(info)
        values.append({
            "_index": 'segmentfault',
            "_type": 'tag',
            # "_op_type": "create",
            "_source": deepcopy_info
        })
    return values

def es_client(server):
    es = Elasticsearch(server)
    es.indices.create(index='segmentfault',ignore = 'ignore_unavailable')
    return es


if __name__ == "__main__":
    starttime= time.time()
    es = es_client("192.168.1.1")
    for page_num in xrange(1,570):
        content = get_tag(page_num)
        values = process_tag(content)
        helpers.bulk(es, values)
    print time.time()-starttime