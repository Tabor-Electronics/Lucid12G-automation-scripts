# -------------------------------------------------
# Name:     Amplitude_modulation_Internal_Source_Test_reports.py
#
# Description:
#   This script shows the capability of Amplitude modulation of Lucid device.
#   We generate a modulating signal of 100KHz with 75% Depth amplitude.
#   We read the frequency of modulated wave.
#   if we consider 1% accuracy then we can say that test is pass if modulated signal frequency is between 99KHz and 101KHz.
#
#
# Hardware Requirement
#  1. Lucid LS1291P
#  2. Agilent MSOS9254A Oscilloscope
#

# Hardware Connection
#   Lucid RF Out ------> Scope Channel1
#
# -------------------------------------------------

import numpy as np
import pyvisa as visa
import socket
import time
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
def send_scpi_cmd(cmd,handle):
    try:
        resourceManager = visa.ResourceManager()
        session = resourceManager.open_resource(handle)

        # Need to define the termination string
        session.write_termination = '\n'
        session.read_termination = '\n'

        session.write(cmd)
        session.close()
    except Exception as e:
        print('[!] Exception: ' + str(e))
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

##########################################################################################################################

# --- MAIN ---

# Set the IP Address and port
handle = 'TCPIP0::192.90.70.22::10000::SOCKET'

# Parameters
freq = 1000
pwr_dBm = 5
channel_select = 1
threshold = 101

# Initialization
send_scpi_cmd('*RST',handle )
send_scpi_cmd('*IDN?',handle )
send_scpi_cmd(':INST 1',handle )
send_scpi_cmd(':INST:ACT 1',handle )

# Set the cw to 500Mhz and Powe 10 dbm
send_scpi_cmd(':FREQuency {0}MHz'.format(freq),handle )
send_scpi_cmd(':POWer {0}'.format(pwr_dBm),handle )


#AM modulation setting with Internal source
send_scpi_cmd(':AM:SOUR INT',handle )
send_scpi_cmd(':AM:INT:FREQ 100e3',handle )
send_scpi_cmd(':AM:DEPT 75',handle )
send_scpi_cmd(':AM ON',handle )


# Output on
send_scpi_cmd(':OUTPut ON',handle )

#####################################################################################################################3##

scope.write(':CHANnel{}:PROBe 1.0'.format(channel_select))
scope.write(':CHANnel{}:SCALe 100E-3'.format(channel_select))
scope.write(':TIMebase:SCALe 10E-6')
time.sleep(5)
scope.write(':STOP')
scope.write(':FUNCtion1:ADEMod CHANnel1')
scope.write(':FUNCtion1:DISPlay ON')
scope.write(':MEASure:FREQuency FUNCtion1'.format(channel_select))
time.sleep(2)
scope.write(':MEASure:RESults?')
result = scope.read()
measured_freq= float(result.split(',')[1])/1e3
print('Modulating frequency is {}'.format(measured_freq))


scope.write(':MEASure:VMIN FUNCtion1'.format(channel_select))
time.sleep(2)
scope.write(':MEASure:RESults?')
result = scope.read()
voltage_min= float(result.split(',')[1])
print('Minimum Voltage is {}'.format(voltage_min))


scope.write(':MEASure:VMAX FUNCtion1'.format(channel_select))
time.sleep(2)
scope.write(':MEASure:RESults?')
result = scope.read()
voltage_max= float(result.split(',')[1])
print('Maximum Voltage is {}'.format(voltage_max))

Mod_depth = (voltage_max-voltage_min)/(voltage_max+voltage_min)*100
print('Modulation depth in percentage is {} %'.format(Mod_depth))



serial_no_tb = np.zeros(2)
modulation_depth_tb = np.zeros(2)
modulating_frequency_tb = np.zeros(2)
output_status_tb= []
table_i = 0

for i in range(1):
    serial_no_tb[table_i] = table_i + 1
    modulation_depth_tb[table_i] = Mod_depth
    modulating_frequency_tb[table_i] = measured_freq

    if modulating_frequency_tb[table_i] < threshold:
        output_status_tb.append("pass")
        print("TEST is pass")
    else:
        test_success = False
        output_status_tb.append("fail")
        print("TEST is FAIL")

    table_i = table_i + 1
########################################################################################################################
# Test report
from tabulate import tabulate

# Sample data for the table
data = list(zip(serial_no_tb, modulation_depth_tb, modulating_frequency_tb,output_status_tb))
# Creating the table
table = tabulate(data,headers=["Test step", "Modulation Depth Reading", "Modulation Frequency Reading","PASS/FAIL"],
                 tablefmt="grid")
# Displaying the table
print(table)
# Writing the table to a text file
with open("Amplitude Modulation Internal Source test report.txt", "w") as f:
    f.write(table)

print("Table has been written to table.txt")



print('Test Run successfully')



















