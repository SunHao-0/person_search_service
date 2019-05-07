import urllib2
import json


def rest_call(url):
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    return json.loads(response.read())


def data_to_txt():
    pass
