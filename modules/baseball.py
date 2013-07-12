#!/usr/bin/env python

import datetime
import json
import web

game_list = 'http://gd2.mlb.com/components/game/mlb/year_%s/month_%s/day_%s/master_scoreboard.json'

def find_game(games, team):
    team_game = None
    team_turn = None
    if team:
        team = (team).upper()
    for game in games:
        grab = False
        if game['away_name_abbrev'] == team:
            team_turn = 'away'
            grab = True
        if game['home_name_abbrev'] == team:
            team_turn = 'home'
            grab = True

        if grab:
            team_game = game
    return {'team_game': team_game, 'team_turn': team_turn}


def mlb(jenni, input):
    '''.mlb <team code> -- look up the current score of a MLB team.'''
    txt = input.group(2)
    if not txt:
        return jenni.reply('No input provided.')

    now = datetime.datetime.now() - datetime.timedelta(hours=7)

    ## retrieve the almighty JSON
    scores = game_list % (now.year, str(now.month).zfill(2), str(now.day).zfill(2))
    page = web.get(scores)
    jsons = json.loads(page)
    games = jsons['data']['games']['game']

    ## operation control
    txt_list = txt.split()
    if (txt_list[0]).lower() == 'pbp':
        ## show play by play information
        team = txt_list[1]
        info = find_game(games, team)
        if info['team_game']:
            if 'pbp' in info['team_game']:
                pbp = info['team_game']['pbp']['last']
                if pbp:
                    return jenni.reply(pbp)
        return jenni.reply('Could not find play by play.')
    else:
        ## only team name was given.
        ## show default information
        ## game is in progress
        team = txt_list[0]
        info = find_game(games, team)
        team_game = info['team_game']
        team_turn = info['team_turn']
        if team_game and 'alerts' in team_game:
            info = team_game['alerts']['text']
            return jenni.reply(info)
        elif team_game and team_turn:
            ## game is not in progress
            if 'broadcast' in team_game:
                listen = team_game['broadcast'][team_turn]['radio']
                watch = team_game['broadcast'][team_turn]['tv']
                time_starts = team_game[team_turn + '_time']
                timezone = team_game[team_turn + '_time_zone']
                away = team_game['away_team_city'] + ' ' + team_game['away_team_name']
                home = team_game['home_team_city'] + ' ' + team_game['home_team_name']
                response = '%s at %s, ' % (away, home)
                response += 'starts at %s %s.' % (time_starts, timezone)
                response += ' You can listen on %s and watch on %s.' % (listen, watch)
                jenni.reply(response)
            else:
                status = team_game['status']['status']
                reason = team_game['status']['reason']
                response = 'Game is %s due to %s.' % (status, reason)
                jenni.reply(response)
        else:
            jenni.reply('No information can be ascertained.')
mlb.commands = ['mlb']
mlb.rate = 20
