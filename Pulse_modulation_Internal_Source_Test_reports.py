# -------------------------------------------------
# Name:     Pulse_modulation_Internal_Source_Test_reports.py
#
# Test Description:
#   This script shows the capability of Pulse modulation of Lucid device.
#   We select the internal source of Lucid to generate a modulating signal of 1MHz and 10MHz with pulse width of 500 nanosec and 30 nanosec.
#   We measure the Pulse duration by reading burst width from Oscilloscope.
#   For 1 MHz, it should be within range of 425 nsec to 575 nsec.
#   For 10 MHz, it should be within range of 25.5 nsec to 34.5 nsec.
#   We measure the Pulse repetition by reading burst period from Oscilloscope.
#   For 1 MHz, it should be within range of 0.95*10e-06 sec to 1.05*10e-06 sec.
#   For 10 MHz, it should be within range of 0.95*10e-07 sec to 1.05*10e-07 sec.
#
# Hardware Requirement
# 1. Lucid LS1291P
# 2. Agilent MSOS9254A Oscilloscope
#
#
# Hardware Connection
#   Lucid RF Out ------> Scope Channel1

########################################################################################################################
import pyvisa as visa
import socket
import time
from tabulate import tabulate
import numpy as np


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


# Set the IP Address and port
handle = 'TCPIP0::192.90.70.22::10000::SOCKET'

########################################################################################################################

# Scope Connection and initialization
scope_addr = 'USB0::0x2A8D::0x900E::MY55490134::INSTR' # connect to scope via USB
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

# Lucid Initialization and setup

# Initialization
send_scpi_cmd('*CLS',handle)
send_scpi_cmd('*RST',handle)
send_scpi_cmd(':INST 1',handle)
send_scpi_cmd(':INST:ACT 1',handle)

# Set the Lucid parameters
send_scpi_cmd(':FREQuency 1000000000',handle)
send_scpi_cmd(':POWer 5',handle)

###################################################################################################################################################

# Set scope parameter
scope.write(':CHANnel{}:PROBe 1.0'.format(1))
scope.write(':CHANnel{}:SCALe 200E-3'.format(1))
scope.write(':CHANnel{}:OFFSet 0.0'.format(1))
scope.write(':TRIGger:MODE EDGE')
scope.write(':TRIGger:EDGE:SOURce CHANnel{}'.format(1))
time.sleep(2)

########################################################################################################################

# Set testing and table parameters
serial_no_tb = np.zeros(2)
pulse_width_tb = np.zeros(2)
pulse_repetition_tb = np.zeros(2)
pulse_duration_reading_tb = np.zeros(2)
pulse_repetition_reading_tb = np.zeros(2)
output_status_tb= []
table_i = 0

freq = [1e6,10e6]
width = [500e-9,30e-9]
ideal_min_width = [425e-09,25.5e-09]
ideal_max_width = [575e-09,34.5e-09]
ideal_min_period = [0.95e-06,0.95e-07]
ideal_max_period = [1.05e-06,1.05e-07]
timebase_scale = [500e-09,50e-09]
timebase_position = [423.4E-9,423.4E-9]

########################################################################################################################

print('Test start for Pulse Modulation Internal Source')
for test in range(2):
    scope.write('AUTOscale')
    time.sleep(2)
    # FM modulation setting with Internal source
    send_scpi_cmd(':PULS:SOUR INT', handle)
    send_scpi_cmd(':PULS:FREQ {}'.format(freq[test]), handle)
    pulse_repetition_tb[test] = freq[test]
    send_scpi_cmd(':PULS:WIDT {}'.format(width[test]), handle)
    pulse_width_tb[test] = width[test]
    send_scpi_cmd(':PULS ON', handle)
    send_scpi_cmd(':OUTPut ON', handle)
    print('Parameters set for square wave signal with Pulse Repetition frequency {0} and Pulse Width {1} and press enter to continue test'.format(freq[test],width[test]))
    input()

    scope.write(':TIMebase:SCALe {}'.format(timebase_scale[test]))
    scope.write(':TIMebase:POSition {}'.format(timebase_position[test]))
    time.sleep(2)
    scope.write(':STOP')
    scope.write(':MEASure:BPERiod CHANnel{},1e-9'.format(1))
    time.sleep(3)
    scope.write(':MEASure:RESults?')
    result1 = scope.read()
    # print(result1)
    BURST_PERIOD = float(result1.split(',')[1])
    pulse_repetition_reading_tb[test]=BURST_PERIOD
    # print(BURST_PERIOD)


    scope.write(':MEASure:BWIDth CHANnel{},1e-9'.format(1))
    time.sleep(3)
    scope.write(':MEASure:RESults?')
    result2 = scope.read()
    # print(result2)
    BURST_WIDTH = float(result2.split(',')[1])
    pulse_duration_reading_tb[test] = BURST_WIDTH
    # print(BURST_WIDTH)

    if ideal_min_width[test] <= BURST_WIDTH <= ideal_max_width[test]:
        if ideal_min_period[test] <= BURST_PERIOD <= ideal_max_period[test]:
            output_status_tb.append('Pass')
            print('Test Pass successfull')
        else:
            output_status_tb.append('Fail')
            print('Test Fail due to burst period ')
    else:
        output_status_tb.append('Fail')
        print('Test Fail due to burst width')
    serial_no_tb[table_i] = table_i + 1
    table_i = table_i + 1

########################################################################################################################

# Sample data for the table
data = list(zip(serial_no_tb, pulse_width_tb, pulse_repetition_tb, pulse_duration_reading_tb, pulse_repetition_reading_tb, output_status_tb))

# Creating the table
table = tabulate(data, headers=["Test step", "Pulse Width", "Pulse Repetition", "Pulse Duration Reading", "Pulse Repetition Reading", "PASS/FAIL"], tablefmt="grid")

# Displaying the table
print(table)

# Writing the table to a text file
with open("Pulse Modulation internal source test report.txt", "w") as f:
    f.write(table)

print("Table has been written to Pulse Modulation internal source test report.txt")

print('Test Run successfully')

########################################################################################################################