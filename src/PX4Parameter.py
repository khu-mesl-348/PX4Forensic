from src.Parameter.PX4ParameterParser import load_json, load_bson 
import pandas
import os
'''
구현할 기능

1. Parameter 내부 정보 가져오기 parameter_config.json (번역 추가?)
2. Parameter 가져오기 (/fs/mtd_params)
3. 변경된 Parameter (1번을 이용해서 대조하면 될듯)
4. 파라미터 수정기능 (/fs/mtd_params에 적어야 하는데 어떻게 해야할까? Write()를 호출하는 방법은?)
5. 파라미터 백업 파일 가져오기
6. 파라미터 파일 무결성 유지 (hash값)

'''

def get_parameters():
    print(os.getcwd())
    data1 = load_json("./etc/extras/parameters.json.xz")
    data2 = load_bson("./fs/microsd/parameters_backup.bson")
    
    #print(data1['version'],data1['parameters'])
    #print(data2)
    
    res = []
    for param in data1['parameters']:
        for backup in data2:
            if param['name'] == backup['name']:
                param['value'] = backup['value']
                break
        res.append(param)
    return res

res = get_parameters()

