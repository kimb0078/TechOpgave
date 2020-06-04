import socket
from threading import Timer

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('127.0.0.1', 1234)
hostname = socket.gethostname()

client_ip = socket.gethostbyname(hostname)
config = open('opt.conf')
line = config.readline()
count = 1

while line:

    if count == 1:
        line = line.strip()
        KeepAlive = str(line.split(':')[1])

    if count == 2:
        line = line.strip()
        package_size = int(line.split(':')[1])

    line = config.readline()
    count += 1


def heart_beat():
    if KeepAlive == 'True':
        timer = Timer(3.0, heart_beat)
        timer.setDaemon(True)
        timer.start()
        sock.sendto('con-h 0x00'.encode(), server_address)
        return
    else:
        return


def send_many_packages():
    for x in range(package_size):
        sock.sendto('Spam'.encode(), server_address)


def three_way_handshake():
    # Connection request sent
    request = 'com-0 ' + client_ip
    print('C: ' + request)
    request_encoded = request.encode()
    sock.sendto(request_encoded, server_address)

    # Response received
    data, address = sock.recvfrom(4096)
    data_decoded = data.decode()
    print('S: ' + data_decoded)

    # Check if server accepts request and that the address matches known server address
    if address == server_address and data_decoded == 'com-0 accept 127.0.0.1':
        accept = 'com-0 accept'
        print('C: ' + accept)
        accept_encoded = accept.encode()
        sock.sendto(accept_encoded, server_address)
        # Three-Way-Handshake is complete when client accept is sent
        print('C: Three way handshake is complete.')
    # If they don't, client closes socket
    else:
        print('C: Three way handshake failed. Closing socket.')
        sock.close()


def communication():

    heart_beat()

    order = 0

    # Sender besked til serveren
    while True:
        print('Write something:')
        client_input = input()

        message = 'msg-' + str(order) + '=' + client_input
        message_encoded = message.encode()
        sock.sendto(message_encoded, server_address)
        order += 1

        response, address = sock.recvfrom(4096)

        if response.decode() == 'con-res=0xFE':
            print('S: Gonna close now.')
            sock.sendto('con-res 0xFF'.encode(), server_address)

        else:
            response_decoded = response.decode().split("=")
            print('S: ' + response_decoded[0] + '=' + response_decoded[1])
            response_body = response_decoded[1]
            response_code = response_decoded[0].split('-')
            response_prefix = response_code[0]
            server_order = response_code[1]

            # Tjekker om svaret fra serveren starter med den rigtige besked og rækkefølge
            if str(order) == server_order:
                order += 1

            else:
                message = 'Wrong order! Closing connection.'
                print('C: ' + message)
                message_encoded = message.encode()
                sock.sendto(message_encoded, server_address)
                sock.close()
