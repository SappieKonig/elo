#!/usr/bin/env python3

import os
import sys
import json
import argparse

ELO_INITIAL = 1000
CONFIG_PATH = os.path.expanduser('~/.elo/config')
MATCH_HISTORY_DIR = os.path.expanduser('~/.elo/match_history')

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {}
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def save_config(config):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f)

def load_match_history(competition):
    history_path = os.path.join(MATCH_HISTORY_DIR, f'{competition}.txt')
    if not os.path.exists(history_path):
        return []
    with open(history_path, 'r') as f:
        return [line.strip().split(',') for line in f.readlines()]

def save_match_history(competition, history):
    history_path = os.path.join(MATCH_HISTORY_DIR, f'{competition}.txt')
    os.makedirs(os.path.dirname(history_path), exist_ok=True)
    with open(history_path, 'w') as f:
        for match in history:
            f.write(','.join(match) + '\n')

def calculate_elo(rating1, rating2, result):
    K = 32
    expected1 = 1 / (1 + 10 ** ((rating2 - rating1) / 400))
    expected2 = 1 / (1 + 10 ** ((rating1 - rating2) / 400))
    new_rating1 = rating1 + K * (result - expected1)
    new_rating2 = rating2 + K * ((1 - result) - expected2)
    return new_rating1, new_rating2

def update_elo(competition, name1, name2, result):
    history = load_match_history(competition)
    ratings = {name: ELO_INITIAL for name in [name1, name2]}
    for match in history:
        ratings[match[0]], ratings[match[1]] = calculate_elo(ratings[match[0]], ratings[match[1]], int(match[2]))
    new_rating1, new_rating2 = calculate_elo(ratings[name1], ratings[name2], result)
    history.append([name1, name2, str(result)])
    save_match_history(competition, history)
    return new_rating1, new_rating2

def create_user(competition, name):
    history = load_match_history(competition)
    if name not in [match[0] for match in history] and name not in [match[1] for match in history]:
        history.append([name, '', '0'])
        save_match_history(competition, history)

def undo_last_match(competition):
    history = load_match_history(competition)
    if history:
        history.pop()
        save_match_history(competition, history)

def show_ranking(competition):
    history = load_match_history(competition)
    ratings = {name: ELO_INITIAL for name in set([match[0] for match in history] + [match[1] for match in history])}
    for match in history:
        if match[1] != '':
            ratings[match[0]], ratings[match[1]] = calculate_elo(ratings[match[0]], ratings[match[1]], int(match[2]))
    sorted_ratings = sorted(ratings.items(), key=lambda x: x[1], reverse=True)
    max_name_length = max(len(name) for name, _ in sorted_ratings)
    for name, rating in sorted_ratings:
        print(f'{name:<{max_name_length}} {round(rating):>4}')

def main():
    parser = argparse.ArgumentParser(description='ELO Rating System CLI')
    subparsers = parser.add_subparsers(dest='command')

    match_parser = subparsers.add_parser('match', help='Record a match between two players')
    match_parser.add_argument('name1', type=str, help='Name of the first player')
    match_parser.add_argument('name2', type=str, help='Name of the second player')
    match_parser.add_argument('result', type=int, choices=[0, 1], help='Result of the match (0 for name1, 1 for name2)')

    undo_parser = subparsers.add_parser('undo', help='Undo the last match')

    ranking_parser = subparsers.add_parser('ranking', help='Show the ranking of players')

    start_parser = subparsers.add_parser('start', help='Start a new competition')
    start_parser.add_argument('competition', type=str, help='Name of the competition')

    args = parser.parse_args()

    config = load_config()
    competition = config.get('default_competition', 'tt_singles')

    if args.command == 'match':
        name1, name2 = args.name1, args.name2
        if name1 not in [match[0] for match in load_match_history(competition)] and name2 not in [match[1] for match in load_match_history(competition)]:
            create_user(competition, name1)
            create_user(competition, name2)
        update_elo(competition, name1, name2, args.result)
    elif args.command == 'undo':
        undo_last_match(competition)
    elif args.command == 'ranking':
        show_ranking(competition)
    elif args.command == 'start':
        config['default_competition'] = args.competition
        save_config(config)

if __name__ == '__main__':
    main()
