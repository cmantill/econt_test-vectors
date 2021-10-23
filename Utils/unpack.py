from unpack_utils import *
import numpy as np
import pandas as pd
import bitstring
import argparse
from functools import partial
parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, required=True, dest="inputFile", help="input file")
parser.add_argument('-n', type=int, default=13, dest="n_TX_enabled",help="number of etx enabled")
parser.add_argument('--sim', dest="sim", action='store_true', default=False, help='Input file from emulation')
parser.add_argument('--algo', type=str, required=True, dest="algo", choices=["TS","repeater","input"], help="algorithm to unpack")
parser.add_argument('--nrows', type=int, default=1, dest="nrows", help="number of rows")
args = parser.parse_args()

"""
For reading HEX files.
"""

if args.algo=="input":
    nlinks = 12
    x_names = ['RX_DATA_%i'%i for i in range(nlinks)]
else:
    nlinks = 13
    x_names = ['TX_DATA_%i'%i for i in range(nlinks)]

converters = dict.fromkeys(x_names)
for key in converters.keys():
    converters[key] = partial(int, base=16)
    
if args.sim:
    df = pd.read_csv(args.inputFile, converters=converters)[:args.nrows]
    if args.algo!="input":
        df = df.iloc[:, :args.n_TX_enabled]
else:
    df = pd.read_csv(args.inputFile,header=None,names=x_names,converters=converters)[:args.nrows]

# convert to np array
data_bxs = df.to_numpy(dtype=np.dtype(np.uint32)).flatten()

# convert to bytes
data_raw = b"".join([bitstring.BitArray(uint=d,length=32).bytes for d in data_bxs])

# unpack data
if args.algo=='TS':
    data_rows = TS_unpack(data_raw)
elif args.algo=='repeater':
    data_rows = Repeater_unpack(data_raw)
elif args.algo=='input':
    df2 = pd.read_csv(args.inputFile)[:args.nrows]
    tc_0 = (np.vectorize(int)(df2,16) >> 21) & 127
    tc_1 = (np.vectorize(int)(df2,16) >> 14) & 127
    tc_2 = (np.vectorize(int)(df2,16) >> 7) & 127
    tc_3 = np.vectorize(int)(df2,16) & 127
    df2[[f'ADC_TC_{i}' for i in range(0,48,4)]] = pd.DataFrame(tc_0,index=df2.index)
    df2[[f'ADC_TC_{i}' for i in range(1,48,4)]] = pd.DataFrame(tc_1,index=df2.index)
    df2[[f'ADC_TC_{i}' for i in range(2,48,4)]] = pd.DataFrame(tc_2,index=df2.index)
    df2[[f'ADC_TC_{i}' for i in range(3,48,4)]] = pd.DataFrame(tc_3,index=df2.index)
    print( df2[[f'ADC_TC_{i}' for i in range(48)]])
    data_rows = Input_unpack(data_raw)
else:
    print('no selected algo')
    exit
    
for d in data_rows:
    print(d['BX'],d['Charge'],len(d['Charge']))
