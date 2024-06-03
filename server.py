import socket
import threading

host = '127.0.0.1'
start_port = 9990
end_port = 10000

clients_dict = {}
nicknames_dict = {}
stop_event = threading.Event()

def broadcast(message, clients):
    for client in clients:
        try:
            client.send(message) # 클라이언트에게 메시지 전송
        except:
            clients.remove(client) # 클라이언트가 연결을 끊으면 제거

def handle(client, clients, nicknames): # 클라이언트 핸들링 함수 메시지 받고 전송하는 역할
    while not stop_event.is_set():
        try:
            message = client.recv(1024) # 클라이언트로부터 메시지 받기
            broadcast(message, clients) # 모든 클라이언트에게 메시지 전송
        except:
            index = clients.index(client) # 클라이언트가 연결을 끊으면 제거
            clients.remove(client) 
            client.close() 
            nickname = nicknames[index] 
            nicknames.remove(nickname)
            break

def receive(server, port): # 서버에서 클라이언트 연결 받는 함수
    while not stop_event.is_set():
        try:
            server.settimeout(1.0)  # 1초마다 타임아웃하여 stop_event를 확인
            client, address = server.accept()
            print(f"Connected with {str(address)} on port {port}") # 클라이언트가 연결되었을 때 출력 (cli창)
            nickname = client.recv(1024).decode('utf-8') # 닉네임 받기
            nicknames_dict[port].append(nickname) # 닉네임과 포트를 매핑
            clients_dict[port].append(client) # 클라이언트와 포트를 매핑

            print(f"Nickname of the client is {nickname} on port {port}!")
            broadcast(f'{nickname}님이 입장하셨습니다!\n'.encode('utf-8'), clients_dict[port]) # 유저한테 누가 입장 했는지 알림
            client.send(f'{port}번방에 입장하셨습니다!'.encode('utf-8'))  # 유저한테 무슨 방 입장 했는지 알림

            thread = threading.Thread(target=handle, args=(client, clients_dict[port], nicknames_dict[port])) # 쓰레드 생성 (handle 함수 호출 arg는 함수 인자)
            thread.start()
        except socket.timeout:
            continue

def start_server_on_port(port): # 포트에 대한 서버 시작 함수 (포트는 9990~10000 사이의 포트를 사용)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # 소켓 생성
    server.bind((host, port)) # 소켓 바인딩 (서버 주소와 포트 번호 할당 및 클라이언트 연결 대기 상태로 만듬)
    server.listen() # 소켓 리스닝 (연결 요청 수신가능 상태로 만듬)
    clients_dict[port] = []
    nicknames_dict[port] = []
    print(f"Server started on port {port}")
    threading.Thread(target=receive, args=(server, port)).start() # 쓰레드 생성 (receive 함수 호출 arg는 함수 인자)
    return server

# 각 포트에 대해 서버 시작
servers = [] # 서버 리스트 저장 리스트
for port in range(start_port, end_port + 1): # 9990~10000 사이의 포트를 사용
    server = start_server_on_port(port)
    servers.append(server)

def stop_servers(): # 서버 종료 함수
    stop_event.set()
    for port in range(start_port, end_port + 1):
        if port in clients_dict:
            for client in clients_dict[port]:
                client.close()
    print("Servers stopped")

# 종료 명령 대기
try:
    while True:
        command = input()
        if command.lower() == 'exit': # exit 입력시 서버 종료
            stop_servers()
            break
except KeyboardInterrupt: # ctrl+c 입력시 서버 종료
    stop_servers()
