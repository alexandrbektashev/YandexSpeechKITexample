import xml.etree.ElementTree as XmlElementTree
import httplib2
import uuid
import sys

YANDEX_API_KEY = '8a578fa8-c8a0-4970-8bd4-fa16f41e764f'
YANDEX_ASR_HOST = 'asr.yandex.net'
YANDEX_ASR_PATH = '/asr_xml'
CHUNK_SIZE = 1024 ** 2


def speech_to_text(filename=None, bytes=None, request_id=uuid.uuid4().hex, topic='notes', lang='ru-RU',
                   key=YANDEX_API_KEY):
    # Формирование тела запроса к Yandex API
    url = YANDEX_ASR_PATH + '?uuid=%s&key=%s&topic=%s&lang=%s' % (
        request_id,
        key,
        topic,
        lang
    )

    # Считывание блока байтов
    chunks = read_chunks(CHUNK_SIZE, bytes)

    # Установление соединения и формирование запроса
    connection = httplib2.HTTPConnectionWithTimeout(YANDEX_ASR_HOST)

    connection.connect()
    connection.putrequest('POST', url)
    connection.putheader('Transfer-Encoding', 'chunked')
    connection.putheader('Content-Type', 'audio/x-wav')
    connection.endheaders()

    # Отправка байтов блоками
    for chunk in chunks:
        connection.send(('%s\r\n' % hex(len(chunk))[2:]).encode())
        connection.send(chunk)
        connection.send('\r\n'.encode())

    connection.send('0\r\n\r\n'.encode())
    response = connection.getresponse()

    # Обработка ответа сервера
    if response.code == 200:
        response_text = response.read()
        xml = XmlElementTree.fromstring(response_text)

        if int(xml.attrib['success']) == 1:
            max_confidence = - float("inf")
            text = ''

            for child in xml:
                if float(child.attrib['confidence']) > max_confidence:
                    text = child.text
                    max_confidence = float(child.attrib['confidence'])

            if max_confidence != - float("inf"):
                return text
            else:
                raise Exception('No text found.\n\nResponse:\n%s' % (response_text))
        else:
            raise Exception('No text found.\n\nResponse:\n%s' % (response_text))
    else:
        raise Exception('Unknown error.\nCode: %s\n\n%s' % (response.code, response.read()))


def read_chunks(chunk_size, bytes):
    while True:
        chunk = bytes[:chunk_size]
        bytes = bytes[chunk_size:]

        yield chunk

        if not bytes:
            break


for param in sys.argv:
    fname = param
    if ".wav"  in fname:
        if fname:
            with open(fname, 'br') as file:
                bytes = file.read()
        if not bytes:
            raise Exception('Neither file name nor bytes provided.')

        text = speech_to_text(bytes=bytes)
        print("Speech recognited in " + fname)
        print(text)



