import socket, threading
import sqlite3

con = sqlite3.connect('usdb.db', check_same_thread=False)  # 에러로 인한 쓰레드를 직렬방식으로 바꿔서 사용
with con:
    cur = con.cursor()
    con.commit()


class Server:
    def __init__(self):
        pass

    def server(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('127.0.0.1', 2500))
        self.sock.listen(5)
        self.clients = []
        print('서버가 실행됩니다.')

    def accept_ct(self):
        self.server()  # 서버
        self.user = User()  # 유저
        while 1:
            c_sock, c_addr = self.sock.accept()
            print(f'{c_addr}접속')
            c = Chat(self.user, c_sock)  # 채팅
            self.user.addClient(c)
            th = threading.Thread(target=c.recvdMsg)
            th.start()
        self.sock.close()


class Chat:
    def __init__(self, user, c_sock):
        self.user = user  
        self.nickName = None
        self.c_sock = c_sock

    def comeIn(self):
        self.log = UserLogin()
        self.c_sock.send('1.로그인 2.회원가입 : '.encode())
        msg = self.c_sock.recv(1024).decode()

        if msg == '1':
            self.c_sock.send('[Id/Pw 입력]'.encode())
            msg = self.c_sock.recv(1024).decode()
            log = msg.split('/')
            self.id = log[0]
            self.pw = log[1]
            print(self.log.login(self.id, self.pw))
            self.c_sock.send(f'{self.id}님 로그인 성공!'.encode())
        elif msg == '2':
            self.c_sock.send('[Id/Pw 입력]'.encode())
            msg = self.c_sock.recv(1024).decode()
            log = msg.split('/')
            self.id = log[0]
            self.pw = log[1]
            self.log.signUp(self.id, self.pw)
            self.c_sock.send('회원가입 완료! 로그인 진행 바람'.encode())
            return self.comeIn()

        self.c_sock.send('채팅을 시작합니다 '.encode())
        self.c_sock.send("'닉 네임'을 입력하세요".encode())
        self.nickName = self.c_sock.recv(1024).decode()

        print(f'[{self.nickName}] 님이 입장하셨습니다')
        self.user.sendMsgAll(f'[{self.nickName}] 님이 입장하셨습니다')

    def recvdMsg(self):
        self.comeIn()  # 입장
        while 1:
            try:
                msg = self.c_sock.recv(1024).decode()
                if not msg:
                    self.c_sock.sendall(msg)
                    self.user.delClient(self)
                    break
            except:
                self.user.sendMsgAll(f'[{self.nickName}] 님이 퇴장하셨습니다.')
                break
            else:
                msg = (f'[{self.nickName}]: {msg}')  # 채팅방 메세지 입력
                self.user.sendMsgAll(msg)

    def sendMsg(self, msg):
        self.c_sock.sendall(msg.encode())


class User:  # 유저 분리
    def __init__(self):
        self.clients = []  # 접속자

    def addClient(self, c):  # 더하기
        self.clients.append(c)

    def delClient(self, c):  # 삭제
        self.clients.remove(c)

    def sendMsgAll(self, msg):
        for ct in self.clients:
            ct.sendMsg(msg)


class UserLogin:
    def login(self, id, pwd):  # 로그인 1
        cur.execute('SELECT * FROM usdb WHERE id=?', (id,))
        IDresult = cur.fetchone()
        cur.execute('SELECT * FROM usdb WHERE pw=?', (pwd,))
        PWresult = cur.fetchone()

        if None == IDresult or None == PWresult:
            return '로그인 실패! 재입력 바람'
        else:
            return '로그인 성공! 채팅을 시작합니다'

    def signUp(self, id, pwd):  # 회원가입 2
        cur.execute('INSERT INTO usdb (id, pw) VALUES (?, ?)', (id, pwd,))
        con.commit()
        print('회원가입 완료')


if __name__ == "__main__":
    cs = Server()
    cs.accept_ct()