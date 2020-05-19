import csv
from models import *

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