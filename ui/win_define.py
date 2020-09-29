#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@author:WILLIAM
@file: win_define.py
@time: 20:44
@Device: Personal Win10
@Description: 
"""
import json
import time

import pyaudio
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMainWindow, QDialog, QTableWidgetItem, QAbstractItemView, QCheckBox, QListWidgetItem

from misc.audio.__init__ import wav2duration, RecordChnThread, RecordMicThread, check_hackrf
from misc.prepare_trans import get_num_sets, get_utt_sets, get_spk_tran
from ui.new_spk import Ui_Dialog
from ui.record_main import Ui_MainWindow
import os
import qtawesome

from ui.select_spk import Ui_LoadSpkDialog


class Add_Spk_Win(QDialog, Ui_Dialog):
    def __init__(self, sid, parent=None):
        super(Add_Spk_Win, self).__init__(parent)
        self.setupUi(self)
        self.sid_lineEdit.setText(sid)
        self.saveButton.clicked.connect(self.confirm)
        self.cancleButton.clicked.connect(self.reject)

    def confirm(self):
        sname = self.name_lineEdit.text()
        if sname != '':
            self.accept()
        else:
            QtWidgets.QMessageBox.information(self,
                                              '提示',
                                              "姓名不能为空",
                                              QtWidgets.QMessageBox.Yes)

class Load_Spk_Win(QDialog, Ui_LoadSpkDialog):
    def __init__(self, parent=None, **kwargs):
        super(Load_Spk_Win, self).__init__(parent)

        self.setupUi(self)
        self.spk_tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.spk_tableWidget.verticalHeader().setVisible(False)
        while self.spk_tableWidget.rowCount() > 0:
            self.spk_tableWidget.removeRow(self.spk_tableWidget.rowCount() - 1)

        try:
            self.sid2sname = kwargs['sids']


            for i, ss in enumerate(self.sid2sname):
                row = self.spk_tableWidget.rowCount()
                self.spk_tableWidget.insertRow(row)

                item = QTableWidgetItem(str(ss[0]))
                # item.setCheckState(QtCore.Qt.Unchecked)
                item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                self.spk_tableWidget.setItem(row, 0, item)

                item = QTableWidgetItem(str(ss[1]))
                # item.setCheckState(QtCore.Qt.Unchecked)
                item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                self.spk_tableWidget.setItem(row, 1, item)



            self.selectButton.clicked.connect(self.return_spk)
            self.cancleButton.clicked.connect(self.reject)
        except Exception as f:
            print(f)

    def return_spk(self):
        this_item = self.spk_tableWidget.currentItem().row()

        if this_item != None:
            self.accept()
        else:
            QtWidgets.QMessageBox.information(self,
                                              '提示',
                                              "选择不能为空",
                                              QtWidgets.QMessageBox.Yes)


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        if check_hackrf():
            self.hackrf_lineEdit.setText('hackrf 已就绪')

        self.speakers = {} # [sid, sname, sgender, sage, sdis]
        if os.path.exists('data/spk_info'):
            with open('data/spk_info', 'r') as spkf:
                try:
                    speakers = json.load(spkf)
                    if len(speakers) > 0:
                        self.speakers.update(speakers)
                except:
                    pass

        self.wav2scp = {}
        if os.path.exists('data/wav.scp'):
            with open('data/wav.scp', 'r') as wsf:

                for l in wsf.readlines():
                    try:
                        uid, upath = l.split()
                        self.wav2scp[uid] = upath
                    except:
                        pass

        self.chns_value = {}
        with open('data/chn_info', 'r') as chnf:
            for l in chnf.readlines():
                ls = l.split()
                self.chns_value[int(ls[0])] = int(ls[3])

        output_device = {}
        input_device = {}
        p = pyaudio.PyAudio()
        # 找寻输入输出设备
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            # print(dev)
            if dev['maxInputChannels'] > 0:
                input_device[i] = dev
            elif dev['maxOutputChannels'] > 0:
                output_device[i] = dev
        self.input_device = list(input_device.keys())[0]
        self.sr = input_device[self.input_device]['defaultSampleRate']

        self.num5_set = get_num_sets(file_path='data/transcript/num5.txt', num_tran=24)
        self.num10_set = get_num_sets(file_path='data/transcript/num10.txt', num_tran=16)
        self.short_set = get_utt_sets(file_path='data/transcript/short.txt', num_tran=104)
        self.long_set = get_utt_sets(file_path='data/transcript/long.txt', num_tran=72)

        self.new_spk.triggered.connect(self.add_Spk)
        self.select_spk.triggered.connect(self.load_Spk)
        self.num_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.num_table.verticalHeader().setVisible(False)
        self.num_table.clicked.connect(self.set_Num_Trans)
        self.num_table.setColumnWidth(0, 200)
        self.num_table.setColumnWidth(1, 200)
        self.num_table.setColumnWidth(2, 500)


        self.short_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.short_table.verticalHeader().setVisible(False)
        self.short_table.clicked.connect(self.set_Short_Trans)
        self.short_table.setColumnWidth(0, 200)
        self.short_table.setColumnWidth(1, 200)
        self.short_table.setColumnWidth(2, 500)

        self.long_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.long_table.verticalHeader().setVisible(False)
        self.long_table.clicked.connect(self.set_Long_Trans)
        self.long_table.setColumnWidth(0, 200)
        self.long_table.setColumnWidth(1, 200)
        self.long_table.setColumnWidth(2, 500)

        self.rec_thread = None
        self.rem_thread = None

        self.record_Button.clicked.connect(self.start_Record)

    def add_Spk(self):
        j = 0
        while 'S%05d' % (j) in self.speakers.keys():
            j += 1
        sid = 'S%05d' % (j)
        if j%2 ==0:
            chns = [0, 1, 2, 3, 4, 5, 6, 7]
        else:
            chns = [8, 9, 10, 11, 12, 13, 14, 15]

        add_dialog = Add_Spk_Win(sid=sid)
        return_code = add_dialog.exec_()
        # print(hell)
        if return_code == 1:
            sname = add_dialog.name_lineEdit.text()
            sgender = add_dialog.gender_comboBox.currentText()
            sage = add_dialog.age_lineEdit.text()
            sdis = add_dialog.prov_comboBox.currentText()

            try:
                self.speakers[sid] = [sid, sname, sgender, int(sage), sdis]
            except Exception as e:
                print(e)
                return False
            sid_path = [os.path.join('data', 'wav', 'sid', s ) for s in ['radio', 'clear']]
            for p in sid_path:
                if not os.path.exists(p):
                    os.makedirs(p)

            reply = QtWidgets.QMessageBox.information(self,
                                                      '提示',
                                                      "已添加说话人 %s " % sname,
                                                      QtWidgets.QMessageBox.Yes)

            num5_utt, num10_utt, short_utt, long_utt = get_spk_tran(j, self.num5_set, self.num10_set, self.short_set, self.long_set)
            self.load_tables(sid, sname, chns, num5_utt, num10_utt, short_utt, long_utt)
            self.speakers[sid] = [sname, sgender, sage, sdis]
            with open('data/spk_info', 'w') as spkf:
                try:
                    json.dump(self.speakers, spkf)
                except:
                    pass
        pass

    def load_Spk(self):
        sids = list(self.speakers.keys())
        sids.sort()
        sid2sname = [(sid, self.speakers[sid][0]) for sid in sids]
        load_dialog = Load_Spk_Win(sids=sid2sname)
        return_code = load_dialog.exec_()

        if return_code == 1:
            this_item = load_dialog.spk_tableWidget.currentItem().row()
            sname = load_dialog.spk_tableWidget.item(this_item, 1).text()
            self.sid = load_dialog.spk_tableWidget.item(this_item, 0).text()

            # sid = this_item.text()
            j = int(self.sid[1:])

            chns = [ 1, 2, 3, 4, 5, 6, 7, 8] if j % 2 == 0 else [9, 10, 11, 12, 13, 14, 15, 16]
            assert self.speakers[self.sid][0] == sname

            sid_path = [os.path.join('data', 'wav', self.sid, s ) for s in ['radio', 'clear']]
            for p in sid_path:
                if not os.path.exists(p):
                    os.makedirs(p)

            reply = QtWidgets.QMessageBox.information(self,
                                                      '提示',
                                                      "已加载说话人 %s " % sname,
                                                      QtWidgets.QMessageBox.Yes)

            num5_utt, num10_utt, short_utt, long_utt = get_spk_tran(j, self.num5_set, self.num10_set, self.short_set, self.long_set)
            self.load_tables(self.sid, sname, chns, num5_utt, num10_utt, short_utt, long_utt)
            # self.speakers[sid] = [sname, sgender, sage, sdis]

        pass

    def load_tables(self, sid, sname, chns, num5_utt, num10_utt, short_utt, long_utt):
        self.sid_lineEdit.setText(sid)
        self.sname_lineEdit.setText(sname)
        try:
            self.load_num_table(sid, chns, num5_utt, num10_utt)
            self.load_sutt_table(sid, chns, short_utt)
            self.load_lutt_table(sid, chns, long_utt)
        except Exception as e:
            print(e)

    def load_num_table(self, sid, chns, num5_utt, num10_utt):

        sid_utterances = {}
        all_save_utts = {}

        with open('data/wav.scp', 'r') as f:
            for line in f.readlines():
                try:
                    uid,upath = line.split()
                    all_save_utts[uid] = upath
                except:
                    pass

        uids = []
        saves_utt = 0
        for i,l in enumerate(num5_utt):
            tid, trans = l.split()
            uid = '-'.join((sid, tid))
            if '-'.join(('radio',uid)) in all_save_utts.keys():
                dur = wav2duration(all_save_utts['-'.join(('radio',uid))])
                saves_utt += 1
            else:
                dur = 0.
            saved = True if dur>0. else False
            chn = chns[int(i/3)]
            dev = 0 if chn<8 else 1
            sid_utterances[uid] = [saved, tid, trans, chn, dev, dur]
            uids.append(uid)

        for i,l in enumerate(num10_utt):
            tid, trans = l.split()
            uid = '-'.join((sid, tid))
            if uid in all_save_utts.keys():
                dur = wav2duration(all_save_utts[uid])
                saves_utt += 1
            else:
                dur = 0.
            saved = True if dur>0. else False
            chn = chns[int(i/2)]
            dev = 0 if chn < 8 else 1
            sid_utterances[uid] = [saved, tid, trans, chn, dev, dur]
            uids.append(uid)

        while self.num_table.rowCount() > 0:
            self.num_table.removeRow(self.num_table.rowCount() - 1)
        self.num_progressBar.setValue(int(100 * saves_utt / (len(num5_utt)+len(num10_utt))))
        for i,uid in enumerate(uids):
            # self.chns_table.
            row = self.num_table.rowCount()
            self.num_table.insertRow(row)

            item = QTableWidgetItem(str(uid))
            # item.setCheckState(QtCore.Qt.Unchecked)
            upload_icon = qtawesome.icon('fa.check-circle') if sid_utterances[uid][0] else qtawesome.icon('fa.times-circle')
            item.setIcon(upload_icon)
            item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            self.num_table.setItem(row, 0, item)

            item = QTableWidgetItem(str(sid_utterances[uid][1]))
            item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            self.num_table.setItem(row, 1, item)

            item = QTableWidgetItem(str(sid_utterances[uid][2]))
            item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            self.num_table.setItem(row, 2, item)

            item = QTableWidgetItem(str(sid_utterances[uid][3]))
            item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            self.num_table.setItem(row, 3, item)

            item = QTableWidgetItem(str(sid_utterances[uid][4]))
            item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            self.num_table.setItem(row, 4, item)

            item = QTableWidgetItem('%.2f'%(sid_utterances[uid][5]))
            item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            self.num_table.setItem(row, 5, item)

    def load_sutt_table(self, sid, chns, short_utt):

        sid_utterances = {}
        all_save_utts = {}

        with open('data/wav.scp', 'r') as f:
            for line in f.readlines():
                try:
                    uid,upath = line.split()
                    all_save_utts[uid] = upath
                except:
                    pass

        uids = []
        saves_utt = 0
        for i,l in enumerate(short_utt):
            tid, trans = l.split()
            uid = '-'.join((sid, tid))
            if '-'.join(('radio',uid)) in all_save_utts.keys():
                dur = wav2duration(all_save_utts['-'.join(('radio',uid))])
                saves_utt += 1
            else:
                dur = 0.
            saved = True if dur>0. else False
            chn = chns[int(i/13)]
            dev = 0 if chn<8 else 1
            sid_utterances[uid] = [saved, tid, trans, chn, dev, dur]
            uids.append(uid)


        while self.short_table.rowCount() > 0:
            self.short_table.removeRow(self.short_table.rowCount() - 1)
        self.short_progressBar.setValue(int(100 * saves_utt / len(short_utt)))
        for i,uid in enumerate(uids):
            # self.chns_table.
            row = self.short_table.rowCount()
            self.short_table.insertRow(row)

            item = QTableWidgetItem(str(uid))
            # item.setCheckState(QtCore.Qt.Unchecked)
            upload_icon = qtawesome.icon('fa.check-circle') if sid_utterances[uid][0] else qtawesome.icon('fa.times-circle')
            item.setIcon(upload_icon)
            item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            self.short_table.setItem(row, 0, item)

            item = QTableWidgetItem(str(sid_utterances[uid][1]))
            item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            self.short_table.setItem(row, 1, item)

            item = QTableWidgetItem(str(sid_utterances[uid][2]))
            item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            self.short_table.setItem(row, 2, item)

            item = QTableWidgetItem(str(sid_utterances[uid][3]))
            item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            self.short_table.setItem(row, 3, item)

            item = QTableWidgetItem(str(sid_utterances[uid][4]))
            item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            self.short_table.setItem(row, 4, item)

            item = QTableWidgetItem('%.2f'%(sid_utterances[uid][5]))
            item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            self.short_table.setItem(row, 5, item)

    def load_lutt_table(self, sid, chns, long_utt):

        sid_utterances = {}
        all_save_utts = {}

        with open('data/wav.scp', 'r') as f:
            for line in f.readlines():
                try:
                    uid,upath = line.split()
                    all_save_utts[uid] = upath
                except:
                    pass

        uids = []
        saves_utt = 0
        for i,l in enumerate(long_utt):
            tid, trans = l.split()
            uid = '-'.join((sid, tid))
            if '-'.join(('radio',uid)) in all_save_utts.keys():
                dur = wav2duration(all_save_utts['-'.join(('radio',uid))])
                saves_utt += 1
            else:
                dur = 0.
            saved = True if dur>0. else False
            chn = chns[int(i/9)]
            dev = 0 if chn<8 else 1
            sid_utterances[uid] = [saved, tid, trans, chn, dev, dur]
            uids.append(uid)

        self.long_progressBar.setValue(int(100*saves_utt/len(long_utt)))
        while self.long_table.rowCount() > 0:
            self.long_table.removeRow(self.long_table.rowCount() - 1)

        for i,uid in enumerate(uids):
            # self.chns_table.
            row = self.long_table.rowCount()
            self.long_table.insertRow(row)

            item = QTableWidgetItem(str(uid))
            # item.setCheckState(QtCore.Qt.Unchecked)
            upload_icon = qtawesome.icon('fa.check-circle') if sid_utterances[uid][0] else qtawesome.icon('fa.times-circle')
            item.setIcon(upload_icon)
            item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            self.long_table.setItem(row, 0, item)

            item = QTableWidgetItem(str(sid_utterances[uid][1]))
            item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            self.long_table.setItem(row, 1, item)

            item = QTableWidgetItem(str(sid_utterances[uid][2]))
            item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            self.long_table.setItem(row, 2, item)

            item = QTableWidgetItem(str(sid_utterances[uid][3]))
            item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            self.long_table.setItem(row, 3, item)

            item = QTableWidgetItem(str(sid_utterances[uid][4]))
            item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            self.long_table.setItem(row, 4, item)

            item = QTableWidgetItem('%.2f'%(sid_utterances[uid][5]))
            item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            self.long_table.setItem(row, 5, item)

    def set_Num_Trans(self):

        if self.num_table.currentRow() != -1:
            # QtWidgets.QMessageBox.information(self,
            #                                   '提示',
            #                                   "请先选择频段",
            #                                   QtWidgets.QMessageBox.Yes)

            trans = self.num_table.item(self.num_table.currentRow(), 2).text()
            chn = self.num_table.item(self.num_table.currentRow(), 3).text()
            self.chn_lineEdit.setText(chn)
            self.trans_lineEdit.setText(trans)

    def set_Short_Trans(self):

        if self.short_table.currentRow() != -1:
            # QtWidgets.QMessageBox.information(self,
            #                                   '提示',
            #                                   "请先选择频段",
            #                                   QtWidgets.QMessageBox.Yes)

            trans = self.short_table.item(self.short_table.currentRow(), 2).text()
            chn = self.short_table.item(self.short_table.currentRow(), 3).text()
            self.chn_lineEdit.setText(chn)
            self.trans_lineEdit.setText(trans)

    def set_Long_Trans(self):
        if self.long_table.currentRow() != -1:
            # QtWidgets.QMessageBox.information(self,
            #                                   '提示',
            #                                   "请先选择频段",
            #                                   QtWidgets.QMessageBox.Yes)

            trans = self.long_table.item(self.long_table.currentRow(), 2).text()
            chn = self.long_table.item(self.long_table.currentRow(), 3).text()
            self.chn_lineEdit.setText(chn)
            self.trans_lineEdit.setText(trans)

    def start_Record(self):
        tab_idx = self.rec_tab.currentIndex()
        self.sid = self.sid_lineEdit.text()

        the_table = None
        if tab_idx == 0:
            if self.num_table.currentRow() != -1:
                the_table = self.num_table
        elif tab_idx == 1:
            if self.short_table.currentRow() != -1:
                the_table = self.short_table
        elif tab_idx == 2:
            if self.long_table.currentRow() != -1:
                the_table = self.long_table

        if the_table != None:
            if not check_hackrf():
                QtWidgets.QMessageBox.information(self,
                                                  '提示',
                                                  "hackrf 连接有误！",
                                                  QtWidgets.QMessageBox.Yes)
                return
            self.uid = the_table.item(the_table.currentRow(), 0).text()
            self.chn = the_table.item(the_table.currentRow(), 3).text()
            self.cvalue = self.chns_value[int(self.chn)]

            wav_radio_path = os.path.join('data', 'wav', self.sid, 'radio', self.chn, self.uid+'.wav')
            wav_clear_path = os.path.join('data', 'wav', self.sid, 'clear', self.uid+'.wav')

            for tmp_path in [wav_radio_path, wav_clear_path]:
                if not os.path.exists(os.path.dirname(tmp_path)):
                    os.mkdir(os.path.dirname(tmp_path))

            try:
                self.rec_thread = RecordChnThread(wavpath=wav_radio_path, freq=int(self.cvalue))
                self.rec_thread.start()

                self.rem_thread = RecordMicThread(wavpath=wav_clear_path, input_device=self.input_device, sr=int(self.sr))


            except Exception as e:
                raise e
                return

            if not self.rec_thread.state:
                print('打开录入设备失败！')
                self.rec_thread.terminate()
                self.rec_thread = None
            else:
                # self.timer.start(100)1
                time.sleep(3)
                self.rem_thread.start()

                self.record_Button.setText('停止录制 ')
                self.record_Button.clicked.connect(self.stop_record)
                self.record_Button.clicked.disconnect(self.start_Record)

    def stop_record(self):

        c_uid = '-'.join(['radio', self.uid])
        m_uid = '-'.join(['clear', self.uid])

        if self.rec_thread != None and self.rec_thread.state == True:

            c_state = self.rec_thread.stop()
            # self.playBtn.setEnabled(True)
            # self.timer.stop()
            if c_state == 'success':
                c_upath = self.rec_thread.wavpath
                self.wav2scp[c_uid] = c_upath

        if self.rem_thread != None and self.rem_thread.saveFlag == True:
            m_state = self.rem_thread.stop()

            # self.playBtn.setEnabled(True)
            # self.timer.stop()
            if m_state == 'success':
                m_upath = self.rem_thread.wavpath
                self.wav2scp[m_uid] = m_upath

        if c_uid in self.wav2scp or m_uid in self.wav2scp :
            with open('data/wav.scp', 'w') as wsf:
                for l in self.wav2scp:
                    wsf.write(l + ' ' + self.wav2scp[l] + '\n')

        self.record_Button.setText('开始录制 ')
        self.record_Button.clicked.connect(self.start_Record)
        self.record_Button.clicked.disconnect(self.stop_record)

        j = int(self.sid[1:])
        chns = [1, 2, 3, 4, 5, 6, 7,8 ] if j % 2 == 0 else [9, 10, 11, 12, 13, 14, 15,16]
        # assert self.speakers[self.sid][0] == sname
        sname = self.speakers[self.sid][0]
        num5_utt, num10_utt, short_utt, long_utt = get_spk_tran(j, self.num5_set, self.num10_set, self.short_set,
                                                                self.long_set)
        self.load_tables(self.sid, sname, chns, num5_utt, num10_utt, short_utt, long_utt)
        # self.load_wav_table()