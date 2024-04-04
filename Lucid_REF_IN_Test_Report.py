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

# Initialization
send_scpi_cmd('*CLS',handle)
send_scpi_cmd('*RST',handle)
send_scpi_cmd(':INST 1',handle)
send_scpi_cmd(':INST:ACT 1',handle)

frequency_list= [10e6,10e6,10e6,100e6,100e6,100e6]
power_list= [-5,0,10,-5,0,10]


serial_no_tb = np.zeros(len(frequency_list)*len(power_list))
sig_gen_freq_tb = np.zeros(len(frequency_list)*len(power_list))
sig_gen_power_tb = np.zeros(len(frequency_list)*len(power_list))
output_status_tb= []
table_i = 0

ideal_min_width = [425e-09,25.5e-09]
ideal_max_width = [575e-09,34.5e-09]
ideal_min_period = [0.95e-06,0.95e-07]
ideal_max_period = [1.05e-06,1.05e-07]
timebase_scale = [500e-09,20e-09]
timebase_position = [423.4E-9,423.4E-9]





for test in range(2):
    # Set the cw to 500Mhz and Powe 10 dbm
    send_scpi_cmd(':FREQuency {}'.format(frequency_list[table_i]),handle)
    send_scpi_cmd(':POWer 5',handle)

    send_scpi_cmd(':ROSC:SOUR EXT', handle)
    send_scpi_cmd(':ROSC:SOUR:FREQ {}'.format(frequency_list[table_i]), handle)

    scope.write(':CHANnel{}:PROBe 1.0'.format(1))
    scope.write(':CHANnel{}:SCALe 200E-3'.format(1))
    scope.write(':CHANnel{}:OFFSet 0.0'.format(1))
    scope.write(':TRIGger:MODE EDGE')
    scope.write(':TRIGger:EDGE:SOURce CHANnel{}'.format(3))
    time.sleep(2)
    scope.write(':TIMebase:SCALe {}'.format(timebase_scale[test]))
    scope.write(':TIMebase:POSition {}'.format(timebase_position[test]))


    send_scpi_cmd(':OUTPut ON', handle)



    print('Please set the external signal generator frequency {} and power {} dBm and press enter'.format(frequency_list[table_i],power_list[table_i]))
    input()
    scope.write('*CLS;:DISPlay:CGRade:LEVels ')
    scope.write('AUTOscale')
    time.sleep(2)
    scope.write(':CHANnel{}:SCALe 400E-3'.format(1))
    scope.write(':CHANnel{}:OFFSet 0.0'.format(1))
    scope.write(':CHANnel{}:SCALe 400E-3'.format(2))
    scope.write(':CHANnel{}:OFFSet 0.0'.format(2))

    send_scpi_cmd(':PHAS 0', handle)
    time.sleep(1)
    scope.write(':MEASure:PHASe CHANnel1,CHANnel2')
    time.sleep(2)
    scope.write(':MEASure:RESults?')
    result = scope.read()
    measured_phase = float(result.split(',')[1])
    print('Measured phase is {}'.format(measured_phase))

    if abs(measured_phase) < 0:
        send_scpi_cmd(':PHAS {}'.format(abs(measured_phase)), handle)
    else:
        send_scpi_cmd(':PHAS {}'.format(360 - abs(measured_phase)), handle)

    time.sleep(3)
    scope.write(':MEASure:PHASe CHANnel1,CHANnel2')
    time.sleep(2)
    scope.write(':MEASure:RESults?')
    result = scope.read()
    measured_phase = float(result.split(',')[1])
    print('Measured phase is {}'.format(measured_phase))

    if abs(measured_phase) < 5:
        print('Test Pass')
        print('Phase locked')
        print(table_i)
        output_status_tb.append("Pass")
    else:
        print('Test Fail')
        print('Phase not locked')
        print(table_i)
        output_status_tb.append("Fail")

    serial_no_tb[table_i] = table_i + 1
    sig_gen_freq_tb[table_i]= frequency_list[table_i]
    sig_gen_power_tb[table_i] = power_list[table_i]
    table_i = table_i + 1

    for in_siggenpow in range(2):
        print('Change the signal generator power to {} dBm and press enter'.format(power_list[in_siggenpow + 1]))
        input()
        scope.write(':MEASure:DELTatime:DEFine RISing,1,MIDDle,RISing,1,MIDDle')
        time.sleep(2)
        scope.write(':MEASure:DELTatime CHANnel1,CHANnel2')
        time.sleep(2)
        scope.write(':MEASure:RESults?')
        result = scope.read()
        measured_skew = float(result.split(',')[1])
        print('Measured skew is {}'.format(measured_skew))

        if measured_skew > -1.5e9 and measured_skew < 1.5e9:
            print('Test Pass for power level {} dBm'.format(power_list[in_siggenpow + 1]))
            output_status_tb.append("Pass")
        else:
            print('Test Fail for power level {} dBm'.format(power_list[in_siggenpow + 1]))
            output_status_tb.append("Fail")

        serial_no_tb[table_i] = table_i + 1
        sig_gen_freq_tb[table_i] = frequency_list[table_i]
        sig_gen_power_tb[table_i] = power_list[table_i]
        table_i = table_i + 1
    print('Test completed for frequency {}'.format(frequency_list[test]))
print('Test Completed')


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




