# 一般的なやつ

import sys
import logging
import os
import errno
import datetime

import json

# def used_memory(dir_tmp = dir()):
#     '''
#     メモリ確認
#     '''
#     print("{}{: >25}{}{: >20}{}".format('|','Variable Name','|','Memory[byte]','|'))
#     print(" "+"-"*46+" ")
#     used_memory = 0
#     for var_name in dir_tmp:
#         if not var_name.startswith("_"):
#             print("{}{: >25}{}{: >20}{}".format('|',var_name,'|',sys.getsizeof(eval(var_name)),'|'))
#             used_memory += sys.getsizeof(eval(var_name))
#     print(" "+"-"*46+" ")
#     print("Used Memory: {}[byte]".format(used_memory))
#     print("Used Memory: {:.2f}[Mbyte]".format(used_memory/1000000))
#     print("Used Memory: {:.2f}[Gbyte]".format(used_memory/1000000000))

def dir_check(dir:str):
    if os.path.exists(dir) is False:
            try:
                os.makedirs(dir)
            except Exception as e:
                raise e


def rootLogger(dir, log_level):
    '''
    ログ取得用
    '''
    dir_check(dir)
    if log_level == "DEBUG":
        logger_level = logging.DEBUG
    elif log_level == "INFO":
        logger_level = logging.INFO
    elif log_level == "WARNING":
        logger_level = logging.WARNING
    elif log_level == "ERROR":
        logger_level = logging.ERROR
    elif log_level == "CRITICAL":
        logger_level = logging.CRITICAL

    # サードパーティのログを消すためにレベルをあげる
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("h5py").setLevel(logging.WARNING)

    logger = logging.getLogger()
    logger.setLevel(logger_level)

    # ログの記述フォーマット
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter('%(asctime)s:\t%(levelname)s\t%(name)s\t%(funcName)s\t%(message)s')

    # ストリームハンドラの設定
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logger_level)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # # ファイルハンドラ作成
    ch = logging.FileHandler(filename=dir+"/"+str(datetime.datetime.now().strftime("%Y%m%d"))+".log")
    ch.setLevel(logger_level)
    ch.setFormatter(formatter) # ファイルハンドラにフォーマット情報を与える
    logger.addHandler(ch) # logger(インスタンス)にファイルハンドラの情報を与える

    return logger

def childLogger(name):
    '''
    ログ取得用
    '''
    logger = logging.getLogger(name)
    # logger.addHandler(logging.NullHandler())
    # logger.setLevel(logging.DEBUG)
    # logger.propagate = True

    return logger

# Loggerの設定
logger = childLogger(__name__)

def read_json(file_path):
    '''
    JSONファイル読み込み
    '''
    # 指定したファイルが存在しない場合、エラー発生
    if not os.path.exists(file_path):
        logger.critical("Read_Error")
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file_path)

    # ファイルの読み込み
    with open(file_path, encoding="utf-8") as f:
        file_data = json.load(f)

    return file_data

def check_json(file_data):
    '''
    辞書データ中身確認
    '''
    if file_data.items() is None:
        raise
    for key, value in file_data.items():
        print("key: {}\nVal: {}\tClass: {}".format(key, value, type(value)))


if __name__=="__main__":
    # # Configデータ読取り
    config = read_json("../config/config.json")
    # check_json(config)

    # 仕様情報読取り
    # spec = read_json("../config/spec_info.json")
    # check_json(spec)
    # key = [k for k, v in spec.items() if v["SEBAN"] == "4P6"]
    # print(key[0])
    # if len(key) != 1:
    #     print("Error")

    # print(spec[key[0]]["HINBAN"])
    # part_number = [spec[key[0]]["HINBAN"] for i in range(int(spec[key[0]]["NUM"]))]
    # print(part_number)

    logger = rootLogger(config["LOG_EXE_DIR"], config["LOG_LEVEL"])
    logger.info("test")
