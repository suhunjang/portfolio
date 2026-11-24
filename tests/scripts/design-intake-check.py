#!/usr/bin/env python3
"""Claude Design bundle intake check (설계 §11.1). 표준 라이브러리만, 읽기 전용.

사용: python3 -I tests/scripts/design-intake-check.py [--fixture <path>]
순서: unsafe(symlink·non-regular) → files mismatch → hash mismatch → summary mismatch. 실패 exit 1, 통과 exit 0.
"""
import hashlib
import json
import os
import stat
import sys

DEFAULT_FIXTURE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fixtures', 'claude-design-intake.json')


def fail(msg):
    print(f'design-intake: {msg}')
    sys.exit(1)


def lstat_mode(p):
    try:
        return os.lstat(p).st_mode
    except FileNotFoundError:
        return None


def read_regular(p):
    try:
        fd = os.open(p, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except OSError:
        fail(f'unsafe:{p}')
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            fail(f'unsafe:{p}')
        chunks = []
        while True:
            b = os.read(fd, 1 << 16)
            if not b:
                break
            chunks.append(b)
        return b''.join(chunks)
    finally:
        os.close(fd)


def parse_args(argv):
    if not argv:
        return DEFAULT_FIXTURE
    if len(argv) == 2 and argv[0] == '--fixture' and argv[1]:
        return argv[1]
    fail('usage: design-intake-check.py [--fixture <path>]')


def load_fixture(p):
    try:
        fx = json.loads(read_regular(p).decode('utf-8'))
    except (ValueError, UnicodeDecodeError):
        fail('bad fixture')
    if not isinstance(fx, dict):
        fail('bad fixture')
    files = fx.get('files')
    if (not isinstance(fx.get('summaryPath'), str) or not isinstance(fx.get('bundleDir'), str)
            or not isinstance(files, dict) or len(files) != 9
            or not all(isinstance(v, str) for v in files.values())):
        fail('bad fixture')
    return fx


def main(argv):
    fx = load_fixture(parse_args(argv))
    summary_path, bundle_dir, files = fx['summaryPath'], fx['bundleDir'], fx['files']

    mode = lstat_mode(summary_path)
    if mode is None or not stat.S_ISREG(mode):
        fail(f'unsafe:{summary_path}')
    mode = lstat_mode(bundle_dir)
    if mode is None or not stat.S_ISDIR(mode):
        fail(f'unsafe:{bundle_dir}')
    for name in files:
        p = os.path.join(bundle_dir, name)
        mode = lstat_mode(p)
        if mode is not None and not stat.S_ISREG(mode):
            fail(f'unsafe:{p}')

    if sorted(os.listdir(bundle_dir)) != sorted(files):
        fail('files mismatch')

    for name, sha in files.items():
        if hashlib.sha256(read_regular(os.path.join(bundle_dir, name))).hexdigest() != sha:
            fail(f'hash mismatch:{name}')

    try:
        lines = read_regular(summary_path).decode('utf-8').splitlines()
    except UnicodeDecodeError:
        fail(f'unsafe:{summary_path}')
    for name, sha in files.items():
        needle = f'`{name}` — `{sha}`'
        if not any(needle in line for line in lines):
            fail(f'summary mismatch:{name}')

    print('design-intake: OK')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
