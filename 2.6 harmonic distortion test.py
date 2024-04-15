'''
Test - 2.7  Harmonic Distortion
Test description - This test gives out the value the 2nd harmonic power and compare the given threshold to conclude the result hormonic power
Equipment required -
Lucid device - LS1291D
Spectrum analyzer- Agilent Technologies, E4440A (PSA Series spectrum analyzer)
what is happening in thi sscript ?
- - After initializing the device, all the parameter are define in 2nd section,
 - span and center frequency is selected according to the given table
 - reference of the spectrum must be set  5 dbm above the given power level
 -we check the given  freq and power using power_at_centerFrequency function
 - then we multiple the centre frequency with a factor of 2 to get the power at second harmonic frequency using  power_at_second_harmonics function
 - after comparing with the threshold , the final result is concluded
- A test report will be generated at the end of the script and is saved as a text file in the same directory
 '''
import os
import sys
import time
import numpy as np
import ctypes
import _ctypes
import pyvisa as visa
def connect():
    hLib = ctypes.cdll.LoadLibrary('lucidsdk_x64_cpp.dll')
    initChannelProto = ctypes.WINFUNCTYPE(
        ctypes.c_int,       # Return type.
        ctypes.c_int,       # int spiType
        ctypes.c_uint,      # unsigned int device_idx
        ctypes.c_char_p,    # const char * log_path
        ctypes.c_int        # int log_mode
    )
    initChannelParams = (1, "p1", 0), (1, "p2", 0), (1, "p3", 0), (1, "p4", 0)

    # Actually map the call ("initChannel(...)") to a Python name.
    initChannel = initChannelProto(("initChannel", hLib), initChannelParams)

    p1 = ctypes.c_int(0)
    p2 = ctypes.c_uint(0)
    p3 = ctypes.c_char_p(bytes(b'lucid_log.txt'))
    p4 = ctypes.c_int(0)

    res = initChannel(p1, p2, p3, p4)
    if (not res):
        disconnect(hLib)
        return None
    else:
        return(hLib)
def disconnect(hLib):
    if(hLib == None):
        return
    # Unload the DLL so that it can be rebuilt
    libHandle = hLib._handle
    _ctypes.FreeLibrary(libHandle)
    del hLib
def sendScpi(command, hLib):
    if (hLib == None):
        return
    # int SendScpi(char const *,char *,unsigned int)
    SendScpiProto = ctypes.WINFUNCTYPE(
        ctypes.c_int,       # Return type
        ctypes.c_char_p,    # const char * scpi command
        ctypes.c_char_p,    # char * response
        ctypes.c_int,       # max input, in chars
    )
    SendScpiParams = (1, "cmd", 0), (1, "answer", 0), (1, "nchars", 0)
    sendScpi = SendScpiProto(("SendScpi", hLib), SendScpiParams)
    #print(sendScpi)
    answer = ctypes.create_string_buffer(1024)
    cmd = ctypes.create_string_buffer(bytes(command, 'utf-8'))
    nchars = ctypes.c_int(64)

    rv = sendScpi(cmd, answer, nchars)
    if (rv <= -1):
        print("error")
def send_scpi_query(dev, query):
    try:
        resourceManager = visa.ResourceManager()
        session = resourceManager.open_resource(dev)

        # Need to define the termination string
        session.write_termination = '\n'
        session.read_termination = '\n'

        #print('IDN: ' + str(session.query(query)))
        response = str(session.query(query))
        session.close()
        return response

    except Exception as e:
        print('[!] Exception: ' + str(e))
