import threading, socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 2500))

def recvMsg(sock):
    while 1:
        try:
            r_msg = sock.recv(1024)
            if not r_msg:
                print("연결이 종료되었습니다")
                break
        except:
            print("연결이 종료되었습니다")
            sock.close()
            break
        else:
            print(r_msg.decode())

def sendMsg(sock):
    tRecv = threading.Thread(target=recvMsg, args=(sock,))
    tRecv.daemon = True
    tRecv.start()
    while 1:
        msg = input()
        try:
            if msg == '/나가기':
                sock.sendall(msg.encode()) 
                sock.close()
                break
        except:
            print('송신 연결이 종료되었습니다')
            break
        else:
            sock.sendall(msg.encode()) 

if __name__ == '__main__':
    sendMsg(sock)