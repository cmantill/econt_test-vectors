import bitstruct
import numpy as np

def Input_unpack(data):
    offset = 0
    rows = []
    neRx = 12
    possible_headers = [9,10]
    try:
        while True:
            charges = []
            for i in range(neRx):
                header, = bitstruct.unpack_from('u4', data, offset=offset)
                offset += bitstruct.calcsize('u4')

                if header not in possible_headers:
                    print(f'Bad BX {header}')
                    offset = start_offset + 16
                    continue
            
                NTCQ = 4
                charge = np.array(bitstruct.unpack_from('u7'*NTCQ, data, offset=offset))
                charges.extend(list(charge))
                offset += 7*NTCQ

            rows.append({'BX'      : header,
                         'Charge'  : charges})

    except bitstruct.Error:
        print('bitstruct error - offset',offset)
        pass
    return rows

def Repeater_unpack(data,neTx=13):
    offset = 0
    rows = []
    nTC = 48
    possible_headers = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,31]
    try:                
        while True:
            start_offset = offset
            header, = bitstruct.unpack_from('u5', data, offset=offset)
            offset += bitstruct.calcsize('u5')

            if header not in possible_headers:
                print(f'Bad BX {header}')
                offset = start_offset + 16
                continue

            # 16 bit words * 2 * number of eTX - (nTC * 7bit + header)
            padding_bits = (16*2*neTx)- (nTC*7 + 5)
            charge = np.array(bitstruct.unpack_from('u7'*48, data, offset=offset))
            offset += bitstruct.calcsize('u7'*48)
            if padding_bits > 0:
                padding = bitstruct.unpack_from(f'u{padding_bits}', data, offset=offset)
                offset += padding_bits
                
            rows.append({'BX'      : header,
                         'Charge'  : charge})

            expBX = ((header + 1) % 16) if (header != 31) else 1
            while True:
                nextHeader, = bitstruct.unpack_from('u5', data, offset=offset)
                offset += bitstruct.calcsize('u5')
                if nextHeader==expBX:
                    offset -= bitstruct.calcsize('u5')
                    break
    except:
        print('bitstruct error - offset',offset)
        pass
    return rows
            
def TS_unpack(data):
    offset = 0
    rows = []
    try:
        while True:
            start_offset = offset

            # sum can be sum of all 48 TC or the sum of non-transmitted TC
            header = bitstruct.unpack_from_dict('u5u3u8', ['BX', 'Type', 'Sum'], data, offset=offset)
            offset += bitstruct.calcsize('u5u3u8')

            if header['Type'] == 0b100: # high occupancy
                print('high occupancy')
                # 3 words of channel map
                addr = np.array(bitstruct.unpack_from('b1'*48, data, offset=offset), bool)
                offset += bitstruct.calcsize('b1'*48)
                NTCQ = sum(addr)
                # 22 16 bit words - NTCQ * (7 bit charge)
                padding_bits = (22*16 - NTCQ*7) 
                charge = np.array(bitstruct.unpack_from('u7'*NTCQ, data, offset=offset))
                offset += 7*NTCQ
                if padding_bits > 0:
                    padding = bitstruct.unpack_from(f'u{padding_bits}', data, offset=offset)
                    offset += padding_bits
                else:
                    padding = None
                rows.append({'BX'      : header['BX'],
                             'Type'    : header['Type'],
                             'Sum'     : header['Sum'],
                             'Addr'    : addr,
                             'NTCQ'    : NTCQ,
                             'Charge'  : charge,
                             'Padding' : padding})
            elif header['Type'] == 0b010: # low occupancy
                print('low occupancy')
                # 3 bit number of TC
                NTCQ, = bitstruct.unpack_from('u3', data, offset=offset)
                offset += 3
                # 6 bit address for each TC
                addr = np.array(bitstruct.unpack_from('u6'*NTCQ, data, offset=offset))
                offset += NTCQ*6
                # 7 bit charge for each TC
                charge = np.array(bitstruct.unpack_from('u7'*NTCQ, data, offset=offset))
                offset += NTCQ*7
                # 25 16 bit words - ((NTCQ bits) + NTCQ * (6 bit addr + 7 bit charge))
                padding_bits = (25*16 - (3 + NTCQ*13))
                if padding_bits > 0:
                    padding = bitstruct.unpack_from(f'u{padding_bits}', data, offset=offset)
                    offset += padding_bits
                else:
                    padding = None
                rows.append({'BX'      : header['BX'],
                             'Type'    : header['Type'],
                             'Sum'     : header['Sum'],
                             'Addr'    : addr,
                             'NTCQ'    : NTCQ,
                             'Charge'  : charge,
                             'Padding' : padding})
            elif header['Type'] in (0b000, 0b110, 0b111): # Zero occupancy or two types of truncated frame
                if header['Type']==0b000: 
                    print('zero')
                elif header['Type']==0b110: 
                    print('from T1 truncation', 'Bx ', header['BX'], ' sum ',header['Sum'])
                elif header['Type']==0b111:
                    print('from T2 or T3 truncation', 'Bx ', header['BX'], ' sum ',header['Sum'])
                rows.append({'BX'      : header['BX'],
                             'Type'    : header['Type'],
                             'Sum'     : header['Sum'],
                             'Addr'    : None,
                             'NTCQ'    : 0,
                             'Charge'  : None,
                             'Padding' : None})

            # Now move past any idle words
            N_idles = 0
            sync_words = []
            expBX = ((header['BX'] + 1) % 16) if (header['BX'] != 31) else 1
            while True:
                nextBX, = bitstruct.unpack_from('u5', data, offset=offset)
                if nextBX == header['BX']:
                    N_idles += 1
                    sync_words.append(bitstruct.unpack_from('u11', data, offset = offset+5))
                    offset += 16
                else:
                    rows[-1]['N_idles'] = N_idles
                    rows[-1]['Sync_words'] = sync_words
                    break

            if nextBX != expBX:
                print(f'Wrong BX progression from {header["BX"]} to {nextBX}, expected {expBX}')
                offset = start_offset + 16
                rows = rows[:-1]
                continue
            
    except bitstruct.Error:
        print('bitstruct error - offset',offset)
        pass
    return rows