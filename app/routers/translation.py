import openai
import requests
from typing import Union
from pydantic import BaseModel
from fastapi import APIRouter, Header


class Translation(BaseModel):
    ext_ref_no: str
    title: Union[str, None] = None
    transcript: str
    transcript_language: Union[str, None] = None
    translation_language: str

router = APIRouter(prefix='/ai')

@router.post("/translation")
async def translation(translation:Translation, x_async_request: str = Header(None)):
    # In case if x-async-request header is true  (HTTP 202 Accepted)
    if x_async_request == "true":
        return {"id": "123",
                "ext_ref_no": translation.ext_ref_no,
                "title": translation.title,
                "transcript": translation.transcript,
                "transcript_language": translation.transcript_language,
                "translation_language": translation.translation_language,
                "status": "PENDING"}
    else:
        # In case if x-async-request header is false  (HTTP 201 Created)
        #1-(GET segments) 2-(TRANSLATE segments) 3-(POST to DATABASE)

        #get the path
        # segments_response = requests.get("../PATH")
        # #save fetched data into a object
        # segments = segments_response.json()
        # print("printing the segmets response")
        # print(segmets)
        
        # translated_segment = []
        # #loop on segments
        # for segment in segmets:
        #     response = openai.Completion.create(
        #                                 engine="text-curie-001",
        #                                 prompt= (f"Translate this  {transcript} from {transcript_language} language to {translation_language} language"),
        #                                 max_tokens=1500,
        #                                 n=1,
        #                                 stop=None,
        #                                 top_p=1,
        #                                 temperature=0.3
        #                                 )
        #     translated_segment = response["choices"][0]["text"]
        #     translated_segments.append(translated_segment)

        #     return translated_segment



        translation_data = ""
        chunk_size = 2048
        i = 0
        for i in range(0, len(translation.transcript), chunk_size):
            chunk = translation.transcript[i:i+chunk_size]
            if chunk[-1] == '.':
                translated_chunk = await call_gpt3_for_translation(chunk, translation.transcript_language, translation.translation_language)
                translation_data += translated_chunk
                i += len(chunk)
            else:
                last_period_index = chunk.rindex('.')
                chunk = chunk[:last_period_index + 1]
            translated_chunk = await call_gpt3_for_translation(chunk, translation.transcript_language, translation.translation_language)
            translation_data += translated_chunk


        data = {
            "id": "123",
            "ext_ref_no": 123,
            "title": translation.title,
            "transcript": translation.transcript,
            "transcript_language": translation.transcript_language,
            "translation_language": translation.translation_language,
            "translation_data": translation_data,
            "status": "COMPLETE",
        }

        return {"translation": data}


async def call_gpt3_for_translation(transcript,transcript_language, translation_language):
    prompt = (
        f"Translate this  {transcript} from {transcript_language} language to {translation_language} language")
    translation = openai.Completion.create(engine="text-curie-001",
                                           prompt=prompt,
                                           max_tokens=1500,
                                           n=1,
                                           stop=None,
                                           top_p=1,
                                           temperature=0.3
                                           )
    translated_transcript = translation.choices[0].text

    return translated_transcript