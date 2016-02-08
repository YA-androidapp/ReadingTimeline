#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Changed by: YA <ya.androidapp@gmail.com>
# require:  openjtalk.sh( https://gist.github.com/YA-androidapp/73a44f8ff29a4c9e9efc )
# OS:       for Mac / Linux
# Usage:    ./twList.py ScreenName ListSlug
# 以下を改良

#
# リストのTLを擬似ストリーミングで読み上げさせる
#
# Author:   haya14busa
# URL:      http://haya14busa.com
# Require:  SayKotoeri, Saykana or SayKotoeri2
# License:  MIT License
# OS:       for Mac Only

import tweepy
from datetime import timedelta
import time
from subprocess import call
import re
import sys, codecs

sys.stdout = codecs.getwriter('utf_8')(sys.stdout)
sys.stdin = codecs.getreader('utf_8')(sys.stdin)

owner = ''
slug  = ''
if len(sys.argv) > 2:
    owner = sys.argv[1]
    slug = sys.argv[2]

blockmems = ''

def get_oauth():
    CONSUMER_KEY='**********'
    CONSUMER_SECRET='**********'
    ACCESS_TOKEN_KEY='**********'
    ACCESS_TOKEN_SECRET='**********'

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
    return auth

def str_replace(string):
    string = re.sub('&.+;', ' ', string)
    # remove URL
    string = re.sub('(https?|ftp)(:\/\/[-_.!~*\'()a-zA-Z0-9;\/?:\@&=+\$,%#]+)', 'URL', string)
    # remove quote
    string = re.sub('"', ' ', string)
    string = re.sub("'", ' ', string)
    string = re.sub('\/', ' ', string)
    string = string.replace('\r','')
    string = string.replace('\n','')

    # string = re.sub('RT', 'Retweet', string)
    return string

def showTL(api, read_id):
    try:
        tl = api.list_timeline(owner, slug, count=200, since_id = read_id)
        tl.reverse()
        for status in tl:
            if(not ','+status.author.screen_name+',' in ','+blockmems):
                status.created_at += timedelta(hours=9) # add 9 hours for Japanese time
                print u'---{name}/@{screen}---\n   {text}\nvia {src} {created}'.format(
                        name = status.author.name,
                        screen = status.author.screen_name,
                        text = status.text,
                        src = status.source,
                        created = status.created_at)
                read_text = str_replace(status.text.encode('utf_8'))
                call(['echo "{text}"|~/openjtalk/mei.sh >/dev/null 2>&1'.format(text=read_text)], shell=True)
        else:
            global lastSinceId
            lastSinceId = tl[-1].id
    except Exception, e:
        time.sleep(10)
        pass

def blockmem():
    str = ''
    auth = get_oauth()
    api = tweepy.API(auth_handler=auth)
    for member in tweepy.Cursor(api.blocks).items():
        str = str + member.screen_name + ','
    return str

def main():
    auth = get_oauth()
    blockmems = blockmem()
    api = tweepy.API(auth_handler=auth)
    lastGetTime = time.time() - 8
    global lastSinceId
    lastSinceId = None
    while True:
        if time.time() > lastGetTime + 8:
            lastGetTime = time.time()
            showTL(api, lastSinceId)
        else:
            time.sleep(1)

 
if __name__ == "__main__":
    main()
