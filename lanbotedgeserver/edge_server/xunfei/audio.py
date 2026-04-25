import pyaudio

'''
参考文档
http://people.csail.mit.edu/hubert/pyaudio/#docs
'''


class Recorder(object):

    def __init__(self, FORMAT=pyaudio.paInt16, CHANNELS=1, RATE=16000, CHUNK=1024, RECORD_TIME=1):
        self.CHUNK = CHUNK
        self.FORMAT = FORMAT
        self.CHANNELS = CHANNELS
        self.RATE = RATE
        self.RECORD_TIME = RECORD_TIME

        self.p = pyaudio.PyAudio()
        try:
            self.stream = self.p.open(format=self.FORMAT,
                                    channels=self.CHANNELS,
                                    rate=self.RATE,
                                    input=True,
                                    frames_per_buffer=self.CHUNK)
        except Exception as e:
            print(e)
            self.stream = None
        # print('Recorder已创建')
        return

    def get_record_audio(self):
        frames = []
        if self.stream is None:
            return frames
        
        for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_TIME)):
            data = self.stream.read(self.CHUNK)
            frames.append(data)
        return frames

    def __del__(self):
        if not self.stream is None:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()
        # print('Recorder已销毁')
        return


class Player():

    def __init__(self, FORMAT=pyaudio.paInt16, CHANNELS=1, RATE=16000, CHUNK=1024):
        self.CHUNK = CHUNK
        self.FORMAT = FORMAT
        self.CHANNELS = CHANNELS
        self.RATE = RATE

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.FORMAT,
                                  channels=self.CHANNELS,
                                  rate=self.RATE,
                                  output=True)
        # print('Player已创建')
        return

    def play_audio(self, data):
        self.stream.write(data)

    def __del__(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        # print('Player已销毁')
        return
