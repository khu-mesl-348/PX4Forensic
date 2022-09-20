'''
구현할 기능

1. 로그파일 가져와서 열기
2. 로그 파일 내부 구조 보여주기
3. 로그 파일 생성 일자, 해쉬값, 암호화 여부 등 파악
4. 로그 파일 시각화

'''
import os

path = "fs/microsd/log"

# os.system('ulog_info fs/microsd/log/2022-07-18/09_39_09.ulg')  #info

# os.system('ulog_params fs/microsd/log/2022-07-18/09_39_09.ulg') #params

# os.system('ulog_messages fs/microsd/log/2022-07-18/09_39_09.ulg') # log message

def log_info():
    info_result = os.popen('ulog_info fs/microsd/log/2022-07-18/09_39_09.ulg').read()
    print(info_result)

def log_params():
    params_result = os.popen('ulog_params fs/microsd/log/2022-07-18/09_39_09.ulg').read()
    print(params_result)

def log_messages():
    messages_result = os.popen('ulog_messages fs/microsd/log/2022-07-18/09_39_09.ulg').read()
    print(messages_result)

def ulog_2_csv():
    os.system('ulog2csv fs/microsd/log/2022-07-18/09_39_09.ulg')

#log_info()
#log_params()
#log_messages()

