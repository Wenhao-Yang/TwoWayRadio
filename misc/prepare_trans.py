#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@author:WILLIAM
@file: prepare_trans.py
@time: 21:24
@Device: Personal Win10
@Description: 
"""
import random

def get_utt_sets(file_path='data/transcript/long.txt', num_tran=100):

    all_sets = []
    with open(file_path, 'r') as lf:
        all_tras = [l for l in lf.readlines()] #BAC009S0002W0122 而对楼市成交抑制作用最大的限购

    random.seed(12345)
    random.shuffle(all_tras)
    tmp_set = []
    for i,tra in enumerate(all_tras):
        tmp_set.append(tra)
        if (i+1) % num_tran == 0:
            all_sets.append(tmp_set.copy())
            tmp_set = []

    return all_sets

def get_num_sets(file_path='data/transcript/num5.txt', num_tran=24):

    all_sets = []
    with open(file_path, 'r') as lf:
        all_tras = [l for l in lf.readlines()] #TWRSRN13251 四七七八七五四幺八八

    tmp_set = []
    for i, tra in enumerate(all_tras):
        tmp_set.append(tra)
        if (i + 1) % num_tran == 0:
            all_sets.append(tmp_set.copy())
            tmp_set = []

    return all_sets

def get_spk_tran(idx, num5_set, num10_set, short_set, long_set):
    num_subset = min(len(num5_set), len(num10_set), len(short_set), len(long_set))
    idx %= num_subset

    return num5_set[idx], num10_set[idx], short_set[idx], long_set[idx]