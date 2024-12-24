import argparse
import logging
import os
import re
import pathlib
from typing import List, Dict, Optional


ENV_VAR_PREFIX = __package__.upper()


def add_env_argument(env, parser, *args, **kwargs):
    stored = parser.add_argument(*args, **kwargs)
    env_key = '_'.join((
        ENV_VAR_PREFIX,
        re.sub(r'_+', '_', re.sub(r'\W', '_', stored.dest.upper())).strip('_')
    ))
    stored.default = env.get(env_key, stored.default)


def get_args(argv: Optional[List[str]]=None, env: Optional[Dict[str,str]]=None):
    if env is None:
        env = os.environ
    parser = argparse.ArgumentParser()
    add_env_argument(
        env,
        parser,
        '--database',
        default='sign.sqlite3',
        type=pathlib.Path,
    )
    add_env_argument(
        env,
        parser,
        '--log-level',
        default='INFO',
    )
    add_env_argument(
        env,
        parser,
        '--device',
        required=True,
    )
    return parser.parse_args(argv)