def connect_spectrum_via_lan():
    device_address = 'TCPIP::192.90.70.36::5025::SOCKET'
    try:
        rm = visa.ResourceManager()
        spectrum_analyzer = rm.open_resource(device_address)
        spectrum_analyzer.timeout = 2000
        spectrum_analyzer.write_termination = '\n'
        spectrum_analyzer.read_termination = '\n'
        print(spectrum_analyzer)
    except visa.Error as e:
        print("Error while connecting: {}".format(e))
    try:
        # Query the *IDN? command to get the identification string
        spectrum_analyzer.write('*IDN?')
        # spectrum_analyzer.timeout = 1000
        idn_response = spectrum_analyzer.read()
        spectrum_analyzer.write('*RST')
        spectrum_analyzer.write('*CLS')

        print("IDN Response: {}".format(idn_response))
    except visa.Error as e:
        print("Error reading IDN: {}".format(e))
    return spectrum_analyzer
def second_harmonic_distortion(freq_out):
    spectrum_analyzer.write(':INIT:CONT OFF')
    spectrum_analyzer.write(':TRIGger[:SEQuence]:SOURce IMM')
    spectrum_analyzer.write(':INIT:IMM')
    spectrum_analyzer.write('*TRG')
    spectrum_analyzer.write(':CONFigure:HARMonics')
    time.sleep(2)
    spectrum_analyzer.write(':INITiate:HARMonics')
    time.sleep(5)
    spectrum_analyzer.write(":FETCh:HARMonics:AMPLitude1?")
    time.sleep(2)
    spectrum_analyzer.write(':MEASure:HARMonics:AMPLitude1?')
    time.sleep(10)
    spectrum_analyzer.write(':READ:HARMonics:AMPLitude1?')
    time.sleep(2)
    resp1 = spectrum_analyzer.read()
    # spectrum_analyzer.write(":FETCh:HARMonics:AMPLitude2?")
    # time.sleep(2)
    # spectrum_analyzer.write(':MEASure:HARMonics:AMPLitude2?')
    # time.sleep(2)
    spectrum_analyzer.write(':READ:HARMonics:AMPLitude2?')
    time.sleep(10)
    resp2 = spectrum_analyzer.read()
    resp3 = float(resp2) - float(resp1)
    print('1st harmonic {1} dBm,2st HD power {0} dBc '.format(resp3,resp1))
    return resp3
def power_at_second_harmonics(center_frequency):
    second_freq = 2*center_frequency
    spectrum_analyzer.write(':CALC:MARK2:STAT ON;:CALC:MARK2:X {} MHz'.format(second_freq))
    time.sleep(1)
    spectrum_analyzer.write('CALC:MARK2:X?')
    time.sleep(1)
    resp = spectrum_analyzer.read()
    time.sleep(1)
    freq_out = float(resp) / 1e6
    time.sleep(1)
    spectrum_analyzer.write('CALC:MARK2:Y?')
    time.sleep(1)
    power_max = spectrum_analyzer.read()
    time.sleep(1)
    print('power at second harmonic ={0},at freq= {1},which should be around {2}'.format(power_max,freq_out,second_freq))
    return power_max

def power_at_centerFrequency(spectrum_analyzer):
    spectrum_analyzer.write(':CALC:MARK1:STAT ON;:CALC:MARK1:MAX')
    time.sleep(1)
    spectrum_analyzer.write('CALC:MARK1:X?')
    time.sleep(1)
    resp = spectrum_analyzer.read()
    time.sleep(1)
    freq_out = float(resp) / 1e6
    #print('centre frequency = {} MHz'.format(freq_out))
    time.sleep(1)
    spectrum_analyzer.write('CALC:MARK1:Y?')
    time.sleep(1)
    power_max = spectrum_analyzer.read()
    time.sleep(1)
    print('power ={1} dBm at frequency = {0} MHz'.format(freq_out, power_max))
    return power_max,freq_out

