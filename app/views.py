import os

# Flask
from flask import Flask, render_template, request, redirect, session, url_for
from flask import current_app as app
from flask_login import login_required, current_user

# SQL Querry
from sqlalchemy.sql import func
from sqlalchemy.orm import load_only

# Import components
from .models import *
from .forms import *
from .test import *

# Algorithm
from .algorithm import CAT, generate_bank, recognize_speech
import speech_recognition as sr
import urllib
from bs4 import BeautifulSoup
import numpy as np

@app.route("/")
def index():
    session.clear()

    # Test zone-----------------
    session.clear()
    session['all_questions'] = Question.query.filter(Question.category_id == '1').all()
    bank = generate_bank(len(session['all_questions']))
    bank[:, 1] = [question.diff for question in session['all_questions']]
    session['items'] = bank
    session['cat'] = CAT(session['items'])

    (_stop, session['item_index']) = session['cat'].item_selection() # Get first item
    session['cat'].administered_items.append(session['item_index'])
    session['progress'] = 0
    session['theta'] = session['cat'].thetas[0]
    # --------------------------

    return render_template("index.html")

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)

@app.route("/adaptivetest", methods=["GET", "POST"])
def adaptivetest():
    # Question variables
    session['question'] = session['all_questions'][session['item_index']]
    form = AnswerForm()
    form.answer.choices = [(index, choice) for index, choice in enumerate(session['question'].choices)]
    title = session['question'].title

    if form.validate_on_submit():
        if form.answer.data == session['question'].answer: # Get user respone for current question
            response = True
        else:
            response = False

        session['cat'].responses.append(response)
        session['cat'].item_administration()

        (_stop, session['item_index']) = session['cat'].item_selection() # Get item
        if _stop:
                return redirect('/result')

        session['cat'].administered_items.append(session['item_index']) # Add new item to list
        session['progress'] = (len(session['cat'].thetas) - 1) * 10 # Update progess
        session['theta'] = session['cat'].thetas[-1] # Update theta

        return redirect(url_for('adaptivetest'))
            
    # Render Template
    return render_template("adaptivetest.html", title = title, theta = session['theta'], progress = session['progress'], form = form)

@app.route("/result")
def result():
    theta = session['cat'].thetas[-1]
    return render_template("result.html", theta = theta)

@app.route("/pronounciation", methods=['GET', 'POST'])
def pronounciation():
    if request.method == "GET":
        result = ''
        session['word'] = RandomWord.query.options(load_only('id')).offset(
            func.floor(
                func.random() *
                db.session.query(func.count(RandomWord.id))
            )
        ).limit(1).all()[0].word.capitalize() 

    return render_template("pronounciation.html", word = session['word'], result = result)

@app.route("/checkpronounciation", methods=['POST'])
def checkpronounciation():
    # Open file and write binary (blob) data
    with open(url_for('static', filename='pronounciation_user.wav'), 'wb') as f:
        f.write(request.data)
    # Speech recognition
    response = recognize_speech(sr.Recognizer(), sr.AudioFile(url_for('static', filename='pronounciation_user.wav')))
    session['answer'] = response['transcription']
    
    return redirect('/result_voice')

@app.route("/result_voice")
def result_voice():
    word = session['word']
    answer = session['answer']
    if answer != None:
        result = (word.lower() == answer.lower())
    else:
        result = "Unable to recognize speech"

    # Get correct pronounciation mp3 file from online dictionary Lexico
    url = 'https://www.lexico.com/en/definition/' + word.lower()
    page = urllib.request.urlopen(url)
    soup = BeautifulSoup(page, features='lxml')
    list_audios = soup.find_all('audio')
    for link in list_audios:
        try:
            urllib.request.urlretrieve(link['src'], url_for('static', filename='pronounciation_dict.wav'))
            break
        except:
            print('Broken link')

    return render_template("result_voice.html", result = result, word= word, answer = answer)