# test_success = True
# serial_no = [1]
# carrier_frequency = [1]
# pwr_dBm = 5
#
# modulating_freq = [0.1]
# peak = np.zeros(len(carrier_frequency))
# right_peak = np.zeros(len(carrier_frequency))
# left_peak = np.zeros(len(carrier_frequency))
# output_status = []
#
# # Set the IP Address and port
# handle = 'TCPIP0::192.90.70.22::10000::SOCKET'
#
# # Initialization
# send_scpi_cmd('*RST',handle )
# send_scpi_cmd('*IDN?',handle )
# send_scpi_cmd(':INST 1',handle )
# send_scpi_cmd(':INST:ACT 1',handle )
# spectrum_analyzer = connect_spectrum_via_lan()
# spectrum_analyzer.write(':INIT:REST')
# print('Initialized')
# ref_level = 10
# spectrum_analyzer.write('DISP:WIND:TRAC:Y:RLEV {} dbm'.format(ref_level))
# time.sleep(2)
# for freq in carrier_frequency:
# # Set the cw to 500Mhz and Powe 10 dbm
#     send_scpi_cmd(':FREQuency {0}MHz'.format(freq),handle )
#     send_scpi_cmd(':POWer {0}'.format(pwr_dBm),handle )
#
#     # # FM modulation setting with External source
#     send_scpi_cmd( ':AM:SOUR EXT',handle )
#     send_scpi_cmd( ':AM ON',handle )
#     # Output on
#     send_scpi_cmd(':OUTPut ON',handle )
#
#     res_BW = 500
#     center_frequency = freq
#     span_sa = 500
#     spectrum_analyzer.write(':BWID:RES {}Hz'.format(res_BW))  # resolutrion bandwidth
#     time.sleep(2)
#     spectrum_analyzer.write('FREQ:CENT {}MHz'.format(center_frequency))
#     time.sleep(2)
#     spectrum_analyzer.write('FREQ:SPAN {}KHz'.format(span_sa))
#     spectrum_analyzer.write(':CALC:MARK1:STAT ON;:CALC:MARK1:MAX')
#     time.sleep(1)
#     spectrum_analyzer.write('CALC:MARK1:X?')
#     time.sleep(1)
#     resp = spectrum_analyzer.read()
#     time.sleep(1)
#     peak_max = float(resp) / 1e6
#     print("\tOutput frequency {} MHz".format(peak_max))
#     if peak_max == freq:
#         center_frequency1 = center_frequency+modulating_freq
#         spectrum_analyzer.write('FREQ:CENT {}MHz'.format(center_frequency1))
#         time.sleep(2)
#         spectrum_analyzer.write('FREQ:SPAN {}KHz'.format(span_sa))
#         spectrum_analyzer.write(':CALC:MARK1:STAT ON;:CALC:MARK1:MAX')
#         time.sleep(1)
#         spectrum_analyzer.write('CALC:MARK1:X?')
#         time.sleep(1)
#         resp = spectrum_analyzer.read()
#         time.sleep(1)
#         peak_max2 = float(resp) / 1e6
#         print("\tOutput frequency {} MHz".format(peak_max2))
#         if peak_max2 == freq:
#             center_frequency2 = center_frequency - modulating_freq
#             spectrum_analyzer.write('FREQ:CENT {}MHz'.format(center_frequency2))
#             time.sleep(2)
#             spectrum_analyzer.write('FREQ:SPAN {}KHz'.format(span_sa))
#             spectrum_analyzer.write(':CALC:MARK1:STAT ON;:CALC:MARK1:MAX')
#             time.sleep(1)
#             spectrum_analyzer.write('CALC:MARK1:X?')
#             time.sleep(1)
#             resp = spectrum_analyzer.read()
#             time.sleep(1)
#             peak_max3 = float(resp) / 1e6
#             print("\tOutput frequency {} MHz".format(peak_max3))
#
#     if test_success:
#         output_status.append("fail")
#         print("Test successed!")
#     else:
#         test_success = False
#         output_status.append("fail")
#         print("Test failed ")
# # disconnecting the instruments
# spectrum_analyzer.close()
# # disconnect(handle)
# ##########################################
# ##########################################
# #Test report
# from tabulate import tabulate
# # Sample data for the table
# data = list(zip(serial_no,carrier_frequency,pwr_dBm,modulating_freq,peak,right_peak,left_peak,output_status))
# # Creating the table
# table = tabulate(data, headers=["Test step","Output frequency","Power","Modulating Frequency","Carrier frequency","Right side ","Left side","PASS/FAIL"], tablefmt="grid")
# # Displaying the table
# print(table)
# # Writing the table to a text file
# with open("Spurious in-band test report.txt", "w") as f:
#     f.write(table)
#
#






# # FM modulation setting with Internal source
# send_scpi_cmd(lucid_device, ':AM:SOUR INT')
# send_scpi_cmd(lucid_device, ':AM:INT:FREQ  20e3')
# send_scpi_cmd(lucid_device, ':AM:DEPT 50')
# send_scpi_cmd(lucid_device, ':AM ON')



