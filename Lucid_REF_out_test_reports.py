# -------------------------------------------------
# Name:     Lucid Reference Out Test_reports.py
#
# Description:
#   This script shows the capability of Reference OUT of Lucid device.
#   In this test we compare the  REF OUT frequency and Output frequency.
#   We can not use Lucid LS1291P as REF OUT is not available in Lucid LS1291P.
#
#
#
# Hardware Requirement
#  1. Agilent MSOS9254A Oscilloscope
#  2. Lucid LS1291D
#
#
# Hardware Connection
#   Lucid LS1291D RF Out ------> Channel 2 of Oscilloscope
#   Lucid LS1291D 10MHz REF Out (Change as per test need) ------> Channel 1 of Oscilloscope
#

# -------------------------------------------------



import pyvisa as visa
import socket
import time
from tabulate import tabulate
import numpy as np
import os
import sys
import ctypes
import _ctypes

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


def send_scpi_cmd(command, hLib):
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
    send_scpi_cmd = SendScpiProto(("SendScpi", hLib), SendScpiParams)

    answer = ctypes.create_string_buffer(1024)
    cmd = ctypes.create_string_buffer(bytes(command, 'utf-8'))
    nchars = ctypes.c_int(64)

    rv = send_scpi_cmd(cmd, answer, nchars)
    if (rv <= -1):
        print("error")


def disconnect(hLib):
    if(hLib == None):
        return
    # Unload the DLL so that it can be rebuilt
    libHandle = hLib._handle
    _ctypes.FreeLibrary(libHandle)
    del hLib


handle = connect()

########################################################################################################################
scope_addr = 'TCPIP0::K-MSO9254-90134.local::inst0::INSTR' # connect to scope via USB
try:
    resourceManager = visa.ResourceManager()  # Create a connection (session) to the instrument
    #scope = resourceManager.get_instrument(scope_addr2)
    #scope.write('*CLS;:DISPlay:CGRade:LEVels ')
    scope = resourceManager.open_resource(scope_addr)
    print(scope)
    ## scope acquisition
    # Send *IDN? and read the response
    scope.write('*RST')
    scope.write('*IDN?')
    idn = scope.read()
    print('*IDN? returned: %s' % idn.rstrip('\n'))
except Error as ex2:
    print('Couldn\'t connect to \'%s\', exiting now...' % scope_addr)
    sys.exit()

scope.write('AUTOscale')
time.sleep(2)
scope.write('*OPC')
scope.write(':MEASure:CLEar')
scope.write('*CLS;:DISPlay:CGRade:LEVels ')
##############################################################################################################################################

# Initialization
send_scpi_cmd('*CLS',handle)
send_scpi_cmd('*RST',handle)
send_scpi_cmd(':INST 1',handle)
send_scpi_cmd(':INST:ACT 1',handle)



###################################################################################################################################################

scope.write(':CHANnel{}:PROBe 1.0'.format(1))
scope.write(':CHANnel{}:SCALe 500E-3'.format(1))
scope.write(':CHANnel{}:SCALe 500E-3'.format(2))
scope.write(':CHANnel{}:OFFSet 0.0'.format(1))
scope.write(':CHANnel{}:OFFSet 0.0'.format(2))
scope.write(':TRIGger:MODE EDGE')
scope.write(':TRIGger:EDGE:SOURce CHANnel{}'.format(3))
time.sleep(2)


serial_no_tb = np.zeros(2)
REF_Out_freq_tb = np.zeros(2)
RF_output_freq_tb = np.zeros(2)
output_status_tb= []
table_i = 0

REF_Out_freq_tb = [10e6,100e6]
ideal_min_freq = [9.85,98.5]
ideal_max_freq = [10.15,101.5]
timebase_scale = [100e-09,10e-09]
timebase_position = [0,423.4E-9]


for test in range(2):
    # FM modulation setting with Internal source
    send_scpi_cmd(':ROSC:SOUR INT', handle)
    send_scpi_cmd(':FREQuency {}'.format(REF_Out_freq_tb[test]), handle)
    send_scpi_cmd(':POWer 5', handle)
    send_scpi_cmd(':OUTPut ON', handle)
    print('Parameters set for signal with REF output frequency {0} and press enter to continue test'.format(REF_Out_freq_tb[test]))
    input()
    scope.write(':TIMebase:SCALe {}'.format(timebase_scale[test]))
    scope.write(':TIMebase:POSition {}'.format(timebase_position[test]))
    time.sleep(2)
    scope.write(':MEASure:FREQuency CHANnel2')
    time.sleep(2)
    scope.write(':MEASure:RESults?')
    result = scope.read()
    measured_freq = float(result.split(',')[1])/1e6
    print(measured_freq)
    RF_output_freq_tb[test] = measured_freq*1e6

    if ideal_min_freq[test] <= measured_freq <= ideal_max_freq[test]:
            output_status_tb.append('Pass')
            print('Test Pass ')
    else:
        output_status_tb.append('Fail')
        print('Test Fail ')

    serial_no_tb[table_i] = table_i + 1
    table_i = table_i + 1



########################################################################################################################

# Sample data for the table
data = list(zip(serial_no_tb, REF_Out_freq_tb,RF_output_freq_tb, output_status_tb))

# Creating the table
table = tabulate(data, headers=["Test step", "Ref Out Frequency", "Output Frequency", "PASS/FAIL"], tablefmt="grid")

# Displaying the table
print(table)

# Writing the table to a text file
with open("Lucid REF Out Test report.txt", "w") as f:
    f.write(table)

print("Table has been written to Reference Output test report.txt")

print('Test Run successfully')

