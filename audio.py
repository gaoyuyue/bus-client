# import pyttsx3
#
# engine = pyttsx3.init()
#
# engine.say('中文')
# engine.runAndWait()

from aip import AipSpeech

""" 你的 APPID AK SK """
APP_ID = '你的APP_ID'
API_KEY = '你的API_KEY'
SECRET_KEY = '你的SECRET_KEY'

client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

for i in range(30):
    result  = client.synthesis('失败，' + str(i + 1) + "号车", 'zh', 1, {
        'vol': 5,
    })
    if not isinstance(result, dict):
        with open('./audio/f_' + str(i + 1) + '.mp3', 'wb') as f:
            f.write(result)

for i in range(50):
    result = client.synthesis('成功，' + str(i + 1) + "号座", 'zh', 1, {
        'vol': 5,
    })
    if not isinstance(result, dict):
        with open('./audio/s_' + str(i + 1) + '.mp3', 'wb') as f:
            f.write(result)

result = client.synthesis('失败，已上车', 'zh', 1, {
    'vol': 5,
})
if not isinstance(result, dict):
    with open('./audio/f_exist.mp3', 'wb') as f:
        f.write(result)

result = client.synthesis('失败，非本班次', 'zh', 1, {
    'vol': 5,
})
if not isinstance(result, dict):
    with open('./audio/f_notNow.mp3', 'wb') as f:
        f.write(result)
