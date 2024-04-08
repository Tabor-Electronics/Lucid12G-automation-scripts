# -------------------------------------------------
# Name:     Lucid Reference in Test_reports.py
#
# Description:
#   This script shows the capability of Reference IN of Lucid device.
#   We select the External signal generator source(Lucid LS1291D) to generate a modulating signal of 10MHz and 100MHz
#   with -5dBm, 0dBm and 10 dBm power consequtively.
#   RF Output of External signal generator sourcec is connected to REF IN input Lucid LS1291P to make phase lock of
#   both signal generator.
#   From Lucid LS1291P, we generate signal of 10MHz and 100 MHz which is to be compared with 10 and 100 MHz REF OUT of
#   External signal generator source(Lucid LS1291D).
#   Skew from both the channels, measured on oscilloscope.
#   For the same setup only power from External signal generator source(Lucid LS1291D) is changed(-5dBm,0dBm,10dBm)
#   and skew should be in range of +1.5nsec and -1.5 nsec.
#
#
#
# Hardware Requirement
#  1. Lucid LS1291P
#  2. Agilent MSOS9254A Oscilloscope
#  3. Lucid LS1291D

# Hardware Connection
#   Lucid LS1291D RF Out ------> Lucid LS1291P 10/100 MHz REF IN
#   Lucid LS1291D 10MHz REF Out (Change as per test need) ------> Channel 2 of Oscilloscope
#   Lucid LS1291D RF Out ------> Channel 1 of Oscilloscope

# -------------------------------------------------



import pyvisa as visa
import socket
import time
from tabulate import tabulate
import numpy as np
import sys


def send_scpi_cmd(cmd,dev):
    try:
        resourceManager = visa.ResourceManager()
        session = resourceManager.open_resource(dev)

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

# --- MAIN ---

# Set the IP Address and port
handle = 'TCPIP0::192.90.70.22::10000::SOCKET'

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



frequency_list= [10e6,10e6,10e6,100e6,100e6,100e6]
power_list= [-5,0,10,-5,0,10]
measured_skew= []

serial_no_tb = np.zeros(len(frequency_list)*len(power_list))
sig_gen_freq_tb = np.zeros(len(frequency_list)*len(power_list))
sig_gen_power_tb = np.zeros(len(frequency_list)*len(power_list))
output_status_tb= []
table_i = 0

timebase_scale = [50e-09,50e-09,50e-09,10e-09,10e-09,10e-09]
timebase_position = [0,0,0,0,0,0]
channel1_scale = [300e-03,300e-03,300e-03,300e-03,300e-03,300e-03]
channel2_scale = [100e-03,200e-03,500e-03,100e-03,200e-03,500e-03]
test = 0


sig_gen_freq_tb = list(frequency_list)
sig_gen_power_tb = list(power_list)


for test1 in range(0,6,3):

    # Initialization
    send_scpi_cmd('*CLS', handle)
    send_scpi_cmd('*RST', handle)
    send_scpi_cmd(':INST 1', handle)
    send_scpi_cmd(':INST:ACT 1', handle)

    # Set the cw to 500Mhz and Powe 10 dbm
    send_scpi_cmd(':FREQuency {}'.format(frequency_list[test1]),handle)
    print('Selected frequency is {}'.format(frequency_list[test1]))
    send_scpi_cmd(':POWer 5',handle)

    send_scpi_cmd(':ROSC:SOUR EXT', handle)
    send_scpi_cmd(':ROSC:SOUR:FREQ {}'.format(frequency_list[test1]), handle)

    send_scpi_cmd(':OUTPut ON', handle)
    print('Please set the external signal generator frequency {} and power {} dBm and press enter'.format(frequency_list[test1],power_list[table_i]))
    input()
    # scope.write('*CLS;:DISPlay:CGRade:LEVels ')
    scope.write('AUTOscale')
    time.sleep(2)
    scope.write(':CHANnel{0}:SCALe {1}'.format(1,channel1_scale[test1]))
    scope.write(':CHANnel{}:OFFSet 0.0'.format(1))
    scope.write(':CHANnel{0}:SCALe {1}'.format(2,channel2_scale[test1]))
    scope.write(':CHANnel{}:OFFSet 0.0'.format(2))
    scope.write(':TIMebase:SCALe {}'.format(timebase_scale[test1]))
    scope.write(':TIMebase:POSition {}'.format(timebase_position[test1]))
    scope.write(':TRIGger:MODE EDGE')
    scope.write(':TRIGger:EDGE:SOURce CHANnel{}'.format(1))

    time.sleep(2)

    scope.write(':CHANnel1:ISIM:BWLimit:WALL')
    scope.write(':CHANnel1:ISIM:BWLimit ON')
    scope.write(':CHANnel1:ISIM:BANDwidth 200e6')

    scope.write(':CHANnel2:ISIM:BWLimit:WALL')
    scope.write(':CHANnel2:ISIM:BWLimit ON')
    scope.write(':CHANnel2:ISIM:BANDwidth 200e6')



    scope.write(':MEASure:DELTatime:DEFine RISing,1,MIDDle,RISing,1,MIDDle')
    time.sleep(2)
    scope.write(':MEASure:DELTatime CHANnel1,CHANnel2')
    time.sleep(2)
    scope.write(':MEASure:RESults?')
    result = scope.read()
    measured_skew_val = float(result.split(',')[1])
    print('Measured skew is {}'.format(measured_skew_val))


    serial_no_tb[table_i] = table_i + 1
    table_i = table_i + 1
    measured_skew.append(measured_skew_val)
    initial_skew = measured_skew_val
    output_status_tb.append("Pass")


    for test in range(2):
        print('Please set the external signal generator frequency {} and power {} dBm and press enter'.format(
            frequency_list[test+test1+1], power_list[test+test1+1]))
        input()
        scope.write('*CLS;:DISPlay:CGRade:LEVels ')
        time.sleep(2)
        scope.write(':CHANnel{0}:SCALe {1}'.format(2, channel2_scale[test+test1+1]))
        scope.write(':CHANnel{}:OFFSet 0.0'.format(2))
        time.sleep(1)
        scope.write(':MEASure:DELTatime:DEFine RISing,1,MIDDle,RISing,1,MIDDle')
        time.sleep(2)
        scope.write(':MEASure:DELTatime CHANnel1,CHANnel2')
        time.sleep(2)
        scope.write(':MEASure:RESults?')
        result = scope.read()
        measured_skew_val = float(result.split(',')[1])
        print('Measured skew is {}'.format(measured_skew_val))
        serial_no_tb[table_i] = table_i +1
        measured_skew.append(measured_skew_val)

        tested_skew = abs(measured_skew[test+test1+1]) - abs(initial_skew)
        if tested_skew > -1.5e-09 and tested_skew < 1.5e-09:
            print('Test Pass')
            output_status_tb.append("Pass")
        else:
            print('Test Fail')
            output_status_tb.append("Fail")

        table_i = table_i + 1

###################################################################################################################################################


# Sample data for the table
data = list(zip(serial_no_tb, sig_gen_freq_tb, sig_gen_power_tb, output_status_tb))

# Creating the table
table = tabulate(data, headers=["Test step", "Signal Generator Frequency", "Signal Generator Power", "PASS/FAIL"], tablefmt="grid")

# Displaying the table
print(table)

# Writing the table to a text file
with open("Lucid_REF_IN_Test_Report.txt", "w") as f:
    f.write(table)

print("Table has been written to Reference Internal source test report.txt")

print('Test Run successfully')




