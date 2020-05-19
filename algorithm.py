import numpy as np
import random
# CAT
from catsim.cat import generate_item_bank # this function generates an item bank, in case the user cannot provide one
from catsim.simulation import * # simulation package contains the Simulator and all abstract classes
from catsim.initialization import * # initialization package contains different initial proficiency estimation strategies
from catsim.selection import * # selection package contains different item selection strategies
from catsim.estimation import * # estimation package contains different proficiency estimation methods
from catsim.stopping import * # stopping package contains different stopping criteria for the CAT
# Speech to text
import speech_recognition as sr

def generate_bank(bank_size):
    # generating an item bank
    print('Generating item bank...')
    
    return(generate_item_bank(bank_size, '1PL'))

class CAT():
    def __init__(self, items):
        self.items = items
        self.responses = []
        self.administered_items = []

        # create a random proficiency initializer
        self.initializer = RandomInitializer()
        print('Creating simulation components...')

        # create a maximum information item selector
        self.selector = MaxInfoSelector()

        # create a hill climbing proficiency estimator
        self.estimator = HillClimbingEstimator()

        # create a stopping criterion that will make tests stop after 10 items
        self.stopper = MaxItemStopper(10)

        # manually initialize an examinee's proficiency as a float variable
        self.est_theta = self.initializer.initialize()
        self.thetas = [self.est_theta]
        print('Examinee initial proficiency:', self.est_theta)

    def item_selection(self):
        # get the index of the next item to be administered to the current examinee, given the answers they have already given to the previous dummy items
        item_index = self.selector.select(items=self.items, administered_items=self.administered_items, est_theta=self.est_theta)
        print('Next item to be administered:', item_index)

        # get a boolean value pointing out whether the test should stop
        _stop = self.stopper.stop(administered_items=self.items[self.administered_items], theta=self.est_theta)
        print('Should the test be stopped:', _stop)
    
        return (_stop, item_index)

    def item_administration(self):
        # get an new estimated theta
        new_theta = self.estimator.estimate(items=self.items, administered_items=self.administered_items, response_vector=self.responses, est_theta=self.est_theta)
        print('Estimated proficiency, given answered items:', new_theta)
        self.thetas.append(new_theta)

def recognize_speech(recognizer, record): # https://github.com/realpython/python-speech-recognition
    """Transcribe speech from recorded from `microphone`.

    Returns a dictionary with three keys:
    "success": a boolean indicating whether or not the API request was
               successful
    "error":   `None` if no error occured, otherwise a string containing
               an error message if the API could not be reached or
               speech was unrecognizable
    "transcription": `None` if speech could not be transcribed,
               otherwise a string containing the transcribed text
    """
    # check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    # adjust the recognizer sensitivity to ambient noise and record audio
    # from the microphone
    with record as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    # set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    # try recognizing the speech in the recording
    # if a RequestError or UnknownValueError exception is caught,
    #     update the response object accordingly
    try:
        response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response

