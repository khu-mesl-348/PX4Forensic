import json
import lzma
import bson
import struct

# load_json: json 파일을 불러오는 함수
# @input: json.xz 파일 경로
# @output: json 객체
def load_json(path):
    # etc/extras/parameters.json
    prm = lzma.open(path, "r").read()
    param_json = json.loads(prm)
    return param_json

# bson 파일을 불러오는 함수
# @input: json 파일 경로
# @output: json 객체
# fs/parameters_backup.json
def load_bson(path):
    bs_prm = open(path,"rb").read()
    data = bs_prm
    bs_ld = bson.loads(data)
    res = []
    for item in bs_ld:
        res.append({'name': item, 'value': bs_ld[item]})
    return res

def load_mtd(path):
    return

# mtd_params
#length = struct.unpack("<i", data[base:base + 4])[0]EEEEEE



