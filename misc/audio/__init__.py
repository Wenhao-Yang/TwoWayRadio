#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@author:WILLIAM
@file: __init__.py
@time: 23:36
@Device: Personal Win10
@Description: 
"""
import queue
import subprocess
import threading
import wave
import os

import pyaudio
from PyQt5.QtCore import QThread, pyqtSignal
from scipy import signal

CHUNK = 1024
WIDTH = 2
CHANNELS = 2
RATE = 44100
HACKRF_PATH = os.path.join('misc', 'audio', 'hackrf', 'bin',  'hackrf_info.exe')

def wav2duration(wavfile):
    try:
        with wave.open(wavfile) as f:

            rate = f.getframerate()
            frames = f.getnframes()
            duration = frames / float(rate)
            return duration
    except Exception as e:
        return 0.

class RecordChnThread(QThread):
    trigger = pyqtSignal(int)
    def __init__(self, wavpath, freq):
        super(RecordChnThread, self).__init__()
        self.wavpath = wavpath
        self.freq = freq
        self.state = True

    def run(self):
        # command = 'misc/audio/Record_Wav/save_block_sink.exe --wavpath %s --freq %s' % (self.wavpath, str(self.freq))
        save_block = os.path.join('misc', 'audio', 'Record_Wav', 'save_block.exe')
        assert os.path.exists(save_block)
        command = '%s --wavpath %s --freq %s' % (save_block, self.wavpath, str(self.freq))
        self.p = subprocess.Popen(command, shell=False,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)

        if len(self.p.stderr.readlines())>0:
            self.state = False

    def stop(self):
        # super(ExtractThread, self).finished()
        try:
            self.p.stdin.close()
            self.p.wait()
            return('success')
        except:
            return('failed')

class RecordMicThread(QThread):
    trigger = pyqtSignal(int)
    def __init__(self, wavpath, input_device=1, sr=RATE):
        super(RecordMicThread, self).__init__()

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16, channels=CHANNELS, rate=sr, input=True,
                                  input_device_index=input_device,
                                  output=False, frames_per_buffer=CHUNK, stream_callback=self.callback)

        self.wavpath = wavpath
        self.saveFlag = False
        self.sr = sr
        self.q = queue.Queue()
        self.state = True
        self.data_frames = []

    def callback(self, in_data, frame_count, time_info, status):
        global ad_rdy_ev
        self.q.put(in_data)
        if self.saveFlag:
            self.data_frames.append(in_data)

        return (None, pyaudio.paContinue)
    def read_audio_thead(self, q, stream, ad_rdy_ev):
        # 获取队列中的数据
        try:
            while stream.is_active():
                self.ad_rdy_ev.wait(timeout=0.1)  # 线程事件，等待0.1s
                if not q.empty():
                    data = q.get()
                    while not q.empty():  # 将多余的数据扔掉，不然队列会越来越长
                        q.get()

                self.ad_rdy_ev.clear()
        except:
            pass

    def run(self):
        # command = 'misc/audio/Record_Wav/save_block_sink.exe --wavpath %s --freq %s' % (self.wavpath, str(self.freq))
        self.stream.start_stream()

        self.ad_rdy_ev = threading.Event()  # 线程事件变量
        self.t = threading.Thread(target=self.read_audio_thead,
                                  args=(self.q, self.stream, self.ad_rdy_ev))  # 在线程t中添加函数read_audio_thead
        self.t.setDaemon(True)  # 设为主进程的守护进程
        self.t.start()  # 线程开始运行
        self.saveFlag = True


    def endSaveAudio(self):
        # 停止获取音频信息
        self.saveFlag = False
        wf = wave.open(self.wavpath, 'wb')
        wf.setnchannels(CHANNELS)  # 声道
        wf.setsampwidth(WIDTH)  # 采样字节 1 or 2
        wf.setframerate(self.sr)  # 采样频率 8000 or 16000
        # print(len(self.data_frames))
        wf.writeframes(b"".join(self.data_frames))
        self.data_frames = []

        wf.close()

    def stop(self):
        # super(ExtractThread, self).finished()
        try:
            self.endSaveAudio()
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()

            # 清空队列
            while not self.q.empty():
                self.q.get()
            return('success')
        except:
            return('failed')

def check_hackrf():
    command = HACKRF_PATH
    p = subprocess.Popen(command, shell=False,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

    [stdout, stderr] = p.communicate()
    return True if p.returncode ==0 else False