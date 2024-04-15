'''
Test - 2.8 Spurious next to carrier 
Test description- This test verifies, there is no spurious present next the the carrier above the defined error limit
Equipment required - 
Lucid device - LS1291D
Spectrum analyzer- Agilent Technologies, E4440A (PSA Series spectrum analyzer)
what is happening in thi sscript ?
 - After initializing the device, all the parameter are define in 2nd section,
 - span and center frequency is selected according to the signal frequency (using if/else condition)
 - using 3 marker, the script is checking the peak, peak right and peak left, 
 - if all these marker values are same, then we conclude that there is not spurious above -60dBc neXt to the carrier.
 -and if the marker value is not then we check if the power level is above threshold, then we conclude the final results
-  A test report will be generated at the end of the script and is saved as a text file in the same directory '''''
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
# Input Parameters
frequency_list =[800]# list(np.arange(20,110,10))+list(np.arange(150,1050,50))+list(np.arange(1250,12250,250)) # list of frequencies to be tested
res_BW = 200 # resolution bandwisth in KHz
video_BW = 400 # video bandwidth in Hz
output = np.zeros(len(frequency_list)) # To store the output frequency from spectrum analyzer (optional step)
power_in_dBm = 5.0 # power level required for the test in dBm
ref_level = power_in_dBm+5 # reference level on the spectrum must be 5dBm above the signal power level
error_limit = -60 # error limit in dBm
threshold = error_limit - power_in_dBm
################
# Parameters for test report
table_i=0
serial_no = np.zeros(len(frequency_list))
input_list = np.zeros(len(frequency_list))
output_list = np.zeros(len(frequency_list))
output_status_list = []# To store the output frequency from spectrum analyzer (optional step)
error_limit = -60+np.zeros(len(frequency_list)) # error limit in dBm


#######################################################################
#Main
spectrum_analyzer.write('DISP:WIND:TRAC:Y:RLEV {} dbm'.format(ref_level)) # set reference power level
spectrum_analyzer.write(':BWID:RES {}KHz'.format(res_BW)) # resolutrion bandwidth
spectrum_analyzer.write(':BWID:VID {}Hz'.format(video_BW)) # video bandwidth
time.sleep(1)
for i in range(len(frequency_list)): # iterating over each frequency (main loop)
    center_frequency = frequency_list[i]
    serial_no[table_i] = table_i+1
    input_list[table_i]=center_frequency
    # selecting span and center frequncy for the spectrum depending on the given signal frequecny
    if center_frequency <= 20 or center_frequency <=100:
        step_size = 10
        span_sa = 20
    elif center_frequency <= 150 or center_frequency <=1000:
        step_size = 50
        span_sa = 30
    elif center_frequency <= 1250 or center_frequency <= 12000:
        step_size = 50
        span_sa = 40
    else:
        continue
    sendScpi(':FREQuency {}MHz'.format(center_frequency), handle)
    sendScpi(':POWer {}'.format(power_in_dBm), handle)
    sendScpi(':OUTPut ON', handle)
    time.sleep(2)
    spectrum_analyzer.write('FREQ:CENT {}MHz'.format(center_frequency)) # set center frequency on spectrum
    spectrum_analyzer.write('FREQ:SPAN {}MHz'.format(span_sa)) # span
    time.sleep(1)
    spectrum_analyzer.write(':CALC:MARK1:STAT ON;:CALC:MARK1:MAX')
    time.sleep(1)
    spectrum_analyzer.write('CALC:MARK1:X?')
    time.sleep(1)
    resp = spectrum_analyzer.read()
    time.sleep(1)
    peak_max = float(resp) / 1e6
    # print("\tOutput frequency {} MHz".format(peak_max))
    spectrum_analyzer.write('CALC:MARK1:Y?')
    time.sleep(1)
    pow_m1 = spectrum_analyzer.read()
    #print(pow_m1)
    time.sleep(1)
    spectrum_analyzer.write(':CALC:MARK:PEAK:THR {}'.format(threshold))
    time.sleep(1)
    spectrum_analyzer.write(':CALCulate:MARKer1:PEAK:EXCursion 0')
    time.sleep(1)
    spectrum_analyzer.write(':CALC:MARK2:STAT ON;:CALC:MARK2:MAX')
    spectrum_analyzer.write(':CALCulate:MARKer2:MAXimum:RIGHt')
    spectrum_analyzer.write('CALC:MARK2:X?')
    time.sleep(1)
    # spectrum_analyzer.write(':CALC:FUNC SPU')
    # spectrum_analyzer.write(':INIT:IMM')
    # time.sleep(10)
    # spectrum_analyzer.write(':FETC:SPU:MAX?')
    resp = spectrum_analyzer.read()
    #print(resp)
    peak_right = float(resp) / 1e6
    spectrum_analyzer.write('CALC:MARK2:Y?')
    time.sleep(1)
    pow_m2 = spectrum_analyzer.read()
    print('Right peak {} dBm'.format(pow_m2))
    try:
        if peak_right == peak_max or float(pow_m2) < error_limit:
            spectrum_analyzer.write(':CALC:MARK3:STAT ON;:CALC:MARK3:MAX')
            spectrum_analyzer.write(':CALCulate:MARKer3:MAXimum:LEFT')
            spectrum_analyzer.write('CALC:MARK3:X?')
            time.sleep(1)
            resp = spectrum_analyzer.read()
            peak_left = float(resp) / 1e6
            spectrum_analyzer.write('CALC:MARK3:Y?')
            time.sleep(1)
            pow_m3 = spectrum_analyzer.read()
            print('Left peak {} dBm'.format(pow_m2))
            if peak_left == peak_max or float(pow_m3) < error_limit:
                output[i] = peak_max
                output_status_list.append("pass")
                print("TEST pass for frequency {}MHz".format(output[i]))
            else:
                test_success =False
                output_status_list.append("Fail")
                print("Test fail for frequency {}MHz".format(center_frequency))
        else:
            test_success = False
            output_status_list.append("Fail")
            print("Test fail for frequency {}MHz".format(center_frequency))
    except ImportError:
        output_status_list.append("Fail")
        print('Error')
    table_i = table_i + 1
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
data = list(zip(serial_no,input_list,error_limit,output_list,output_status_list))
# Creating the table
table = tabulate(data, headers=["Test step","Output frequency","Error Limits (in dBc)","Max Spurious","PASS/FAIL"], tablefmt="grid")
# Displaying the table
print(table)
# Writing the table to a text file
with open("Spurious mext to carrier test report.txt", "w") as f:
    f.write(table)

print("Table has been written to table.txt")