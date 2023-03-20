import telebot
import os
import json
import time
from shutil import rmtree
from pytube import YouTube
import yt_dlp

with open('./configbot.json') as archive:
    botInfo = json.load(archive)

dp = telebot.TeleBot(botInfo["TOKEN"], parse_mode='HTML')

filePath = os.getcwd() + '/data/user/'

user = {} # dictionary

extractAudio = { # se debe utilizar ffmpeg
    'format': 'mp3/bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
    }]
}

@dp.message_handler(commands=['start'])
def sendWelcome(message):
    dp.send_message(message.chat.id, '''<i>¡Bienvenido a MiniTake!</i> Envíame un video de YouTube y en segundos te mando solo el audio.''')

@dp.message_handler(content_types=['text'])
def recieveLink(message):
    user[message.chat.id] = {} # identificador
    user[message.chat.id]['url'] = message.text # guarda el message.text (url) en una palabra clave

    msg = dp.send_message(message.chat.id, '''😎 <i>Descargando la música...</i>''')

    try:
        yt = YouTube(user[message.chat.id]['url'])

        content = os.path.join(filePath, str(message.chat.id)+'/')
        content = os.path.abspath(content)
        os.makedirs(content, exist_ok=True) # determina la ruta
        urlVideo = user[message.chat.id]['url']
        
        with yt_dlp.YoutubeDL(extractAudio) as ytdl: 
            os.chdir(content) # ira a la ruta que se le ha asignado para procesar la descarga
            ytdl.download(urlVideo) # descargara el audio 
        with os.scandir() as fileAudio:
            fileAudio = [file for file in fileAudio if file.is_file()]
        with open(fileAudio[0], 'rb') as audio:
            dp.send_chat_action(message.chat.id, 'upload_audio')
            dp.edit_message_text(text=f'''😎 <i>Enviando <b>{yt.title}!</b></i>''',
                                 chat_id= message.chat.id,
                                 message_id= msg.message_id)
            dp.send_audio(message.chat.id, audio)
            dp.edit_message_text(text=f'''🎸 <i>La música ha sido enviado!</i>''',
                                 chat_id = message.chat.id,
                                 message_id=msg.message_id)
            
            time.sleep(5)
            os.system('clear')
            rmtree(content) # eliminara la carpeta que fue asignada
    except: 
        try: rmtree(content) # si aun se mantiene, lo eliminara
        except: pass
        dp.edit_message_text(text='''😓 <i>¡Error de conexión! No se puede descargar la música.</i>''',
                             chat_id= message.chat.id,
                             message_id= msg.message_id)
        
if __name__ == '__main__':
    print('the bot is listening!')
    dp.infinity_polling()
