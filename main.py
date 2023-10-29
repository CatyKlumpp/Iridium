# List of all global variables
global STD_TIMEOUT

# Test script for message transmission
import serial.tools.list_ports

# Import Functions
import Definiton.Functions

# PORT LISTING & SELECTION
ports = serial.tools.list_ports.comports()
usedPort = 'none'

for port in ports:
    print(f"Port: {port.device}, Description: {port.description}")
    usedPort = str(port.device)

if usedPort == 'none':
    print('No port is connected')
    exit(1)

STD_TIMEOUT = 1  # defines the default value for the standard read-back timeout
ser = serial.Serial(port=usedPort, baudrate=19200, timeout=STD_TIMEOUT)
print('Port used:', ser.port)


# ------Start of TRANSMISSION TEST-------- #
response = Definiton.Functions.serial_com('', ser)  # checking transceiver responsiveness
response = 'nodata'
if response == 'OK':
    print('Transceiver is responsive \n')
else:
    if response == 'nodata':
        print('No response')
        Definiton.Functions.no_answer('', ser, STD_TIMEOUT, readtime=5)
    else:
        if response == 'ERROR':
            print('Command couldnt be read')
            Definiton.Functions.read_error_init('', ser)
        else:
            if response != 'OK':
                print('\n Unexpected behaviour (faulty)\nSystem termination')
                exit(1)

print('Transceiver is responsive \n')

response = Definiton.Functions.serial_com('&K0',ser)  # Disabling flow control
if response == 'OK':
    print('Flow control is deactivated \n')
else:
    if response == 'nodata':
        print('timeout')
    else:
        print('error')
        exit(1)

response = Definiton.Functions.serial_com('+SBDMTA=0',ser)  # Disabling ring alert
if response == 'OK':
    print('Ring alert is deactivated \n')
else:
    if response == 'nodata':
        print('timeout')
    else:
        print('error')
        exit(1)

print('Initiation of registration process, please stand by:')
Definiton.Functions.SBD_registration(ser)
ser.timeout = STD_TIMEOUT  # Reset of to default read-back timeout value

message = input("Please enter your message: ")
Definiton.Functions.send_message(message,ser)