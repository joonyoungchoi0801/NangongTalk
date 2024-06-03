import socket
import threading
import tkinter as tk
from tkinter import  scrolledtext, messagebox

class Chat:
    def __init__(self, master): #tk.Tk로 생성된 윈도우 객체
        self.master = master
        self.client_socket = None
        self.nickname = None

        self.master.title("낭공톡")
        self.master.resizable(width=False, height=True) #너비는 고정 높이는 조정 가능
        self.master.config(bg='white')  #아이보리색 배경 (원하는 색으로 변경 하셈)

        self.master.grid_rowconfigure(0, weight=1) #row 0번째에 대한 가중치 1
        self.master.grid_rowconfigure(1, weight=1) #row 1번째에 대한 가중치 1
        self.master.grid_rowconfigure(2, weight=1) #row 2번째에 대한 가중치 1
        self.master.grid_rowconfigure(3, weight=1) #row 3번째에 대한 가중치 1
        self.master.grid_rowconfigure(4, weight=1) #row 4번째에 대한 가중치 1
        self.master.grid_columnconfigure(0, weight=1) #column 0번째에 대한 가중치 1 (가로로 늘리기 위함)

        self.port_label = tk.Label(master, text="들어갈 방 번호를 입력하세요(9990~10000)")
        self.port_label.grid(row=0, column=0,padx=10, pady=10)

        self.port_input = tk.Spinbox(master, from_=9990, to=10000)
        self.port_input.grid(row=1, column=0,padx=10, pady=10)

        self.nickname_label = tk.Label(master, text="닉네임")
        self.nickname_label.grid(row=2, column=0, padx=10, pady=10 )

        self.nickname_input = tk.Entry(master, fg='grey')
        self.nickname_input.insert(0, "닉네임을 입력하세요")
        self.nickname_input.bind("<FocusIn>", self.clear_placeholder)
        self.nickname_input.bind("<FocusOut>", self.add_placeholder)
        self.nickname_input.grid(row=3, column=0, padx=10, pady=10 )

        self.connect_button = tk.Button(master, text="Connect", command=self.connect_to_server)
        self.connect_button.grid(row=4, column=0, padx=10, pady=10 )
        self.master.protocol("WM_DELETE_WINDOW", self.start_thread)
        

    def clear_placeholder(self,event): # 닉네임 entry에 포커스가 들어왔을 때
        if self.nickname_input.get() == "닉네임을 입력하세요":
            self.nickname_input.delete(0, tk.END)
            self.nickname_input.config(fg='black')

    def add_placeholder(self,event): # 닉네임 entry에 포커스가 나갔을 때 placeholder추가
        if not self.nickname_input.get():
            self.nickname_input.insert(0, "닉네임을 입력하세요")
            self.nickname_input.config(fg='grey')


    def connect_to_server(self):
        port = int(self.port_input.get()) #entry 에서 가져온 포트 번호
        self.nickname = self.nickname_input.get() #entry 에서 가져온 닉네임
        if self.nickname == "닉네임을 입력하세요" or not self.nickname: #닉네임이 입력되지 않았을 때
            messagebox.showerror("Input Error", "닉네임을 입력하세요.")
            return
        if not port: # 포트 번호가 입력되지 않았을 때
            messagebox.showerror("Input Error", "방 번호를 입력하세요.")
            return 
        if not 9990 <= port <= 10000: # 포트 번호가 9990~10000 사이가 아닐 때
            messagebox.showerror("Input Error", "9990~10000 사이의 방 번호를 입력하세요.")
            return
        
        for widget in self.master.winfo_children():
            widget.grid_forget() #이전 grid 요소들 지우기

        self.master.geometry("400x800") # 채팅창 크기 조정
        self.master.grid_rowconfigure(0, weight=100) #채팅창 : 메시지 입력창 비율 조정 (채팅창 위주로 해서 weight 높게 줌)
        self.master.grid_rowconfigure(1, weight=1)
        self.master.config(bg='#FFFFF0') #아이보리색 배경 (원하는 색으로 변경 하셈)

        self.chat_display = scrolledtext.ScrolledText(self.master, state='disabled',bg='#87CEEB') #채팅창 생성  배경색 스카이블루(y축스크롤바 추가)
        self.chat_display.grid(row=0, column=0, columnspan=2, padx=10, pady=10,sticky="nsew") # sticky 동서남북으로 붙기 패딩은 10 

        self.message_input = tk.Entry(self.master)
        self.message_input.grid(row=1, column=0, padx=10, pady=10, sticky="ew") # sticky 동서로 붙기 패딩은 10 
        self.message_input.bind("<Return>", self.send_message)

        self.send_button = tk.Button(self.master, text="Send", width=8,command=self.send_message)
        self.send_button.grid(row=1, column=1, padx=10, pady=10, sticky="ew") # sticky 동서로 붙기 패딩은 10


        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # 소켓 생성
        try:
            self.client_socket.connect(('127.0.0.1', port))
            self.client_socket.send(self.nickname.encode('utf-8')) # ascii는 한국어 안되서 utf-8로 변경 (정 뭐 말하기 그러면 웹에서도 사용하는 다국어 문자 지원 인코딩 방식)
            threading.Thread(target=self.receive_messages).start()

        except ConnectionRefusedError:
            messagebox.showerror("Connection Error", "서버 연결에 실패하였습니다 다른 방 번호를 입력하세요.")
            return
        
        

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8') # 메시지 받기
                self.master.after(0, self.update_chat_display, message) # 메시지 받고 0ms 이후에 바로 채팅창에 메시지 업데이트
            except Exception:
                self.client_socket.close() #오류시 소켓 닫기
                break

    def update_chat_display(self, message):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, message + '\n') # 채팅창 마지막에 메시지 추가 후 줄바꿈
        self.chat_display.config(state='disabled')
        self.chat_display.yview(tk.END) # 스크롤바를 항상 마지막 메시지로 이동
    

    def send_message(self, event=None):
        message = self.message_input.get() # 메시지 입력창에서 메시지 가져오기
        if message == "":
             messagebox.showerror("Input error","메시지를 입력하세요")
             return
        self.message_input.delete(0, tk.END) # 메시지 입력창 비우기 (가져오고 비우는거임)
        self.client_socket.send(f'{self.nickname}: {message}'.encode('utf-8')) # 닉네임 : 메시지 전송

    def start_thread(self): # 응답없음 방지를 위한 쓰레드 생성 (파이썬이 싱글 쓰레드 여서 멀티 쓰레드 방식으로 변경)
        thread = threading.Thread(target=self.close_client)
        thread.daemon = True #daemon이라고 나중에 시스템 프로그램 혹은 운영체제에서 배워^^
        thread.start()

    def close_client(self): # 유저가 x버튼 눌러 채팅창 나갈 때
        if self.client_socket:
            self.client_socket.send(f'{self.nickname}가 채팅방을 떠났습니다.'.encode('utf-8')) # 채팅방 나감 메시지 전송
            self.client_socket.close() # 소켓 닫기
        self.master.quit() # 채팅창 종료

    
root = tk.Tk() #윈도우 객체 생성 (tkinter)
chat_client = Chat(root) #채팅 객체 생성
root.mainloop() #윈도우 객체 실행
