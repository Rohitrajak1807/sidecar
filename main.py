from sys import argv
import itertools
import json
import re
import sys

import docker

BUFFER_LIM = 4096
ALL_CHARS = (chr(i) for i in range(sys.maxunicode))
CATEGORIES = {'Cc'}
CONTROL_CHARS = ''.join(
    map(chr, itertools.chain(range(0x00, 0x0a), range(0x0b, 0x0d), range(0x0e, 0x20), range(0x7f, 0xa0))))
CONTROL_CHAR_RE = re.compile('[%s]' % re.escape(CONTROL_CHARS))


def read_config(file):
    with open(file) as f:
        config = json.load(f)
    return config


def fill_buffer(stream):
    buffer = bytearray()
    for i, char in enumerate(stream):
        if len(buffer) >= BUFFER_LIM:
            break
        buffer += char
    return buffer.decode(errors='ignore')


def strip_control_chars(buffer):
    return CONTROL_CHAR_RE.sub('', buffer)


def main():
    file_path = None
    if len(argv) > 1:
        file_path = argv[1]
    file = file_path or 'config.json'
    config = read_config(file)
    client = docker.APIClient(base_url=f'ssh://{config["host"]}@{config["ip"]}', use_ssh_client=True)
    log_stream = client.logs(config['id'], stream=True, timestamps=True, follow=True)
    with open(f'/tmp/sidecar/sidecar-{config["id"]}.log', mode='a+') as file:
        while True:
            buffer = fill_buffer(log_stream)
            sanitized = strip_control_chars(buffer)
            file.write(sanitized)


if __name__ == '__main__':
    main()
