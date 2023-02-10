# README #

In this project we are going to make different types of API'S
# 1. root (API)
* will return "Root is Calling"
# 2. speakers (API)
* will return "Speaker Identification and Whisper calling. Transcription from video to text"
# 3. takeaways (API)
* using GPT-3 will generate takeaways.
# 4. trancsription  (API)
* will get URL, then pass to PyAnnote for speaker dirization and then pass to whisper for transcription
# 5. translation (API)
* using GPT-3 will generate takeaways.

# Installation Process
* Step# 1: Install Virtual Environment
  * pip install virtualenv venv
* Step# 2: activate your Environment
   * source venv/bin/activate
* Step# 3: Then Install all requirements
    * pip install -r r.txt
* Step# 4: Run project
  * uvicorn app.main:app 
