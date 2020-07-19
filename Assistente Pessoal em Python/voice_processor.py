from dictation import start_stream
from reading import start_reading, talkback
import os
import time
import getpass 
import globals




def dictate():
    print('Iniciando assistente...')
    start_stream()

    

### INÍCIO DO PROGRAMA ####
globals.initialize() 
    
talkback('Asssistente Pessoal Python Inicializando')
talkback('Você pode dizer, "computador: ajuda", para saber mais sobre mim.')
user = getpass.getuser()
texto = 'Você está logado com o usuário: ' + user
talkback(texto)


talkback('Por favor, informe: ')
talkback('1 para simular os comandos e 2 para realmente executar.')
simular = 0
simular = input('Digite 1 para simular ou 2 para executar e tecle enter: ')

if simular == '2':
    globals.executar = True
    talkback('Irei executar os comandos.')
else:
    talkback('Irei simular os comandos.')

dictate()


