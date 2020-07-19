from __future__ import print_function
from ibm_watson import TextToSpeechV1
from ibm_watson.websocket import SynthesizeCallback
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import pyaudio
import configparser

#carrega configuracoes
config = configparser.ConfigParser()
config.read('config.ini')

# If service instance provides API key authentication
authenticator = IAMAuthenticator(config['TEXT2SPEECH']['API_KEY'])
service = TextToSpeechV1(
    authenticator=authenticator)

class Play(object):
    """
    Wrapper to play the audio in a blocking mode
    """
    def __init__(self):
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 22050
        self.chunk = 1024
        self.pyaudio = None
        self.stream = None

    def start_streaming(self):
        self.pyaudio = pyaudio.PyAudio()
        self.stream = self._open_stream()
        self._start_stream()

    def _open_stream(self):
        stream = self.pyaudio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            output=True,
            frames_per_buffer=self.chunk,
            start=False
        )
        return stream

    def _start_stream(self):
        self.stream.start_stream()

    def write_stream(self, audio_stream):
        self.stream.write(audio_stream)

    def complete_playing(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pyaudio.terminate()

class MySynthesizeCallback(SynthesizeCallback):
    def __init__(self):
        SynthesizeCallback.__init__(self)
        self.play = Play()

    def on_connected(self):
        print('Iniciando stream')
        self.play.start_streaming()

    def on_error(self, error):
        print('Erro recebido: {}'.format(error))

    def on_timing_information(self, timing_information):
        print(timing_information)

    def on_audio_stream(self, audio_stream):
        self.play.write_stream(audio_stream)

    def on_close(self):
        print('Síntese completa')
        self.play.complete_playing()



def start_reading():
    watson_callback = MySynthesizeCallback()

    print('Digite a frase a ser lida em voz, digite q para sair')

    text = ''
    while text != 'q':
        text = input('>> ')
        if text != 'q':
            service.synthesize_using_websocket(text,
                                           watson_callback,
                                           accept='audio/wav',
                                           voice="pt-BR_IsabelaVoice"
                                        )

def talkback(text):
    watson_callback = MySynthesizeCallback()
    service.synthesize_using_websocket(text,
                                           watson_callback,
                                           accept='audio/wav',
                                           voice="pt-BR_IsabelaVoice"
                                        )
