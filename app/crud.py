import os

from .models import *
from app import db, staticdir
import string
import csv
import numpy as np
import urllib
from bs4 import BeautifulSoup
import re
import requests
import random

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

def rhyme_questionbank(): 
    s = np.random.normal(5, 1, 100)

    link = os.path.join(staticdir, 'data/rhyme_questionbank.csv')
    f = open(link)
    reader = csv.reader(f)
    next(reader)
    for idx, row in enumerate(reader):
        title = 'Choose the word that sounds differently than the others'
        choices = row[1:5]
        while '' in choices:
            choices.remove('')
        answer = int(row[5])
        diff = int(float(row[6]))
        question = Question(title=title, choices=choices, answer=answer, diff=diff, category_id=2)
        db.session.add(question)
        
    db.session.commit()

def vocabulary_questionbank():
    headers = {
    'x-rapidapi-host': "twinword-word-association-quiz.p.rapidapi.com",
    'x-rapidapi-key': "f9e88b40a3mshe89fe995823038bp1f4ab2jsn4f97b67d0ad0"
    }
    url = "https://twinword-word-association-quiz.p.rapidapi.com/type1/"
    
    for time in range(3):
        for level in range(1, 11):
            querystring = {"area":"overall","level":str(level)}
            response = requests.request("GET", url, headers=headers, params=querystring)
            data = response.json()
            for question in data['quizlist']:
                title = 'Which word is most closely related to this set: ' + ', '.join(map(str, question['quiz']))
                diff = level
                choices = question['option']
                answer = question['correct'] - 1

                question = Question(title=title, choices=choices, answer=answer, diff=diff, category_id=2)
                db.session.add(question)
    
    db.session.commit()

def create():
    #pronounciation_questionbank()
    #grammar_questionbank()
    #vocabulary_questionbank()
    #rhyme_questionbank()
    
    return None
