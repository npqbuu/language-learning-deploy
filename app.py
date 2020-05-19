import os
# Flask
from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_bootstrap import Bootstrap
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
# Import models and forms.
from models import *
from forms import *
from test import *
# Algorithm
from algorithm import CAT, generate_bank, recognize_speech
import speech_recognition as sr
import urllib
from bs4 import BeautifulSoup
import numpy as np

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'

# Session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app) 

# Database
def get_env_variable(name):
    try:
        return os.environ[name]
    except KeyError:
        message = "Expected environment variable '{}' not set.".format(name)
        raise Exception(message)

app.config['SQLALCHEMY_DATABASE_URI'] = get_env_variable("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning

# Link the Flask app with the database (no Flask app is actually being run yet).
db.init_app(app)

# Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def index():
    session.clear()
    session['words'] = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))

        return '<h1>Invalid username or password</h1>'
        #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return '<h1>New user has been created!</h1>'
        #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template('signup.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

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
        session['word'] = session['words'].pop()
        word = session['word']
    return render_template("pronounciation.html", word = word, result = result)

@app.route("/checkpronounciation", methods=['POST'])
def checkpronounciation():
    # Open file and write binary (blob) data
    with open('static/pronounciation_user.wav', 'wb') as f:
        f.write(request.data)
    # Speech recognition
    response = recognize_speech(sr.Recognizer(), sr.AudioFile('static/pronounciation_user.wav'))
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
            urllib.request.urlretrieve(link['src'], 'static/pronounciation_dict.wav')
            break
        except:
            print('Broken link')

    return render_template("result_voice.html", result = result, word= word, answer = answer)

if __name__ == '__main__':
    app.run(debug=True)