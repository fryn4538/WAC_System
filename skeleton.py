#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skeleton for the wireless communication system project in Signals and
Transforms

For plain text inputs, run:
$ python3 skeleton.py "Hello World!"

For binary inputs, run:
$    print('Received: ' + data_rx)
 python3 skeleton.py -b 010010000110100100100001

2020 -- Roland Hostettler <roland.hostettler@angstrom.uu.se>
"""

import sys
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import wcslib as wcs

"""
Main
"""
def lowpass():
    fn = 5400
    wp = 1875/fn
    ws = 1950/fn
    gpass = 3
    gstop = 40

    b, a = signal.iirdesign(wp, ws, gpass, gstop)
    return [b,a]


def bandpass():
    fn = 5400
    wp = [1725/fn, 1875/fn]
    ws = [1650/fn, 1950/fn]
    gpass = 3
    gstop = 40

    b, a = signal.iirdesign(wp, ws, gpass, gstop)
    return [b,a]


def main(s = ""):
    # Parameters
    Kb = 432     # Symbol width in samples
    fs = 10800   # Sampling frequency in Hz
    pi = np.pi
    cos = np.cos
    sin = np.sin
    e = np.e

    lp = lowpass()
    bp = bandpass()
    # Detect input or set defaults
    string_data = True
    if (s != ""):
        data = s

    elif len(sys.argv) == 2:
        data = str(sys.argv[1])

    elif len(sys.argv) == 3 and str(sys.argv[1]) == '-b':
        string_data = False
        data = str(sys.argv[2])

    else:
        print('Warning: No input arguments, using defaults.', file=sys.stderr)
        data = "Hello World!"

    # Convert string to bit sequence or string bit sequence to numeric bit
    # sequence
    if string_data:
        bs = wcs.encode_string(data)
    else:
        bs = np.array([bit for bit in map(int, data)])

    # Encode baseband signal
    xb = wcs.encode_baseband_signal(bs, Kb)

    # TODO: Put your transmitter code here (feel free to modify any other parts
    # too, of course)
    Oc = 1800 * 2 * pi
    Ac = 2
    Ts = 1/10800
    xm =  np.zeros(len(xb))
    xc =  np.zeros(len(xb))

    for k in range(0, len(xb)):
        xm[k] = xb[k]*Ac*np.sin(Oc*k*Ts)

    xt = signal.lfilter(bp[0], bp[1], xm)

    yr = wcs.simulate_channel(xt, fs)
    ym = signal.lfilter(bp[0], bp[1], yr)
    yi = yq = np.zeros(len(ym))

    for k in range(0, len(yi)):
        yi[k] =  ym[k]*np.cos(Oc*k*Ts)
        yq[k] =  (-1)*ym[k]*np.sin(Oc*k*Ts)

    ybq = signal.filtfilt(lp[0], lp[1], yq)
    ybi = signal.filtfilt(lp[0], lp[1], yi)

    yb = ybi + 1j*ybq

    ybm = np.sqrt((ybi**2) + (ybq**2))

    ybp = np.arctan2(ybq, ybi)

    br = wcs.decode_baseband_signal(ybm, ybp, Kb)

    data_rx = wcs.decode_string(br)
    if(s == ""):
        print("Sent:\t\t" + data)
        print("Received:\t" + data_rx)
    br = list(map(int, br))

    wrongStr = 0
    wrongLen = 0
    wrongChar = 0

    if data != data_rx:
        wrongStr += 1
        l = 0
        if(len(bs) == len(br)):
            l = len(bs)
        elif(len(bs) < len(br)):
            wrongLen += 1
            wrongChar += len(br) - len(bs)
            l = len(bs)
        else:
            wrongLen += 1
            wrongChar += len(bs) - len(br)
            l = len(br)

        for k in range(0,l):
            if bs[k] != br[k]:
                wrongChar += 1
                #print("k:" , k, "bs:",bs[k],"br:", br[k])
        #print("Fail")

    #print("----------------------------------------------------------------------------")
    return [wrongStr, wrongChar, wrongLen]

if __name__ == "__main__":
    if (len(sys.argv) == 3 and str(sys.argv[1]) == '-t'):
        K = int(sys.argv[2])

        five = "tests"
        ten = "this is at"
        twenty = "this is atthis is at"
        fifty = "this is atthis is atthis is atthis is atthis is at"

        fiveStr = []
        fiveChar = []
        fiveLen = []

        tenStr = []
        tenChar = []
        tenLen = []

        twentyStr = []
        twentyChar = []
        twentyLen = []

        fiftyStr = []
        fiftyChar = []
        fiftyLen = []

        for i in range(0,K):
            if(i % 5 == 0):
                print(str((i/K)*100) + "%")

            res = main(five)
            fiveStr.append(res[0])
            fiveChar.append(res[1])
            fiveLen.append(res[2])

            res = main(ten)
            tenStr.append(res[0])
            tenChar.append(res[1])
            tenLen.append(res[2])

            res = main(twenty)
            twentyStr.append(res[0])
            twentyChar.append(res[1])
            twentyLen.append(res[2])

            res = main(fifty)
            fiftyStr.append(res[0])
            fiftyChar.append(res[1])
            fiftyLen.append(res[2])

        print("Number of samples: " + str(K))

        print("----------------------------------------------------------------------------")
        print("Result corrupted strings 5: " + str((sum(fiveStr)/K)*100) + "%")
        print("Result corrupted strings 10: " + str((sum(tenStr)/K)*100) + "%")
        print("Result corrupted strings 20: " + str((sum(twentyStr)/K)*100) + "%")
        print("Result corrupted strings 50: " + str((sum(fiftyStr)/K)*100) + "%")
        print("----------------------------------------------------------------------------")
        print("Result corrupted strings length 5: " + str((sum(fiveLen)/K)*100) + "%")
        print("Result corrupted strings length 10: " + str((sum(tenLen)/K)*100) + "%")
        print("Result corrupted strings length 20: " + str((sum(twentyLen)/K)*100) + "%")
        print("Result corrupted strings length 50: " + str((sum(fiftyLen)/K)*100) + "%")
        print("----------------------------------------------------------------------------")
        print("Result corrupted characters 5: " + str((sum(fiveChar)/(K*5))*100) + "%")
        print("Result corrupted characters 10: " + str((sum(tenChar)/(K*10))*100) + "%")
        print("Result corrupted characters 20: " + str((sum(twentyChar)/(K*20))*100) + "%")
        print("Result corrupted characters 50: " + str((sum(fiftyChar)/(K*50))*100) + "%")
        print("----------------------------------------------------------------------------")
        totalErr = sum(fiveChar) + sum(tenChar) + sum(twentyChar) + sum(fiftyChar)
        totalChar = K*(5+10+20+50)
        print("Bit rate error: " + str((totalErr/totalChar)*100)+ "%")
    else:
        main()
