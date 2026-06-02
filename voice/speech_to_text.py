
# voice/speech_to_text.py

"""
Speech To Text Module
Uses SpeechRecognition
Supports microphone and audio file input
"""

import speech_recognition as sr
import tempfile
import os


class SpeechToText:

    def __init__(self):

        self.recognizer = sr.Recognizer()

    # -----------------------------------
    # MICROPHONE INPUT
    # -----------------------------------

    def transcribe_microphone(self):

        try:

            with sr.Microphone() as source:

                self.recognizer.adjust_for_ambient_noise(
                    source,
                    duration=1
                )

                audio = self.recognizer.listen(
                    source
                )

                text = self.recognizer.recognize_google(
                    audio
                )

                return {
                    "success": True,
                    "text": text
                }

        except Exception as e:

            return {
                "success": False,
                "error": str(e)
            }

    # -----------------------------------
    # AUDIO FILE INPUT
    # -----------------------------------

    def transcribe_file(
        self,
        uploaded_file
    ):

        try:

            suffix = uploaded_file.name.split(
                "."
            )[-1]

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=f".{suffix}"
            ) as tmp:

                tmp.write(
                    uploaded_file.read()
                )

                path = tmp.name

            with sr.AudioFile(path) as source:

                audio = self.recognizer.record(
                    source
                )

            text = self.recognizer.recognize_google(
                audio
            )

            os.remove(path)

            return {

                "success": True,
                "text": text

            }

        except Exception as e:

            return {

                "success": False,
                "error": str(e)

            }
