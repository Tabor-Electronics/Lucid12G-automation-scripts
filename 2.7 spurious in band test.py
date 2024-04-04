'''
Test - 2.7 Spurious in band carrier 
Test description- This test verifies, there is no spurious present in-band (between start and stop frequency ie span ) of the carrier above the defined error limit
Equipment required - 
Lucid device - LS1291D
Spectrum analyzer- Agilent Technologies, E4440A (PSA Series spectrum analyzer)
what is happening in thi script ?
 - After initializing the device, all the parameter are define in 2nd section,
 - start and stop frequency is selected +/-500  to the signal frequency
 - using 3 marker, the script is checking the peak, peak right and peak left, 
 - if all these marker values are same, then we conclude that there is not spurious above -60dBc in band to the carrier.
 -and if the marker value is not then we check if the power level of each marker to be above threshold, then we conclude the final results
-  A test report will be generated at the end of the script and is saved as a text file in the same directory '''''
import os
import sys
import time
import numpy as np
import ctypes
import _ctypes
import pyvisa as visa
from telucid_functions_v3 import connect
from telucid_functions_v3 import disconnect
from telucid_functions_v3 import sendScpi
from telucid_functions_v3 import connect_spectrum_via_lan

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
# Parameters
frequency_list =[1100]#np.arange(1000,12000,500)#list(np.arange(10,110,10))+list(np.arange(1100,20100,100))+list(np.arange(20000,40000,200)) # list of frequencies to be tested
res_BW = 30 # resolution bandwisth in KHz
# start_freq = 500
# stop_freq = 1500
output = np.zeros(len(frequency_list)) # To store the output frequency from spectrum analyzer (optional step)
power_in_dBm = 5.0 # power level required for the test in dBm
ref_level = power_in_dBm+5 # reference level on the spectrum must be 5dBm above the signal power level
error_limit = -60 # error limit in dBm
threshold = error_limit - power_in_dBm
## Test report parameters
################
# Parameters for test report
table_i=0
serial_no = np.zeros(len(frequency_list))
input_list_tb = np.zeros(len(frequency_list))
start_freq_tb = np.zeros(len(frequency_list))
stop_freq_tb = np.zeros(len(frequency_list))
output_list_tb= np.zeros(len(frequency_list))
output_status_tb= []# To store the output frequency from spectrum analyzer (optional step)
error_limit = -60+np.zeros(len(frequency_list)) # error limit in dBm
#######################################################################
#Main
spectrum_analyzer.write(':BWID:RES {}KHz'.format(res_BW))  # resolutrion bandwidth
for i in range(len(frequency_list)): # iterating over each frequency (main loop)
    center_frequency = frequency_list[i]
    serial_no[table_i] = table_i + 1
    input_list_tb[table_i] = center_frequency
    # if center_frequency>12000:
    #     continue
    # elif center_frequency<=10 and center_frequency<=1000:
    #     step_size = 10
    # elif center_frequency<=1100 and center_frequency<=8000:
    #     step_size= 100
    # elif center_frequency<= 8100 and center_frequency<=20000:
    #     step_size = 100
    # elif center_frequency<20100 and center_frequency<=40000:
    #     step_size=100
    # else:
    #     print('!!!FREQUENCY OUT OF RANGE!!!')
    #     continue
    # start_freq_tb[table_i]=start_freq+step_size
    # stop_freq_tb[table_i]=stop_freq+step_size
    start_freq_tb[table_i]=center_frequency-500
    stop_freq_tb[table_i]=center_frequency+500
    sendScpi(':FREQuency {}MHz'.format(center_frequency), handle)
    sendScpi(':POWer {}'.format(power_in_dBm), handle)
    sendScpi(':OUTPut ON', handle)
    spectrum_analyzer.write('DISP:WIND:TRAC:Y:RLEV 10 dbm')
    #resolution bw = 30 k
    spectrum_analyzer.write(':FREQ:STAR {}MHz'.format(start_freq_tb[table_i]))
    time.sleep(2)
    spectrum_analyzer.write(':FREQ:STOP {}MHz'.format(stop_freq_tb[table_i]))
    time.sleep(2)
    # spectrum_analyzer.write('[:SENSe]:SPURious[:RANGe][:LIST]:BANDwidth[:RESolution] 22KHz')
    # time.sleep(2)
    # spectrum_analyzer.write('[:SENSe]:SPURious[:RANGe][:LIST]:BWIDth|BANDwidth:VIDeo 400Hz')
    time.sleep(1)
    # spectrum_analyzer.write('[: SENSe]:SPURious[:RANGe][:LIST]: PEAK:THReshold -60')
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
    # print(pow_m1)
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
    # print(resp)
    peak_right = float(resp) / 1e6
    spectrum_analyzer.write('CALC:MARK2:Y?')
    time.sleep(1)
    pow_m2 = spectrum_analyzer.read()
    print('Right peak at {0}MHz power ={1} dBm'.format(peak_right,pow_m2))
    time.sleep(1)
    spectrum_analyzer.write(':CALC:MARK3:STAT ON;:CALC:MARK3:MAX')
    spectrum_analyzer.write(':CALCulate:MARKer3:MAXimum:RIGHt')
    spectrum_analyzer.write('CALC:MARK3:X?')
    time.sleep(1)
    # spectrum_analyzer.write(':CALC:FUNC SPU')
    # spectrum_analyzer.write(':INIT:IMM')
    # time.sleep(10)
    # spectrum_analyzer.write(':FETC:SPU:MAX?')
    resp = spectrum_analyzer.read()
    # print(resp)
    peak_left = float(resp) / 1e6
    spectrum_analyzer.write('CALC:MARK3:Y?')
    time.sleep(1)
    pow_m3 = spectrum_analyzer.read()
    print('Left peak at {0}MHz power ={1} dBm'.format(peak_left, pow_m3))
    if peak_max == peak_right == peak_left:
        output_status_tb.append("pass")
        print("Test pass")
    elif float(pow_m2) <= threshold and float(pow_m3) <= threshold:
        output_status_tb.append("pass")
        print("Test pass")
    else:
        output_status_tb.append("FAIL")
        test_success = False
        print("Test Fail")

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
data = list(zip(serial_no,input_list_tb,start_freq_tb,stop_freq_tb,error_limit,output_list_tb,output_status_tb))
# Creating the table
table = tabulate(data, headers=["Test step","Output frequency","Start frequency","Stop frequency","Error Limits (in dBc)","Max Spurious","PASS/FAIL"], tablefmt="grid")
# Displaying the table
print(table)
# Writing the table to a text file
with open("Spurious in-band test report.txt", "w") as f:
    f.write(table)

