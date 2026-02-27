import os
from gtts import gTTS


async def text_to_speech(text: str, output_file: str, lang: str = "en"):
    tts = gTTS(text=text, lang=lang)
    tts.save(output_file)
    return output_file
