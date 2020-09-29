#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Top Block
# Generated: Mon Jul 13 23:11:42 2020
##################################################

from gnuradio import analog
from gnuradio import audio
from gnuradio import blocks
from gnuradio import filter
from gnuradio import gr
from gnuradio.filter import firdes
import osmosdr
import time
import argparse

parser = argparse.ArgumentParser(description='Speaker Recognition System for record wav')
# Model options
parser.add_argument('--wavpath', type=str, default='data\\wav\\tmp\\tmp.wav', help='path to dataset')
parser.add_argument('--freq', type=float, default=401.195e6, help='path to voxceleb1 test dataset')
args = parser.parse_args()

class top_block(gr.top_block):

    def __init__(self, freq, wavpath):
        gr.top_block.__init__(self, "Top Block")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 4e6
        self.freq = freq

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=12,
                decimation=5,
                taps=None,
                fractional_bw=0.01,
        )
        self.osmosdr_source_0 = osmosdr.source( args="numchan=" + str(1) + " " + 'hackrf=0' )
        self.osmosdr_source_0.set_time_now(osmosdr.time_spec_t(time.time()), osmosdr.ALL_MBOARDS)
        self.osmosdr_source_0.set_sample_rate(samp_rate)
        self.osmosdr_source_0.set_center_freq(freq, 0)
        self.osmosdr_source_0.set_freq_corr(0, 0)
        self.osmosdr_source_0.set_dc_offset_mode(0, 0)
        self.osmosdr_source_0.set_iq_balance_mode(0, 0)
        self.osmosdr_source_0.set_gain_mode(False, 0)
        self.osmosdr_source_0.set_gain(0, 0)
        self.osmosdr_source_0.set_if_gain(35, 0)
        self.osmosdr_source_0.set_bb_gain(62, 0)
        self.osmosdr_source_0.set_antenna('', 0)
        self.osmosdr_source_0.set_bandwidth(200000, 0)

        self.low_pass_filter_0 = filter.fir_filter_ccf(20, firdes.low_pass(
        	1, samp_rate, 75e3, 25e3, firdes.WIN_HAMMING, 6.76))
        self.blocks_wavfile_sink_0 = blocks.wavfile_sink(wavpath, 1, 48000, 16)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vff((1.4, ))
        # self.audio_sink_0 = audio.sink(48000, '', False)
        self.analog_simple_squelch_cc_0 = analog.simple_squelch_cc(-20.8, 1e-3)
        self.analog_nbfm_rx_1 = analog.nbfm_rx(
        	audio_rate=48000,
        	quad_rate=480000,
        	tau=75e-6,
        	max_dev=10e3,
          )

        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_nbfm_rx_1, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.analog_simple_squelch_cc_0, 0), (self.analog_nbfm_rx_1, 0))
        # self.connect((self.blocks_multiply_const_vxx_0, 0), (self.audio_sink_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_wavfile_sink_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.osmosdr_source_0, 0), (self.low_pass_filter_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.analog_simple_squelch_cc_0, 0))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.osmosdr_source_0.set_sample_rate(self.samp_rate)
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, 75e3, 25e3, firdes.WIN_HAMMING, 6.76))

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.osmosdr_source_0.set_center_freq(self.freq, 0)


def main(top_block_cls=top_block, options=None):

    try:
        tb = top_block_cls(wavpath=args.wavpath, freq=args.freq)
        tb.start()

        raw_input('Press Enter to quit: ')
    except EOFError:
        pass
        tb.stop()
        tb.wait()
    except Exception as e:
        raise e


if __name__ == '__main__':
    main()

# try:
#     tb = top_block(wavpath=args.wavpath, freq=args.freq)
#     tb.start()
#     raw_input('Press Enter to quit: ')
# except EOFError:
#     tb.stop()
#     tb.wait()
# except Exception as e:
#     raise e


