from discord import AudioSource
import pyaudio
from discord.opus import Encoder as OpusEncoder


class DesktopAudio(AudioSource):
    """
    streams all audio of device to output of discord bot
    device id can be figured out with the utils/pyaudio_device.py
    only lists input devices
    """
    def __init__(self, deviceId):
        self.device = deviceId
        self.sr = 48000
        self.audio_interface = pyaudio.PyAudio()
        self.audio_stream = self.audio_interface.open(
            format=pyaudio.paInt16,
            channels=2,
            rate=self.sr,
            input=True,
            input_device_index=self.device,
        )
        self.audio_stream.start_stream()

    def read(self) -> bytes:
        # I'm not sure why I have to divide by 4 here, but it works (╯°□°）╯︵ ┻━┻
        ret = self.audio_stream.read(int(OpusEncoder.FRAME_SIZE / 4), True)
        if len(ret) != OpusEncoder.FRAME_SIZE:
            return b""
        return ret

    def is_opus(self) -> bool:
        """Checks if the audio source is already encoded in Opus."""
        return False

    def cleanup(self) -> None:
        self.audio_stream.stop_stream()

