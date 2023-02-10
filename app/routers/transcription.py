import os
import re
import asyncio
import whisper
import requests
import datetime
import subprocess
import urllib.request
# from typing import Union
from pydantic import BaseModel
from pydub import AudioSegment
from pyannote.audio import Pipeline
from fastapi import APIRouter,FastAPI, HTTPException, Header, BackgroundTasks


class Transcribe(BaseModel):
    ext_ref_no: str
    title: str
    url: str
    language:str

router = APIRouter(prefix='/ai')


@router.post("/transcribe")
async def transcribe(transcribe : Transcribe , background_tasks: BackgroundTasks, x_async_request: str = Header(None)):
   # In case if x-async-request header is true  (HTTP 202 Accepted)
    if x_async_request == "true":
        background_tasks.add_task(async_transcribe_internal, transcribe.ext_ref_no, transcribe.title, transcribe.url, transcribe.language)
        
        return {
            "id": 123,
            "ext_ref_no": transcribe.ext_ref_no,
            "url": transcribe.url,
            "title": transcribe.title,
            "language": transcribe.language,
            "status": "PENDING",
        }
    else:
        response = await transcribe_internal(transcribe.ext_ref_no, transcribe.title, transcribe.url,transcribe.language)
        return response

async def async_transcribe_internal(ext_ref_no, title, url, language):
    recording_url= url
    print("async function is calling")
    data = await transcribe_internal(ext_ref_no, title, url, language)
    print("hook is calling now:")
    req = requests.post('https://apis.superkool.io/dashboard/v1/transcript/hook', 
                        json=data,
                        )
    print("Hook Called")
    print(data)
    print(req)

async def transcribe_internal(ext_ref_no, title, url, language):
    result = []
    recording_url = url
    if url.endswith('.mp4'):
        # download the mp4 file
        mp4_file, headers = urllib.request.urlretrieve(url)
        # open the mp4 file
        mp4_audio = AudioSegment.from_file(mp4_file, format="mp4")
        # export the mp4 file to wav
        wav_file = mp4_file.replace('.mp4', '.wav')
        my_w = mp4_audio.export(wav_file, format="wav")
        # print(f"File {mp4_file} has been converted to {wav_file}")
        url=wav_file
        print(my_w)
        
        print("TASK-1: PyAnnote Implementation")
        #old Tokens(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)
        pipeline = Pipeline.from_pretrained('pyannote/speaker-diarization', use_auth_token="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")
        print(pipeline)
        # create the input dictionary with the url
        input_dict = {'uri': "URL implementation", 'audio': url}
        # run the pipeline
        diarization = pipeline(input_dict)
        print("\n Diarization \n")
        print(diarization)
        # write the diarization to a file
        with open(f"{ext_ref_no + '_' + 'd.txt'}", "w") as f:
            f.write(str(diarization))

        print("\n Segments \n")
        print(*list(diarization.itertracks(yield_label = True))[:10], sep="\n")

        print("TASK-2: Preparing audio files according to the diarizations")
        def millisec(timeStr):
            spl = timeStr.split(":")
            s = (int)((int(spl[0]) * 60 * 60 + int(spl[1]) * 60 + float(spl[2]) )* 1000)
            return s

        print("TASK-3: Grouping the diarization segments according to the speaker.")
        print("\n Grouping the diarization segments according to the speaker \n")
        dzs = open(ext_ref_no + '_' + 'd.txt').read().splitlines()
        groups = []
        g = []
        lastend = 0
        for d in dzs:
            if g and (g[0].split()[-1] != d.split()[-1]):      #same speaker
                groups.append(g)
                g = []
            g.append(d)
            end = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=d)[1]
            end = millisec(end)
            if (lastend > end):       #segment engulfed by a previous segment
                groups.append(g)
                g = []
            else:
                lastend = end
        if g:
            groups.append(g)
        print(*groups, sep='\n')
        speaker_transcripts = {}
        for d in dzs:
            speaker_info = d.split()[-1]
            start_time = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=d)[0]
            end_time = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=d)[1]
            transcript = d.split()[0]
            if speaker_info not in speaker_transcripts:
                speaker_transcripts[speaker_info] = []
            speaker_transcripts[speaker_info].append((start_time, end_time, transcript))


        print("TASK-4: Save the audio part corresponding to eåach diarization group.")
        print("\n Save the audio part corresponding to eåach diarization group. \n")
        audio = AudioSegment.from_wav(url)
        gidx = -1
        for g in groups:
            start = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=g[0])[0]
            end = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=g[-1])[1]
            start = millisec(start)
            end = millisec(end)
            print(start, end)
            gidx += 1
            #audio[start:end].export(str(gidx) + '.wav', format='wav')
            audio[start:end].export(ext_ref_no + '_' + str(gidx) + '.wav', format='wav')

        print("TASK-5: Implementation of Whisper")
        print("\nEntering in Whisper model \n")
        with open(f"{ext_ref_no + '_' + 't.txt'}", "wb") as outfile:
            for i in range(gidx+1):
                subprocess.run(["whisper", ext_ref_no + '_' + str(i) + '.wav',"--language","en", "--model", "small"])
                with open(ext_ref_no + '_' + str(i) + '.wav.txt', 'r') as f:
                    transcript_data = outfile.write(transcript.encode())
                    transcript = f.read()
                speaker_info = groups[i][0].split()[-1]
                start_time = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=groups[i][0])[0]
                end_time = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=groups[i][-1])[1]
 
                result.append({
                    "speaker": speaker_info,
                    "seq_no": i,
                    "start":start_time,
                    "end": end_time,
                    "transcript_text":transcript
                })

            print("TASK-6: Free up memory space")
            os.remove(ext_ref_no + '_' + str(i) + '.wav')
            os.remove(ext_ref_no + '_' + str(i) + '.wav.srt')
            os.remove(ext_ref_no + '_' + str(i) + '.wav.txt')
            os.remove(ext_ref_no + '_' + str(i) + '.wav.vtt')
            os.remove(ext_ref_no + '_' + 'd.txt')
            os.remove(ext_ref_no + '_' + 't.txt')

            data = {
                "id": "123",
                "ext_ref_no": ext_ref_no,
                "title": title,
                "recording_url": recording_url,
                "language": language,
                "status": "SUCCESS",
                #"detected_language": detected_language,
                "transcript_data":transcript,
                "transcript_segments": result,
            }

            return data