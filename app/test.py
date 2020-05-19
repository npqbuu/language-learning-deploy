import os

from .models import *
from app import db
import string


def test():
    basedir = os.path.abspath(os.path.dirname(__file__))
    link = os.path.join(basedir, 'words.txt')
    with open(link, 'r') as f:
        lines = f.read().split(',')
    list_lines = []
    for item in lines:
        list_lines.append(item.translate({ord(c): None for c in string.whitespace}))
    print(len(list_lines))

    for rdword in list_lines:
        rdword = RandomWord(word=rdword)
        db.session.add(rdword)

    db.session.commit()