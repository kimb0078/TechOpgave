import UDPServer


state = 0

if state == 0:
    completed = UDPServer.three_way_handshake()
    if completed:
        state = 1

while state == 1:
    UDPServer.communication()