handle = connect()
# Initilization
sendScpi('*RST', handle)
sendScpi('*IDN?', handle)
sendScpi(':SYST:ERR?', handle)
sendScpi(':INST 1;:INST:ACT 1', handle)
spectrum_analyzer = connect_spectrum_via_lan()
spectrum_analyzer.write(':INIT:REST')
print('Initialized')
test_success = True
####################################################################
# Input Parameters (madify this for 40G accordingly)
frequency_list =[10]# [10,15,25,35,60,85,93.75,93.751,130,190,240,315,365,400,401,500,700,800,900,1500,1501,1800,2100,2400,2401,2700,3000,4500,6000,6001,6800,7400,8000,8001,8800,9600,11300,12000]
power_list= [-15,0,15]
table_i = 0
###Test Report Table parameters
serial_no_tb = np.zeros(len(frequency_list)*len(power_list))
input_list_tb = np.zeros(len(frequency_list)*len(power_list))
power_list_tb = np.zeros(len(frequency_list)*len(power_list))
power_out_tb=np.zeros(len(frequency_list)*len(power_list))
freq_out_tb =np.zeros(len(frequency_list)*len(power_list))
output_list_tb = np.zeros(len(frequency_list)*len(power_list))
output_status_tb= []# To store the output frequency from spectrum analyzer (optional step)
error_limit_tb = -40+np.zeros(len(frequency_list)*len(power_list)) # error limit in dBm
###########################################
for i in range(len(frequency_list)):
    center_frequency = frequency_list[i]
    for power_in_dBm in power_list:
        ref_level = power_in_dBm + 5  # reference level on the spectrum must be 5dBm above the signal power level
        threshold = error_limit_tb[table_i] + power_in_dBm
        sendScpi(':FREQuency {}MHz'.format(center_frequency), handle)
        sendScpi(':POWer {}'.format(power_in_dBm), handle)
        sendScpi(':OUTPut ON', handle)
        spectrum_analyzer.write('DISP:WIND:TRAC:Y:RLEV {} dbm'.format(ref_level))
        time.sleep(2)
        spectrum_analyzer.write('FREQ:CENT {}MHz'.format(center_frequency))
        time.sleep(2)
        spectrum_analyzer.write('FREQ:STAR {}MHz'.format(center_frequency / 10))
        spectrum_analyzer.write('FREQ:STOP {}MHz'.format(center_frequency * 20))
        time.sleep(2)
        power_out_tb[table_i],freq_out_tb[table_i]=power_at_centerFrequency(spectrum_analyzer) # function to read power from spectrum analyzer
        output_list_tb[table_i]=power_at_second_harmonics(center_frequency)
######################################################
        #output_list_tb[table_i]= second_harmonic_distortion(freq_out_tb[table_i])
        serial_no_tb[table_i] = table_i + 1
        input_list_tb[table_i] = center_frequency
        power_list_tb[table_i] = power_in_dBm
        if output_list_tb[table_i] <threshold:
            output_status_tb.append("pass")
            print("TEST pass for frequency {}MHz".format(center_frequency))
        else:
            test_success = False
            output_status_tb.append("fail")
            print("TEST FAIL for frequency {}MHz".format(center_frequency))

        table_i =table_i +1
if test_success:
    print("Test successed!")
else:
    print("Test failed ")
    # disconnecting the instruments
spectrum_analyzer.close()
disconnect(handle)
##########################################
#Test report
from tabulate import tabulate
# Sample data for the table
data = list(zip(serial_no_tb,input_list_tb,power_list_tb,error_limit_tb,freq_out_tb,power_out_tb,output_list_tb,output_status_tb))
# Creating the table
table = tabulate(data, headers=["Test step","Input frequency","Power","Error Limits (in dBc)","Output frequency","Output Power","Max HD Spectrum reading(2nd harmonic)","PASS/FAIL"], tablefmt="grid")
# Displaying the table
print(table)
# Writing the table to a text file
with open("Harmonic distortion test report.txt", "w") as f:
    f.write(table)

print("Table has been written to table.txt")

## To do later - work on the direct method to get the harmonics (function already created as "second_harmonic_distortion") rather then positioning the marker 2 at twice of the centre frequency and getting the power of it to verify the 2nd harmonic distortion