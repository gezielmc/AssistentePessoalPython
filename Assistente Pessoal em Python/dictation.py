from __future__ import print_function
import pyaudio
from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from threading import Thread
import configparser
from comandos import *
from reading import start_reading, talkback
import sys
import globals

try:
    from Queue import Queue, Full
except ImportError:
    from queue import Queue, Full

#carrega configuracoes
config = configparser.ConfigParser()
config.read('config.ini')

###############################################
#### inicia fila para gravar as gravacoes do microfone ##
###############################################
CHUNK = 1024
# Nota: gravacoes sao descartadas caso o websocket nao consuma rapido o suficiente
# Caso precise, aumente o max size conforme necessario
BUF_MAX_SIZE = CHUNK * 10
# Buffer para guardar o audio
q = Queue(maxsize=int(round(BUF_MAX_SIZE / CHUNK)))

# Cria o audio source com a fila
audio_source = AudioSource(q, True, True)

#configura o speech2text
authenticator = IAMAuthenticator(config['SPEECH2TEXT']['API_KEY'])
speech_to_text = SpeechToTextV1(
   authenticator=authenticator)
speech_to_text.set_service_url(config['SPEECH2TEXT']['URL'])


# classe de callback para o servico de reconhecimento de voz
class MyRecognizeCallback(RecognizeCallback):
    def __init__(self):
        self.frase = ''
        self.comando = 0
        self.unknow_cmd = 0
        self.inicio = 0
        RecognizeCallback.__init__(self)
        # talkback('Você deseja simular ou executar os comandos?')
        # talkback('Digite 1 para simular ou 2 para executar e tecle enter')
        # self.simular = input('Digite 1 para simular ou 2 para executar e tecle enter')
        
    def retorna_frase(self):
        return self.frase

    def on_transcription(self, transcript):
        pass

    def on_connected(self):
        print('Conexão OK')

    def on_error(self, error):
        print('Erro recebido: {}'.format(error))

    def on_inactivity_timeout(self, error):
        print('Timeout de inatividade: {}'.format(error))

    def on_listening(self):
        print('Serviço está ouvindo, aperte q + Enter para finalizar')

    def on_hypothesis(self, hypothesis):
        pass

    def detect_command(self, data):
        for result in data['results']:
             if result['alternatives'][0]['transcript'] == 'computador':
                print('Detectado comando:')
                print(result['alternatives'][0]['transcript'])


    def on_data(self, data):
        # print('Texto detectado: ')
        # print(data['results'])
        # return data['results']
        #self.frase = [{'final': True, 'alternatives': [{'transcript': 'computador ', 'confidence': 1.0}]}]
        self.frase = data['results']
        # print('frase: ', self.frase)
        # print('data: ', data['results'])
        # print('final: ', self.frase['final'][0])
        for result in data['results']:
             # print(result['alternatives'][0]['transcript'])
             # print('results final: ', result['final'])
             if result['final'] == True:
                 self.interpretador()
        # print('')

                
    def on_close(self):
        print("Conexão fechada")
        
        
    def interpretador(self):
        print('Interpretador de Voz')
        print('frase: ', self.frase)
        for result in self.frase:
            lista = (result['alternatives'][0]['transcript']).split()
            for word in lista:
                if word == 'computador':
                    self.comando = 1
                    print('Aguardando comando...')
                elif self.comando == 1:
                    # Ignorar artigos e preposições:
                    if  (word == 'o' or word == 'as' or word == 'os'  
                        or word == 'as' or word == 'um' or word == 'uma' 
                        or word == 'uns' or word == 'umas') :
                        continue
                    print('Detectei o comando: ', word) 
                    # comando = 0
                    if word == 'desligar':
                        talkback('Desligando agora!')
                        self.comando = 0
                        if globals.executar:
                            desligar()
                        break
                    elif word == 'reiniciar':
                        talkback('Reiniciando imediatamente!')
                        self.comando = 0
                        if globals.executar:
                            reiniciar()
                        break                            
                    elif word == 'hibernar':
                        talkback('Hibernando em alguns instantes!')
                        self.comando = 0
                        if globals.executar:
                            hibernar()
                        break                            
                    elif word == 'deslogar':
                        talkback('Ok, vamos deslogar!')
                        self.comando = 0
                        if globals.executar:
                            deslogar()
                        break                            
                    elif word == 'sair':
                        sys.exit(0)
                        quit()
                    elif word == 'ajuda':
                        talkback('Ótimo, vou te ajudar!')
                        talkback('Por enquanto eu entendo apenas alguns comandos:')
                        talkback('Você pode pedir para desligar, reiniciar, hibernar ou deslogar')
                        talkback('Mas eu não gosto de maçãs e só funciono bem no Windous!')
                        talkback('Por enquanto é isso, estou à disposição!')
                        self.comando = 0   
                        break
                    else:
                        if self.unknow_cmd == 0:
                            self.unknow_cmd = 1
                            self.comando = 0
                            lista = []
                            talkback('Desculpe, não entendi! ')
                            break
                        else:
                            talkback('Desculpe, não estou compreendendo! Por favor, fale mais devagar comigo.')
                            lista = []
                            self.unknow_cmd = 0        
                            self.comando = 0
                            break

# inicia o reconhecimento usando o audio_source
def recognize_using_weboscket(*args):
    mycallback = MyRecognizeCallback()
    speech_to_text.recognize_using_websocket(audio=audio_source,
                                             content_type='audio/l16; rate=44100',
                                             recognize_callback=mycallback,
                                             # model='pt-BR_BroadbandModel',
                                             model='pt-BR_NarrowbandModel',
                                             inactivity_timeout = -1,
                                             interim_results=True)
    # print('json:', mycallback)
    # print('retorno da funcao: ', mycallback.on_data())

###############################################
#### Prepara gravacao usando pyaudio ##
###############################################

# Config do pyaudio para as gravacoes
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# define callback para gravar o audio na fila
def pyaudio_callback(in_data, frame_count, time_info, status):
    try:
        q.put(in_data)
    except Full:
        pass # discard
    return (None, pyaudio.paContinue)


    

def start_stream():
    # instancia pyaudio
    audio = pyaudio.PyAudio()

    # abre stream
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
        stream_callback=pyaudio_callback,
        start=False
    )

    #########################################################################
    #### Start the recording and start service to recognize the stream ######
    #########################################################################

    stream.start_stream()

    try:
        recognize_thread = Thread(target=recognize_using_weboscket, args=())
        recognize_thread.start()


        command = ''
        while command != 'q':
            command = input()

        # para gravacao
        audio_source.completed_recording()
        stream.stop_stream()
        stream.close()
        audio.terminate()
        recognize_thread.join()

    except KeyboardInterrupt:
        # para gravacao
        audio_source.completed_recording()
        stream.stop_stream()
        stream.close()
        audio.terminate()