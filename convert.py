import subprocess
import tempfile
import os



def convert_to_pcm16b16000r(in_filename=None, in_bytes=None):
    with tempfile.TemporaryFile() as temp_out_file:
        temp_in_file = None
        if in_bytes:
            temp_in_file = tempfile.NamedTemporaryFile(delete=False)
            temp_in_file.write(in_bytes)
            in_filename = temp_in_file.name
            temp_in_file.close()
        if not in_filename:
            raise Exception('Neither input file name nor input bytes is specified.')

        # Запрос в командную строку для обращения к FFmpeg
        command = [
            r'ffmpeg\bin\ffmpeg.exe',  # путь до ffmpeg.exe
            '-i', in_filename,
            '-f', 's16le',
            '-acodec', 'pcm_s16le',
            '-ar', '16000',
            '-'
        ]

        proc = subprocess.Popen(command, stdout=temp_out_file, stderr=subprocess.DEVNULL)
        proc.wait()

        if temp_in_file:
            os.remove(in_filename)

        temp_out_file.seek(0)
        return temp_out_file.read()


filename = 'test1.ogg'

if filename:
    with open(filename, 'br') as file:
        bytes = file.read()
if not bytes:
    raise Exception('Neither file name nor bytes provided.')

newbytes = convert_to_pcm16b16000r(filename, bytes)
f = open('processedrecord.ogg', 'wb')

f.write(newbytes)
f.close()
