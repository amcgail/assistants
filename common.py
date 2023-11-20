from openai import OpenAI

import time
import threading
from pathlib import Path
import os
import importlib, inspect
import json
import datetime as dt

from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)

openai_api_key = os.environ.get('OPENAI_API_KEY')
print('openai_api_key', openai_api_key)

def indent(text, amount=4, ch=' '):
    lines = text.splitlines()
    padding = amount * ch
    return '\n'.join(padding + line for line in lines)

def flatten_whitespace(text):
    lines = text.splitlines()

    # first and last lines might be empty
    if not len(lines[0].strip()):
        lines = lines[1:]
    if not len(lines[-1].strip()):
        lines = lines[:-1]

    # calculate the number of spaces at the beginning of each line
    spaces = [len(line) - len(line.lstrip()) for line in lines if len(line.strip())]

    # get rid of min(spaces) spaces at the beginning of each line
    text = '\n'.join(line[min(spaces):] for line in lines)
    return text

oai_client = OpenAI(api_key=openai_api_key)

from .modules import Module, SubModule