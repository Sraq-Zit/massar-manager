import os
import pickle
import requests

from pathlib import Path

HOME_DIR = str(Path.home())
CACHE_DIR = os.path.join(HOME_DIR, '.cache/massar')
COOKIE_FILE = os.path.join(CACHE_DIR, 'cookies.pkl')

__sess__ = requests.Session()
if os.path.exists(COOKIE_FILE):
    __sess__.cookies = pickle.load(open(COOKIE_FILE, 'rb'))