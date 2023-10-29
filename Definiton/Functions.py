
import time

# Variable Definition
usedPort = ''
response = ''

# Functions
def timer(seconds):  # Just a wait timer
    while seconds > 0:
        time.sleep(1)
        seconds -= 1


def calculate_checksum(string):
    checksum = 0
    for char in string:
        checksum += ord(char)
        checksum = checksum % (2 ** 16)  # Limits size of checksum to 2 bytes (least significant ones)
    return checksum


def reg_split(response):
    registrationResponse = response.split(':')
    statusCodes = registrationResponse[1].split(',')
    return int(statusCodes[0]), int(statusCodes[1])


def data_reception(port):
    binaryMessage = read_all(port)
    # print(binaryMessage)
    decodedMessage = binaryMessage.decode()  # decodes binary message into char string
    # decodedMessage=str(binaryMessage,"UTF-8") #alternativ

    if len(decodedMessage) != 0:
        #    decodedMessage = decodedMessage.strip()  # .strip() entfernt die zusätzlichen Leerstellen
        answer = decodedMessage.split()  # split() splits answer at linebreak
        print(answer)
        recievedValue = answer[1]  # this is probably not the best way to do this, need to find a better alternative
    #    print('Number of bytes transfered:', len(recievedValue))
    else:
        recievedValue = 'nodata'
    return recievedValue


def read_all(port, chunk_size=20):
    read_buffer = b''

    while True:
        # Read in chunks. Each chunk will wait as long as specified by
        # timeout. Increase chunk_size to fail quicker
        byte_chunk = port.read(size=chunk_size)
        read_buffer += byte_chunk
        if not len(byte_chunk) == chunk_size:
            break
    return read_buffer


def serial_com(cmdstring,ser):
    ser.write(('AT' + cmdstring + '\r').encode())  # sends AT command to transceiver
    cmdresponse = data_reception(ser)  # gets transceiver response
    return cmdresponse


def read_error_init(cmdstring,ser):  # handling of 'ERROR' readback during the inital startup phase
    print('Transmission retry #1 of:', ('AT' + cmdstring), '\n')
    response = serial_com(cmdstring, ser)
    if response == 'OK':
        return None
    if response == 'ERROR':
        print('Command couldnt be read')
        timer(5)
        print('Transmission retry #2 of:', ('AT' + cmdstring), '\n')
        response2 = serial_com(cmdstring, ser)
        if response2 == 'OK':
            return None
        if response2 == 'ERROR' or 'nodata':
            print('Transceiver is faulty: erroneous replies')
            exit(1)
    if response == 'nodata':
        print('No response\n Communication with transceiver not possible')
        exit(1)


def no_answer(cmdstring, ser, STD_TIMEOUT, readtime):
    print('\nTransmission retry #1 of:', ('AT' + cmdstring))
    ser.timeout = readtime  # Sets serial timeout
    response = serial_com(cmdstring,ser)
    if response == 'OK':
        ser.timeout = STD_TIMEOUT  # Reset of to default readback timeout value
        return None
    else:
        print('Transceiver is irresponsive')
        exit(1)


def SBD_registration(ser):
    ser.timeout = 15  # Sets serial timeout to account for longer processing time
    response = serial_com('+SBDREG',ser)  # Commands SBD Iridium network registration
    statusCode, errorCode = reg_split(response)
    if statusCode == 2:
        print('Transceiver is registered for SBD communications with the gateway')
    if statusCode == 3:
        print('Transceiver registration denied')
    if statusCode == 1:
        print('Transceiver not registered')
    return None


def send_message(message,ser):
    reponse = serial_com('+SBDWT=' + message, ser)
    if response == 'OK':
        print('Message transfer to buffer successful')  #
    else:
        print('failure')