from config import SIMULATOR_MODE, AUDIO_OUT


def text_to_speech(text: str, output_file: str = AUDIO_OUT) -> str:
    """แปลงข้อความเป็นเสียงภาษาไทย ด้วย Google TTS — เฟส 2"""
    if SIMULATOR_MODE:
        # เฟส 1: แค่บอกว่าจะพูดอะไร ไม่ต้องเล่นเสียงจริง
        return output_file

    from google.cloud import texttospeech

    client = texttospeech.TextToSpeechClient()
    response = client.synthesize_speech(
        input=texttospeech.SynthesisInput(text=text),
        voice=texttospeech.VoiceSelectionParams(
            language_code="th-TH",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
        ),
        audio_config=texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        ),
    )
    with open(output_file, "wb") as f:
        f.write(response.audio_content)
    return output_file
