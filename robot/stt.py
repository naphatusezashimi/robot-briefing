from config import SIMULATOR_MODE, AUDIO_IN, RECORD_SECONDS, SAMPLE_RATE


def record_audio(filename: str = AUDIO_IN, seconds: int = RECORD_SECONDS) -> str:
    """อัดเสียงจากไมค์ — เฟส 2"""
    if SIMULATOR_MODE:
        raise RuntimeError("ไม่มีไมค์ในโหมดจำลอง ใช้ simulator.py แทน")
    import sounddevice as sd
    from scipy.io.wavfile import write

    print(f"[ไมค์] กำลังฟัง... พูดได้เลย ({seconds} วินาที)")
    audio = sd.rec(int(seconds * SAMPLE_RATE), samplerate=SAMPLE_RATE,
                   channels=1, dtype="int16")
    sd.wait()
    write(filename, SAMPLE_RATE, audio)
    return filename


def speech_to_text(audio_file: str = AUDIO_IN) -> str:
    """แปลงเสียงเป็นข้อความภาษาไทย ด้วย Google STT — เฟส 2"""
    if SIMULATOR_MODE:
        raise RuntimeError("ไม่มี STT ในโหมดจำลอง ใช้ simulator.py แทน")
    from google.cloud import speech

    client = speech.SpeechClient()
    with open(audio_file, "rb") as f:
        content = f.read()

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=SAMPLE_RATE,
        language_code="th-TH",
    )
    response = client.recognize(
        config=config,
        audio=speech.RecognitionAudio(content=content),
    )
    if not response.results:
        return ""
    return response.results[0].alternatives[0].transcript
