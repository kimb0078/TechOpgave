import socket


# Bind the socket to the port
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('127.0.0.1', 1234)
server_ip = server_address[0]
print('S: starting up on {} port {}'.format(*server_address))
sock.bind(server_address)


def three_way_handshake():

    # Receives connection request and saves client ip
    data, address_1 = sock.recvfrom(4096)
    data_decoded = data.decode()
    print('C: ' + data_decoded)
    client_ip = data_decoded.split(" ")[1] # Recognises the part after the space as client's IP
    ip_parts = client_ip.split(".") # Splits the ip address into separate parts with "."
    print(ip_parts)

    # Checks if each part is between 0 and 255
    for i in ip_parts:
        # Closes socket, if one of the parts is not in that range
        if int(i) > 255 or int(i) < 0:
            ip_denial = 'Connection denied. ' + client_ip + ' is an invalid IP address.'
            print('S: ' + ip_denial)
            ip_denial_encoded = ip_denial.encode()
            sock.sendto(ip_denial_encoded, address_1)
            sock.close()

    # If it hasn't closed the socket, IP is marked as valid
    valid_client_ip = client_ip

    # Checks request. If request is in valid format, server sends accept message
    if data_decoded == 'com-0 ' + valid_client_ip:
        accept = 'com-0 accept ' + server_ip
        print('S: ' + accept)
        accept_encoded = accept.encode()
        sock.sendto(accept_encoded, address_1)
    # If request is invalid, server sends denial message and closes socket
    else:
        denial = 'Connection denied'
        print('S: ' + denial)
        denial_encoded = denial.encode()
        sock.sendto(denial_encoded, address_1)
        sock.close()

    # If the server accepted the connection, server waits for next data transfer
    data, address_2 = sock.recvfrom(4096)
    data_decoded = data.decode()
    print('C: ' + data_decoded)

    # If client sends incorrect acceptance message
    # or the address doesn't match the address from the initial request,
    # the client acceptance is denied
    if address_1 != address_2 or data_decoded != 'com-0 accept':
        denial = 'Invalid accept. Server is closing down now.'
        print('S: ' + denial)
        denial_encoded = denial.encode()
        sock.sendto(denial_encoded, address_2)
        sock.close()
        return False

    else:
        print('S: Three way handshake is complete!')
        return True


def communication():
    sock.settimeout(4.0)
    order = 0

    # Modtager besked fra client
    while True:
        message, address = sock.recvfrom(4096)

        try:
            if message.decode() == 'con-res=0xFF':
                print('C: Okay.')
                sock.close()
            if message.decode() == 'con-h 0x00':
                print('C: con-h 0x00')
                continue
            if message.decode() == 'Spam':
                print('C: ' + message.decode())
                continue

            message_decoded = message.decode().split("=")
            print('C: ' + message_decoded[0] + '=' + message_decoded[1])
            message_code = message_decoded[0].split('-')
            message_body = message_decoded[1]
            message_prefix = message_code[0]
            client_order = message_code[1]

            # Tjekker om beskeden fra kunden starter med den rigtige besked og rækkefølge
            if message_prefix == 'msg' and str(order) == client_order:

                order = order + 1
                response = 'res-' + str(order) + '= I am server.'
                print('S: ' + response)
                response_encoded = response.encode()
                sock.sendto(response_encoded, address)
                order += 1

            else:
                response = 'Wrong order! Closing connection.'
                print('S: ' + response)
                response_encoded = response.encode()
                sock.sendto(response_encoded, address)
                sock.close()
                return False

        except socket.timeout:
            sock.sendto('con-res=0xFE'.encode(), address)
            print('S: Gonna close now.')
