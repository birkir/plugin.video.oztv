# coding: utf-8
# !/usr/bin/env python

# OZ TV
# Author:  Birkir Gudjonsson (birkir.gudjonsson@gmail.com)
# Port of the popular OZ app for android and ios devices.
#
# TODO: Add genres for vod
#       Add following
#       Add context menu
#       Content type for series, episodes or movies with fanart

import urllib, urllib2, re, xbmcaddon, xbmcplugin, xbmcgui, xbmc
from oz import *

# Plugin constants 
__addonid__ = "plugin.video.oztv"
__addon__ = xbmcaddon.Addon(id=__addonid__)
__language__ = __addon__.getLocalizedString

action_key = None
action_value = None
name = None


def showMenu():
    items = []
    items.append([0, 'Now', 'schedule', ''])
    items.append([1, 'Channels', 'channels', ''])
    items.append([2, 'Movies', 'vod', 'movies'])
    items.append([3, 'TV Shows', 'vod', 'series'])

    for item in items:
        addMenuItem(item[1], item[2], item[3])


def showSchedule():
    channels = getChannels()
    items = getNowAndNext(channels)
    for item in items:
        if item[0] == None or 'content' not in item[0]:
            continue
        content = item[0]['content']
        channel = extractChannel(channels, item[0]['channel'])
        name = channel['name'] + ': ' + parseName(content)
        still = 'http://image.l3.cdn.oz.com/still/' + item[0]['channel'] + '/tn'
        name = name.encode('utf-8').strip()
        offering = channel['offerings'][0]
        addMenuItem(name, 'play_offering', offering['organization'] + ',' + offering['key'], still)


def showChannels():
    channels = getChannels()
    for channel in channels:
        name = channel['name'].encode('utf-8').strip()
        offering = channel['offerings'][0]
        logo = channel['media']['icon']
        addMenuItem(name, 'play_offering', offering['organization'] + ',' + offering['key'], logo)


def showVod(params):
    params = params.split(',')
    type = params[0]
    page = 0
    if len(params) > 1:
        page = int(params[1])

    addMenuItem(' # Home', '', '')

    if page > 0:
        addMenuItem(' < Previous page'.encode('utf-8'), 'vod', type + ',' + str(page - 1))

    addMenuItem(' > Next page'.encode('utf-8'), 'vod', type + ',' + str(page + 1))

    items = getVodWithType(type, page)
    for item in items:
        if 'series' in item:
            series = item['series']
            name = series['title']
            still = parseStill(series)
            addMenuItem(name.encode('utf-8').strip(), 'vod_series', series['id'], still)
        else:
            content = item['content']
            offering = item['offerings'][0]
            name = parseName(content)
            still = parseStill(content)
            addMenuItem(name.encode('utf-8').strip(), 'play_offering', offering['organization'] + ',' + offering['key'],
                still)


def showVodSeries(series):
    episodes = getVodSeriesEpisodes(series)
    for episode in episodes:
        content = episode['content']
        name = parseName(content)
        offering = episode['offerings'][0]
        still = parseStill(content)
        addMenuItem(name.encode('utf-8').strip(), 'play_offering', offering['organization'] + ',' + offering['key'],
            still)


def playOffering(param):
    data = param.split(',')
    offering = getOffering(data[0], data[1])
    if 'message' in offering:
        showDialog(offering['message'])
    else:
        xbmc.Player().play(offering['url'])


def parseName(content):
    name = content['title'] + ' '
    if 'season_number' in content:
        season_number = content['season_number']
        episode_number = content['episode_number']
        if season_number < 10:
            season_number = str('0') + str(season_number)
        if episode_number < 10:
            episode_number = str('0') + str(episode_number)
        name += 'S' + str(season_number) + 'E' + str(episode_number)
    elif 'number_of_episodes' in content:
        name += str(content['episode_number']) + '/' + str(content['number_of_episodes'])
    elif 'year' in content:
        name += '(' + str(content['year']) + ')'
    return name


def parseStill(item):
    if 'stills' in item:
        for still in item['stills']:
            return 'https://oz-img.global.ssl.fastly.net' + still + '?width=340'
    return ''


def extractChannel(channels, channel):
    for chan in channels:
        if chan['key'] == channel:
            return chan


def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]

    return param


def addMenuItem(name, action_key, action_value, iconimage='DefaultFolder.png'):
    is_folder = True
    if action_key == 'play_offering':
        is_folder = False
    u = sys.argv[0] + "?action_key=" + urllib.quote_plus(action_key) + "&action_value=" + str(
        action_value) + "&name=" + urllib.quote_plus(name)
    liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage='')
    liz.setInfo(type="Video", infoLabels={"Title": name})
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=is_folder)


def showDialog(message):
    dialog = xbmcgui.Dialog()
    dialog.ok('OZ TV', message)


params = get_params()
try:
    action_key = urllib.unquote_plus(params["action_key"])
    action_value = urllib.unquote_plus(params["action_value"])
    name = urllib.unquote_plus(params["name"])
except:
    pass

if action_key is None:
    showMenu()
elif action_key == 'schedule':
    showSchedule()
elif action_key == 'channels':
    showChannels()
elif action_key == 'vod':
    showVod(action_value)
elif action_key == 'vod_series':
    showVodSeries(action_value)
elif action_key == 'play_offering':
    playOffering(action_value)

xbmcplugin.endOfDirectory(int(sys.argv[1]))