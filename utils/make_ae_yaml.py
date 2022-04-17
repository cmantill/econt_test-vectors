import h5py
import numpy as np

def toDecimal(x):
    w = -1. if x[0]=='1' else 0
    w += int(x[1:],2)/2**5
    return w

#convert decimal values to the 6 bit binary encoding
def toBinary(x):
    if x<0:
        w='1'
        val=x+1
    else:
        w='0'
        val=x
    w += f'{int((val)*2**5):05b}'
    return w

toBinary=np.vectorize(toBinary)

def splitTo16Bytes(x):
    return [(x>>(i*128)) & 0xffffffffffffffffffffffffffffffff for i in range(9)]

def i2cDictToWeights(i2cDict):
    bits=''
    for i in range(12)[::-1]:
        reg_name=f'AUTOENCODER_{i}INPUT_weights_byte128'
        r=f'{i2cDict[reg_name]:048b}'
        bits += r
        for j in range(0,127,16)[::-1]:
            reg_name=f'AUTOENCODER_{i}INPUT_weights_byte{j}'
            r=f'{i2cDict[reg_name]:0128b}'
            bits += r
    wbWB=[toDecimal(bits[i:i+6]) for i in range(0,len(bits),6)][::-1]
    _w=wbWB[:72]
    _b=wbWB[72:80]
    _W=wbWB[80:2128]
    _B=wbWB[2128:]
    return _w,_b,_W,_B

def writeYaml(fName, AE_weight_12_split):
    yamlOutput="""
ECON-T:
 RW:
  MFC_ALGORITHM_SEL_DENSITY:
   registers:
    algo:
     value: 0x4

  FMTBUF_ALL:
   registers:
    mask_ae:
     value: 0xffff_ffff_ffff_ffff_ffff_ffff_ffff_ffff
    mask_ae2:
     value: 0xffff
"""
    i=0
    for i in range(12):
        yamlOutput += f"""
  AUTOENCODER_{i}INPUT:
   registers:
    weights_byte0:
     value: {hex(AE_weight_12_split[i][0])}
    weights_byte16:
     value: {hex(AE_weight_12_split[i][1])}
    weights_byte32:
     value: {hex(AE_weight_12_split[i][2])}
    weights_byte48:
     value: {hex(AE_weight_12_split[i][3])}
    weights_byte64:
     value: {hex(AE_weight_12_split[i][4])}
    weights_byte80:
     value: {hex(AE_weight_12_split[i][5])}
    weights_byte96:
     value: {hex(AE_weight_12_split[i][6])}
    weights_byte112:
     value: {hex(AE_weight_12_split[i][7])}
    weights_byte128:
     value: {hex(AE_weight_12_split[i][8])}
"""
    with open(fName,'w') as _file:
        _file.write(yamlOutput)
    return yamlOutput

def AE_h5_to_yaml(h5_fileName, yamlFileName):
    f = h5py.File(h5_fileName, 'r')

    #load conv layer weights (w) and biases (b) and dense layer weights (W) and biases (B)
    w=f['conv2d_0_m']['conv2d_0_m']['kernel:0'][:]
    b=f['conv2d_0_m']['conv2d_0_m']['bias:0'][:]
    W=f['encoded_vector']['encoded_vector']['kernel:0'][:]
    B=f['encoded_vector']['encoded_vector']['bias:0'][:]

    #saturate values (in case they weren't quantized)
    w=np.maximum(np.minimum(w,.99999),-1)
    b=np.maximum(np.minimum(b,.99999),-1)
    W=np.maximum(np.minimum(W,.99999),-1)
    B=np.maximum(np.minimum(B,.99999),-1)

    #convert to binary representations
    w_bin=toBinary(w.flatten())
    b_bin=toBinary(b.flatten())
    W_bin=toBinary(W.flatten())
    B_bin=toBinary(B.flatten())

    #merge into bit strings (inverted because first weights are the LSB)
    w_bin_string=''.join(w_bin[::-1])
    b_bin_string=''.join(b_bin[::-1])
    W_bin_string=''.join(W_bin[::-1])
    B_bin_string=''.join(B_bin[::-1])

    reg_string_full=B_bin_string + W_bin_string + b_bin_string + w_bin_string

    #split into the 12 AE weight groups specified in RTL registers
    AE_weight_12 = [int(reg_string_full[n:n+1072],2) for n in range(0,len(reg_string_full),1072)][::-1]

    #split the weight grouyps into 16 byte registers for test setup
    AE_weight_12_split = [splitTo16Bytes(x) for x in AE_weight_12]

    writeYaml(yamlFileName, AE_weight_12_split)

if __name__=='__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='encoder.hdf5', dest='h5_file_name', help=".hdf5 file containing model weights")
    parser.add_argument('--yaml',  type=str, default='AE.yaml', dest='yaml_file_name', help="yaml output file with i2c register values")
    args = parser.parse_args()

    AE_h5_to_yaml(args.h5_file_name, args.yaml_file_name)