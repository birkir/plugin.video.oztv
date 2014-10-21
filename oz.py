# coding: utf-8
#!/usr/bin/env python
import urllib, urllib2, re, xbmcaddon, xbmcplugin, xbmcgui, xbmc, base64, os
import requests
import simplejson as json

waypoint = 'https://api.oz.com/v1/'
user_agent = 'OZDroidz/1.5.0.3 (XBMC; Android 4.4.2)'
xsecret = 'b89b0060-cece-11e3-b6e1-7f4ae3f97677'
xtoken = 'ozmobileandroid'

def request(path, username = '', password = ''):
	session = requests.session()
	session.headers.update({'User-Agent': user_agent})
	session.headers.update({'x-application-secret': xsecret})
	session.headers.update({'x-application-token': xtoken})

	if path == 'authorizations':
		session.auth = (username, password)
	else:
		token = readAuthToken()
		session.headers.update({'Authorization': 'Bearer ' + token})

	response = session.get(waypoint+path)

	return json.JSONDecoder('utf8').decode(response.text)

def writeAuthToken(token):
	f = open(os.path.join(xbmc.translatePath( "special://profile" ), 'token.txt'),'w');
	f.write(token)
	f.close()

def readAuthToken():
	token = ''
	try:
		f = open(os.path.join(xbmc.translatePath( "special://profile" ), 'token.txt'),'r');
		token = f.readline()
		f.close()
	except IOError:
		token = getAccessToken()
		if token:
			writeAuthToken(token)
		else:
			showDialog('Invalid Credentials')
	return token

def getAccessToken():
	addon = xbmcaddon.Addon('plugin.video.oztv')
	username = addon.getSetting('username')
	password = addon.getSetting('password')
	response = request('authorizations', username, password)
	if 'code' in response and response['code'] == 'InvalidCredentials':
		return False
	else:
		return response[0]['access_token']

def getUser():
	return request('users/me')

def getChannels():
	return request('indexes/user_channels')

def getChannel(organization, channel):
	return request('indexes/user_channel/' + organization + '/' + channel)

def getNowAndNext(channels):
	items = []
	for channel in channels:
		items.append(channel['organization'] + ':' + channel['key'])
	return request('schedule/nowandnext?channels=' + ','.join(items))

def getOffering(organization, key):
	return request('offering/' + organization + '/' + key + '/token')

def getVod():
	return request('vod')

def getVodWithType(type, page):
	return request('vod?type=' + str(type) + '&items=20&page=' + str(page))

def getVodSeriesEpisodes(series):
	return request('vod/series/'+str(series)+'/episodes')

def getVodCategories():
	return request('vod/categories')

def getVodProviders():
	return request('vod/providers')

def getFollowing():
	return request('user/following')
