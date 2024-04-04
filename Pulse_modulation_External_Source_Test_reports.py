# -------------------------------------------------
# Name:     Pulse_modulation_External_Source_Test_reports.py
#
# Description:
#   This script shows the capability of Pulse modulation of Lucid device.
#   We select the External signal generator source to generate a modulating signal of 1MHz and 10MHz with 50% and 30%
#   duty cycle consequtively.
#   We measure the Pulse duration by reading burst width from Oscilloscope.
#   For 1 MHz, it should be within range of 425 nsec to 575 nsec.
#   For 10 MHz, it should be within range of 25.5 nsec to 34.5 nsec.
#   We measure the Pulse repetition by reading burst period from Oscilloscope.
#   For 1 MHz, it should be within range of 0.95*10e-06 sec to 1.05*10e-06 sec.
#   For 10 MHz, it should be within range of 0.95*10e-07 sec to 1.05*10e-07 sec.
#
# Hardware Requirement
#  1. Lucid LS1291P
#  2. Agilent MSOS9254A Oscilloscope
#  3. 100MS/S Waveform Generator

# Hardware Connection
#   Lucid RF Out ------> Scope Channel1
#   Lucid TRIG IN -----> External signal generator output
# -------------------------------------------------

import pyvisa as visa
import socket
import time
import numpy as np
from tabulate import tabulate

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
# Scope Connection
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


# Set the cw to 500Mhz and Powe 10 dbm
send_scpi_cmd(':FREQuency 1000000000',handle)
send_scpi_cmd(':POWer 5',handle)


###################################################################################################################################################

scope.write(':CHANnel{}:PROBe 1.0'.format(1))
scope.write(':CHANnel{}:SCALe 200E-3'.format(1))
scope.write(':CHANnel{}:OFFSet 0.0'.format(1))
scope.write(':TRIGger:MODE EDGE')
scope.write(':TRIGger:EDGE:SOURce CHANnel{}'.format(1))
time.sleep(2)


serial_no_tb = np.zeros(2)
# pulse_width_tb = np.zeros(2)
Fun_gen_duty_cycle_tb = np.zeros(2)
# pulse_repetition_tb = np.zeros(2)
Fun_gen_freq_tb = np.zeros(2)
pulse_duration_reading_tb = np.zeros(2)
pulse_repetition_reading_tb = np.zeros(2)
output_status_tb= []
table_i = 0

Fun_gen_freq_tb = [1e6,10e6]
Fun_gen_duty_cycle_tb = [50,30]
ideal_min_width = [425e-09,25.5e-09]
ideal_max_width = [575e-09,34.5e-09]
ideal_min_period = [0.95e-06,0.95e-07]
ideal_max_period = [1.05e-06,1.05e-07]
timebase_scale = [500e-09,50e-09]
timebase_position = [423.4E-9,423.4E-9]


for test in range(2):
    scope.write('AUTOscale')
    # Pulse modulation setting with External source
    send_scpi_cmd(':PULS:SOUR EXT', handle)
    send_scpi_cmd(':PULS ON', handle)
    send_scpi_cmd(':OUTPut ON', handle)
    print('Parameters set for square wave signal with frequency {0} and {1}% Duty cycle and press enter to continue test'.format(Fun_gen_freq_tb[test],Fun_gen_duty_cycle_tb[test]))
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
            print('Test1 Pass')
        else:
            output_status_tb.append('Fail')
            print('Test Fail due to burst period')
    else:
        output_status_tb.append('Fail')
        print('Test Fail due to burst width')
    serial_no_tb[table_i] = table_i + 1
    table_i = table_i + 1


########################################################################################################################


# Sample data for the table
data = list(zip(serial_no_tb,Fun_gen_duty_cycle_tb, Fun_gen_freq_tb,  pulse_duration_reading_tb, pulse_repetition_reading_tb, output_status_tb))

# Creating the table
table = tabulate(data, headers=["Test step", "Function Generator Duty Cycle", "Function Generator Frequency", "Pulse Duration Reading", "Pulse Repetition Reading", "PASS/FAIL"], tablefmt="grid")

# Displaying the table
print(table)

# Writing the table to a text file
with open("Pulse Modulation External Source test report.txt", "w") as f:
    f.write(table)

print("Table has been written to Pulse Modulation External Source test report.txt")

print('Test Run successfully')

########################################################################################################################
