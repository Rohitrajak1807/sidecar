import itertools
import json
import re
import sys
from os import path, makedirs
import docker

BUFFER_LIM = 512
LOG_DIR = path.join('/tmp', 'sidecar')

# referenced from
# https://stackoverflow.com/questions/92438/stripping-non-printable-characters-from-a-string-in-python
# regex to remove all control chars
ALL_CHARS = (chr(i) for i in range(sys.maxunicode))
CATEGORIES = {'Cc'}
CONTROL_CHARS = ''.join(
    map(chr, itertools.chain(range(0x00, 0x0a), range(0x0b, 0x0d), range(0x0e, 0x20), range(0x7f, 0xa0))))
CONTROL_CHAR_RE = re.compile('[%s]' % re.escape(CONTROL_CHARS))

# referenced from:
# https://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi-escape-sequences-from-a-string-in-python
# regex to remove terminal colour characters(well, most of it)
ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


def read_config(file='config.json'):
    with open(file) as f:
        config = json.load(f)
    return config


def fill_buffer(stream):
    buffer = bytearray()
    for i, char in enumerate(stream):
        if len(buffer) > BUFFER_LIM:
            break
        buffer += char
    return buffer.decode(errors='ignore')


def sanitize(buffer):
    sanitized = ANSI_ESCAPE.sub('', buffer)
    sanitized = CONTROL_CHAR_RE.sub('', sanitized)
    return sanitized


def unclean_exit(log_stream, file, client):
    log_stream.close()
    file.close()
    client.close()
    exit(2)


def init():
    config = read_config()
    client = docker.APIClient(base_url=f'ssh://{config["host"]}@{config["ip"]}', use_ssh_client=True)
    log_stream = client.logs(config['id'], stream=True, timestamps=True, follow=True)
    makedirs(LOG_DIR, exist_ok=True)
    file_path = path.join(LOG_DIR, f'{config["id"]}.log')
    file_handle = open(file_path, mode='a+')
    return client, log_stream, file_handle


def main():
    client, log_stream, file_handle = init()
    while True:
        try:
            buffer = fill_buffer(log_stream)
            sanitized = sanitize(buffer)
            file_handle.write(sanitized)
        except Exception:
            unclean_exit(log_stream, file_handle, client)


if __name__ == '__main__':
    main()
