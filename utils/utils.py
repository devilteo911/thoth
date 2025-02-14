from datetime import timedelta
from typing import List

import librosa
import numpy as np
from loguru import logger


def split_string(string: str) -> List[str]:
    """
    Split a string into a list of strings of length < 4096.
    :param string: the string to split
    :return: a list of strings
    """
    if len(string) < 4096:
        yield string
        return
    words = string.split()
    current_string = ""
    for word in words:
        if len(current_string) + len(word) > 4095:
            yield current_string
            current_string = word
        else:
            current_string += f" {word}"
    yield current_string


def format_timedelta(td: timedelta) -> str:
    """
    Format a timedelta object into a string
    """
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    result = []
    if days > 0:
        result.append(f"{days} days")
    if hours > 0:
        result.append(f"{hours} hours")
    if minutes > 0:
        result.append(f"{minutes} minutes")
    if seconds > 0:
        result.append(f"{seconds} seconds")
    return " e ".join(result)


def detect_silence(audio: np.ndarray, sr: int, threshold: int = 70) -> int:
    """
    Detects the number of half seconds of total silence at the end of an audio file.

    Args:
        audio_file (str): The path to the audio file to be analyzed.
        threshold (int, optional): The threshold value below which a half second of audio is considered silent. Defaults to 70.

    Returns:
        Tuple[int, float]: A tuple containing the number of half seconds of total silence at the end of the audio file and the duration of the audio file in seconds.
    """
    try:
        duration = librosa.get_duration(y=audio, sr=sr) * 1000  # in milliseconds
        seconds = []

        # transform the amplitude of the audio signal into decibels for every 0.5 seconds
        for s in range(0, len(audio), int(sr)):
            seconds.append(np.abs(audio[s : s + int(sr)]).sum())

        seconds = seconds[::-1]

        count = 0
        for s in seconds:
            if s < threshold:
                count += 1
            else:
                break
        return count, duration / 1000
    except Exception as e:
        logger.exception(e)
        raise e


def get_message_info(update):
    try:
        file_id = update.message.video_note.file_id
        message_type = "video_note"
    except AttributeError:
        file_id = update.message.voice.file_id
        message_type = "voice"

    return file_id, message_type
