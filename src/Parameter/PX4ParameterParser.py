import json
import lzma
import bson
import struct

# load_json: json 파일을 불러오는 함수
# @input: json 파일 경로
# @output: json 객체
def load_json(path):
    # etc/extras/parameters.json
    prm = lzma.open(path, "r").read()
    param_json = json.loads(prm)
    for param in param_json['parameters']:
        print(param)

# bson 파일을 불러오는 함수
# @input: json 파일 경로
# @output: json 객체
# fs/parameters_backup.json
def load_bson(path):
    bs_prm = open("../../fs/microsd/parameters_backup.bson","rb").read()
    data = bs_prm
    bs_ld = bson.loads(data)
    return bs_ld

def load_mtd(path):
    return

# mtd_params
#length = struct.unpack("<i", data[base:base + 4])[0]EEEEEE



load_json("../../etc/extras/parameters.json.xz")