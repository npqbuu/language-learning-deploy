import os
import io

# Flask
from flask import Flask, render_template, request, redirect, session, url_for, send_from_directory
from flask import current_app as app
from flask_login import login_required, current_user

# SQL Querry
from sqlalchemy.sql import func
from sqlalchemy.orm import load_only

# Import components
from .models import *
from .forms import *
from .crud import create
from app import basedir, staticdir, BUCKET

# Algorithm
from .algorithm import CAT, generate_bank, recognize_speech, get_dict_file, upload_blob
import speech_recognition as sr
import numpy as np

# ----------------------------------------------
@app.route("/")
def index():

    if current_user.is_anonymous:
        name = ''
    else:     
        name = current_user.username
    return render_template("index.html", name=name)

@app.route("/about")
def about():

    return render_template("about.html")

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.username)

@app.route("/adaptivetest", methods=["GET", "POST"])
def adaptivetest(): # TODO: FIX THIS
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
                return redirect(url_for('result_adaptivetest'))

        session['cat'].administered_items.append(session['item_index']) # Add new item to list
        session['progress'] = (len(session['cat'].thetas) - 1) * 10 # Update progess
        session['theta'] = session['cat'].thetas[-1] # Update theta

        return redirect(url_for('adaptivetest'))
            
    # Render Template
    return render_template("adaptivetest.html", title = title, theta = session['theta'], progress = session['progress'], form = form)

@app.route("/adaptivetest/result")
def result_adaptivetest():
    theta = session['cat'].thetas[-1]
    return render_template("result_adaptivetest.html", theta = theta)

@app.route("/grammar")
def grammar():
    session['all_questions'] = Question.query.filter(Question.category_id == '1').all()
    bank = generate_bank(len(session['all_questions']))
    bank[:, 1] = [question.diff for question in session['all_questions']]
    session['items'] = bank
    session['cat'] = CAT(session['items'])

    (_stop, session['item_index']) = session['cat'].item_selection() # Get first item
    session['cat'].administered_items.append(session['item_index'])
    session['progress'] = 0
    session['theta'] = session['cat'].thetas[0]

    return redirect(url_for('adaptivetest'))

@app.route("/vocabulary")
def vocabulary():
    session['all_questions'] = Question.query.filter(Question.category_id == '2').all()
    bank = generate_bank(len(session['all_questions']))
    bank[:, 1] = [question.diff for question in session['all_questions']]
    session['items'] = bank
    session['cat'] = CAT(session['items'])

    (_stop, session['item_index']) = session['cat'].item_selection() # Get first item
    session['cat'].administered_items.append(session['item_index'])
    session['progress'] = 0
    session['theta'] = session['cat'].thetas[0]

    return redirect(url_for('adaptivetest'))

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

@app.route("/pronounciation/result", methods=['POST', 'GET'])
def result_pronounciation():
    word = session['word']

    if request.method == "POST":      
        # Write blob data to AWS
        upload_blob(request.data, 'audio/pronounciation_user.wav', BUCKET)

        # Speech recognition        
        f = io.BytesIO(request.data)
        response = recognize_speech(sr.Recognizer(), sr.AudioFile(f))
        session['answer'] = response['transcription'] 

    answer = session['answer']
    if answer != None:
        result = (word.lower() == answer.lower())
    else:
        result = "Unable to recognize speech"

    return render_template("result_pronounciation.html", result = result, word= word, answer = answer.capitalize(), link_audio = get_dict_file(word))

@app.route("/listening/test", methods=["GET", "POST"])
def listening():
    form = ListeningForm()

    if request.method == "GET":
        session['result_listening'] = None
        session['word_listening'] = RandomWord.query.options(load_only('id')).offset(
            func.floor(
                func.random() *
                db.session.query(func.count(RandomWord.id))
            )
        ).limit(1).all()[0].word.capitalize()
        
    if form.validate_on_submit():
        if form.answer.data.lower() == session['word_listening'].lower():
            session['result_listening'] = True
        else:
            session['result_listening'] = False
        
        return redirect(url_for('result_listening'))

    return render_template("listening.html",form = form, link_audio = get_dict_file(session['word_listening']))

@app.route("/listening/result")
def result_listening():

    return render_template("result_listening.html", word = session['word_listening'], result = session['result_listening'], link_audio = get_dict_file(session['word_listening']))