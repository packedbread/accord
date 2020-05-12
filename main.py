#!/usr/bin/env python
import argparse
import ast
import requests
import time
import random


def add_arguments(parser: argparse.ArgumentParser):
    parser.add_argument('--lines-file', default='movie_lines.txt')
    parser.add_argument('--conversations-file', default='movie_conversations.txt')
    parser.add_argument('--character-delay', type=float, default=0.05)
    parser.add_argument('--message-delay', type=float, default=2)
    parser.add_argument('webhook_url')


def main(args: argparse.Namespace):
    lines = load_lines(args.lines_file)
    conversations = load_conversations(args.conversations_file)
    conversation = get_random_conversation(lines, conversations)

    print_conversation(conversation, args.message_delay, args.character_delay)
    send_conversation(conversation, args.message_delay, args.character_delay, args.webhook_url)


def load_lines(lines_file):
    lines = {}
    with open(lines_file, 'r', encoding='utf-8') as file:
        while True:
            line = file.readline()
            if line == '':
                break
            parts = line.split(' +++$+++ ')
            if len(parts) != 5:
                parts.append('')
            lines[parts[0]] = {
                'speaker': parts[3].title(),
                'text': parts[4].strip(),
            }
    return lines


def load_conversations(conversations_file):
    conversations = []
    with open(conversations_file, 'r', encoding='utf-8') as file:
        while True:
            line = file.readline()
            if line == '':
                break
            parts = line.split(' +++$+++ ')
            lines = ast.literal_eval(parts[3])
            conversations.append(lines)
    return conversations


def get_random_conversation(lines, conversations):
    conv = random.choice(conversations)
    conversation = []
    for line_id in conv:
        conversation.append(lines[line_id])
    return conversation


def print_conversation(conversation, message_delay, character_delay):
    for line in conversation:
        print('sender: {}, text: {}, delay: {}'.format(line['speaker'], line['text'], message_delay + character_delay * len(line['text'])))


def send_conversation(conversation, message_delay, character_delay, webhook_url):
    characters = set(line['speaker'] for line in conversation)
    offset = random.randint(0, 200)
    character_avatar_urls = {character: 'http://dedgan.herokuapp.com/img/{}'.format(offset + i) for i, character in enumerate(characters)}

    def build_message_item(text, speaker):
        return {
            'content': text,
            'username': speaker,
            'avatar_url': character_avatar_urls[speaker],
        }

    for line in conversation:
        delay = message_delay + character_delay * len(line['text'])
        message_item = build_message_item(line['text'], line['speaker'])
        requests.post(webhook_url, json=message_item)
        time.sleep(delay)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)  # noqa
    add_arguments(parser)
    args = parser.parse_args()
    main(args)
