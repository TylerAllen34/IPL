#!/usr/bin/env python3
"""Check this Mini package against the supplied start or solution contract.

This file is distributed as CHECK_PROJECT.py beside CMakeLists.txt.
Requires Python 3.8+ and an already built minic, using only the standard library.
The compiler/build process remains C++/CMake and needs no Python.
Verified on macOS. Timeout cleanup covers the process group on POSIX;
on Windows it stops only the direct child (descendant cleanup is unverified).
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

COMMANDS = {'tokens', 'ast', 'lower', 'check', 'cpp', 'run'}
EXPECTED_KEYS = {'exit', 'stdout', 'stderr', 'stdout_contains', 'stderr_contains',
                 'stdout_not_contains', 'stderr_not_contains'}


def run_process(argv, root, timeout):
    started = time.monotonic()
    process = subprocess.Popen(argv, cwd=str(root), stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True,
                               encoding='utf-8', errors='replace',
                               start_new_session=(os.name != 'nt'))
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        if os.name != 'nt':
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        else:
            process.kill()
        stdout, stderr = process.communicate()
    return {'exit': process.returncode, 'stdout': stdout, 'stderr': stderr,
            'timeout': timed_out, 'seconds': round(time.monotonic() - started, 3)}


def mismatches(actual, expected):
    errors = []
    if actual['timeout']:
        errors.append('execution timed out')
    if actual['exit'] != expected['exit']:
        errors.append('exit status: expected {}, got {}'.format(expected['exit'], actual['exit']))
    for stream in ('stdout', 'stderr'):
        # communicate() normalizes native CRLF; source/compiler semantics do not change.
        observed = actual[stream]
        if stream in expected and observed != expected[stream]:
            errors.append('{}: expected {!r}, got {!r}'.format(stream, expected[stream], observed[:2000]))
        for suffix, positive in (('_contains', True), ('_not_contains', False)):
            value = expected.get(stream + suffix, [])
            for fragment in ([value] if isinstance(value, str) else value):
                if (fragment in observed) != positive:
                    errors.append('{} {} {!r}'.format(stream, 'must contain' if positive else 'must not contain', fragment))
    return errors


def main():
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', required=True, choices=('start', 'solution'))
    parser.add_argument('--compiler', required=True,
                        help='Path to your built minic (relative to the current working directory)')
    parser.add_argument('--timeout', type=float, default=20.0, help='Seconds per command (default 20)')
    parser.add_argument('--json-report', type=Path, help='Optional detailed result file')
    args = parser.parse_args()
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error('--timeout must be finite and positive')
    compiler = Path(args.compiler).expanduser().resolve()
    if not compiler.is_file():
        parser.error('compiler not found: {}; build minic first'.format(compiler))
    try:
        manifest = json.loads((root / 'checks/CASES.json').read_text(encoding='utf-8'))
        if manifest['schema_version'] != 1:
            raise ValueError('unsupported checks schema')
        checks = manifest['checks']
        if not checks or len({c['id'] for c in checks}) != len(checks):
            raise ValueError('empty checks or duplicate ids')
        for filename, digest in manifest['fixture_sha256'].items():
            relative = Path(filename)
            if relative.name != filename or relative.suffix != '.mini':
                raise ValueError('invalid fixture path: ' + filename)
            fixture = root / 'inputs' / filename
            if hashlib.sha256(fixture.read_bytes()).hexdigest() != digest:
                raise ValueError('changed fixture: {} (use a separate file for experiments)'.format(fixture))
        for case in checks:
            if case['command'] not in COMMANDS or case['file'] not in manifest['fixture_sha256']:
                raise ValueError('invalid check: ' + case['id'])
            for mode in ('start', 'solution'):
                expected = case[mode]
                if not isinstance(expected.get('exit'), int) or set(expected) - EXPECTED_KEYS:
                    raise ValueError('invalid expectations: ' + case['id'])
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.error(str(error))
    print('Mini stage {:02d}: {} contract'.format(manifest['week'], args.mode))
    print('PASS includes errors with the specified phase, message and exit status.')
    records = []
    for case in checks:
        argv = [str(compiler), case['command'], str(root / 'inputs' / case['file'])]
        try:
            actual = run_process(argv, root, args.timeout)
        except OSError as error:
            parser.error('cannot run compiler: ' + str(error))
        errors = mismatches(actual, case[args.mode])
        record = dict(actual, id=case['id'], command=argv, expected=case[args.mode],
                      passed=not errors, mismatches=errors)
        records.append(record)
        print('{} {}'.format('PASS' if not errors else 'FAIL', case['id']))
        for error in errors:
            print('  ' + error)
    passed = all(record['passed'] for record in records)
    print('{}: {}/{} checks match the {} contract.'.format(
        'PASS' if passed else 'FAIL', sum(r['passed'] for r in records), len(records), args.mode))
    if args.mode == 'start':
        print('A passing start contract confirms the supplied unfinished state, not completion.')
    else:
        print('Use these results to check your work, then try an example of your own and explain its output.')
    if args.json_report:
        args.json_report.parent.mkdir(parents=True, exist_ok=True)
        args.json_report.write_text(json.dumps({'week':manifest['week'], 'mode':args.mode,
            'passed':passed, 'compiler':str(compiler), 'checks':records}, indent=2) + '\n', encoding='utf-8')
    return 0 if passed else 1


if __name__ == '__main__':
    sys.exit(main())
