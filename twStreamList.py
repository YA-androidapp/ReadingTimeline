#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Listをストリーミングで読み上げさせる
# Changed by: YA <ya.androidapp@gmail.com>
# require:  openjtalk.sh( https://gist.github.com/YA-androidapp/73a44f8ff29a4c9e9efc )
# OS:       for Mac / Linux
# Usage:    ./twStreamList.py ScreenName ListSlug
# 以下を改良

#
# Timelineをストリーミングで読み上げさせる
# 
# Author:   haya14busa
# URL:      http://haya14busa.com
# require:  SayKotoeri, Saykana or SayKotoeri2
# OS:       for Mac Only
# Link:     [twitterをターミナル上で楽しむ(python)](http://www.nari64.com/?p=200)

import tweepy
from tweepy import  Stream, TweepError
from datetime import timedelta
import time
import logging
import urllib
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

listmems = ''
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

class CustomStreamListener(tweepy.StreamListener):

    def on_status(self, status):

        auth = get_oauth()
        api = tweepy.API(auth_handler=auth)
        if(','+status.author.screen_name+',' in ','+listmems):
            if(not ','+status.author.screen_name+',' in ','+blockmems):
                try:
                    status.created_at += timedelta(hours=9) # add 9 hours for Japanese time
                    print u'---{name}/@{screen}---\n   {text}\nvia {src} {created}'.format(
                            name = status.author.name,
                            screen = status.author.screen_name,
                            text = status.text,
                            src = status.source,
                            created = status.created_at)
                    read_text = str_replace(status.text.encode('utf-8'))
                    call(['echo "{text}"|~/openjtalk/mei.sh >/dev/null 2>&1'.format(text=read_text)], shell=True)
                except Exception, e:
                    print >> sys.stderr, 'Encountered Exception:', e
                    pass

    def on_error(self, status_code):
        print >> sys.stderr, 'Encountered error with status code:', status_code
        return True # Don't kill the stream

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True # Don't kill the stream


class UserStream(Stream):

    def user_stream(self, follow=None, track=None, async=False, locations=None):
        self.parameters = {"delimited": "length", }
        self.headers['Content-type'] = "application/x-www-form-urlencoded"

        if self.running:
            raise TweepError('Stream object already connected!')

        self.scheme = "https"
        self.host = 'userstream.twitter.com'
        self.url = '/2/user.json'

        if follow:
           self.parameters['follow'] = ','.join(map(str, follow))
        if track:
            self.parameters['track'] = ','.join(map(str, track))
        if locations and len(locations) > 0:
            assert len(locations) % 4 == 0
            self.parameters['locations'] = ','.join(['%.2f' % l for l in locations])

        self.body = urllib.urlencode(self.parameters)
        logging.debug("[ User Stream URL ]: %s://%s%s" % (self.scheme, self.host, self.url))
        logging.debug("[ Request Body ] :" + self.body)
        self._start(async)

def blockmem():
    str = ''
    auth = get_oauth()
    api = tweepy.API(auth_handler=auth)
    for member in tweepy.Cursor(api.blocks).items():
        str = str + member.screen_name + ','
    return str

def listmem():
    str = owner+','
    auth = get_oauth()
    api = tweepy.API(auth_handler=auth)
    for member in tweepy.Cursor(api.list_members, owner, slug).items():
        str = str + member.screen_name + ','
    global listmems
    listmems = str
    return str

def main():
    auth = get_oauth()
    blockmems = blockmem()
    listmems = listmem()
    stream = UserStream(auth, CustomStreamListener())
    stream.timeout = None
    stream.track=listmems
    stream.user_stream()

if __name__ == "__main__":
    main()
