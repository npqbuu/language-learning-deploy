import os

from .models import *
from app import db
import string
import csv
import numpy as np


def pronounciation_questionbank():
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

def csv_to_psql(link, category_id): 
    
    f = open(link)
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        title = row[0]
        choices = row[1:5]
        while '' in choices:
            choices.remove('')
        if row[5] == 'A':
            answer = 0
        elif row[5] == 'B':
            answer = 1
        elif row[5] == 'C':
            answer = 2
        else:
            answer = 3

        diff = int(row[6])
        question = Question(title=title, choices=choices, answer=answer, diff=diff, category_id=category_id)
        db.session.add(question)
        
    db.session.commit()