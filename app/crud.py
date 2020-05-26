import os

from .models import *
from app import db, staticdir
import string
import csv
import numpy as np

def pronounciation_questionbank(): 
    link = os.path.join(staticdir, 'data/words.txt')
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

def grammar_questionbank(): 
    s = np.random.normal(5, 1, 100)

    link = os.path.join(staticdir, 'data/grammar_questionbank.csv')
    f = open(link)
    reader = csv.reader(f)
    next(reader)
    for idx, row in enumerate(reader):
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

        diff = s[idx]
        question = Question(title=title, choices=choices, answer=answer, diff=diff, category_id=1)
        db.session.add(question)
        
    db.session.commit()

def category():
    vocabulary = Category(name='Vocabulary')
    db.session.add(vocabulary)

    db.session.commit()

def create():
    #pronounciation_questionbank()
    grammar_questionbank()