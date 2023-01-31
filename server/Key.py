import os
import sys
import libs.Util as Util

import time
import json

# loggerの設定
logger = Util.childLogger(__name__)

class Savekey():
    def __init__(self, config: dict, frame: tuple) -> None:
        # キー情報
        # --------------------------------------------------
        self.path = config["KEY"]["PATH"] # キー保存パス
        self.num_key = config["KEY"]["NUM"] # キーの数
        self.cnt_time = config["KEY"]["COUNT"] # 登録までの時間
        self.timer = config["KEY"]["COUNT"] # カウンタ
        self.key_cnt = 0 # 登録されたキーのカウンタ

        # 現状のキーを取得
        self._reg_key: dict = json.load(open(self.path, 'r'))
        # 新規のキー
        self.new_key: dict = None

        # キー登録に必要な情報
        # --------------------------------------------------
        self.frame = frame # 登録枠
        self.st_time = None # 登録開始した時間
        self.prev_obj = None # 前回まで映っていた物体
        self.reg_time = None # 登録された時間

        self.status = None # キー登録の状態
        # None: キー登録処理開始前
        # 0: キー登録待ち
        # 1: キー登録中
        # 2: キー登録直後
        # 3: 全てのキー登録直後
        # 4: 全てのキー登録済み
        # 5: 終わり
        # 50: 今回の物体は登録済み
        # 51: いっぱい検出している

    def init(self):
        self.status = None

    def run(self, flg: bool, det: list):
        if flg:
            self.init()
        # logger.debug(self.status)
        if self.status == None: # 登録開始
            self.keyReset()
            self.status = 0 # キー登録待ちへ変更
        elif self.status == 0 or self.status == 50 or self.status == 51: # キー登録待ち
            self.setReset()
            self.setKey(det) # この中でステータス変わる
        elif self.status == 1: # キー登録処理中
            self.setKey(det) # この中でステータス変わる
        elif self.status == 2: # キーが登録されてすぐの場合
            after = time.time()-self.reg_time # 経過時間
            if after < 3:
                pass
            else:
                self.status = 0 # キー登録待ちへ戻す
                self.setReset()
        elif self.status == 3:
            # JSON保存
            with open(self.path, 'w') as f:
                json.dump(self.new_key, f, indent=4)
            self._reg_key = self.new_key
            self.status = 4
            self.fin_time = time.time()
        elif self.status == 4:
            after = time.time()-self.fin_time
            if after < 3:
                pass
            else:
                self.status = 5

        return self.timer, self.status

    @property
    def reg_key(self):
        return self._reg_key

    def keyReset(self):
        """
        キー情報の初期化
        """
        self.new_key = {}
        for i in range(self.num_key):
            self.new_key["key{}".format(i)] = None

        self.key_cnt = 0

    def setReset(self):
        """
        キー登録に必要な情報の初期化
        """
        self.prev_obj = None
        self.timer = self.cnt_time
        self.st_time = time.time()

    def setKey(self, det: list):
        """
        キー登録処理
        """
        obj = self.updateStatus(det)

        if obj != None: # キー設定できる状態
            self.timer = self.cnt_time-(time.time()-self.st_time)
            if self.timer <= 0:
                logger.info("Set")
                self.status = 2 # セットできたよ
                self.reg_time = time.time()
                self.timer = 0
                self.new_key["key{}".format(self.key_cnt)] = obj[2]
                self.key_cnt += 1

    def updateStatus(self, det: list) -> int:
        """
        キー登録の条件を満たしているか確認
        """
        cnt = 0
        for key in self.new_key.values():
            if key != None:
                cnt += 1
        if cnt >= self.num_key:
            self.status = 3
            return None
        if len(det) < 1: # 検出有無
            self.status = 0
            return None

        in_frame_num = []
        for _det in det:
            in_frame = ((self.frame[0] < _det[0] < self.frame[2]) and
                        (self.frame[1] < _det[1] < self.frame[3]))
            in_frame_num.append(in_frame)
        if in_frame_num.count(True) > 1: # 枠内の物体が1以上の場合
            self.status = 51
            return None
        elif in_frame_num.count(True) == 0: # 枠内に物体がない場合
            self.status = 0
            return None

        obj = det[in_frame_num.index(True)] # 枠内にある物体の情報を取得
        if obj[2] in self.new_key.values(): # 既に登録されていないか
            self.status = 50
            return None

        if self.prev_obj == None: # 前回物体を検出しているか
            self.status = 1
            return obj
        elif self.prev_obj == obj[2]:
            self.status = 1
            return obj
        elif self.prev_obj != obj[2]:
            self.status = 0
            return obj

class Unlock():
    def __init__(self, config: dict, frame: tuple) -> None:
        # キー情報
        # --------------------------------------------------
        self.num_key = config["KEY"]["NUM"] # キーの数
        self.cnt_time = config["KEY"]["COUNT"] # 認証までの時間
        self.timer = config["KEY"]["COUNT"] # カウンタ
        self.key_cnt = 0 # 認証されたキーのカウンタ

        self.auth_key = None # 認証用キー

        # キー認証に必要な情報
        # --------------------------------------------------
        self.frame = frame # 認証枠
        self.st_time = None # 認証開始した時間
        self.prev_obj = None # 前回まで映っていた物体
        self.auth_time = None # 認証された時間
        self.ng_time = None # 認証失敗した時間

        self.status = None # キー認証の状態
        # None: キー認証処理開始前
        # 0: キー認証待ち
        # 1: キー認証中
        # 2: キー認証直後
        # 3: 全てのキー認証直後
        # 4: 全てのキー認証済み
        # 10: 認証失敗
        # 50: 今回の物体は認証済み
        # 51: いっぱい検出している

    def init(self):
        self.status = None
        # logger.debug(self.status)

    def run(self, flg: bool, det: list, reg_key: dict):
        # if flg:
        #     self.init()
        logger.debug(self.status)
        if self.status == None: # 認証処理前
            self.keyReset()
            self.status = 0 # キー認証待ちへ変更
        elif self.status == 0 or self.status == 50 or self.status == 51: # キー認証待ち
            self.setReset()
            self.setKey(det) # この中でステータス変わる
        elif self.status == 1: # キー認証中
            self.setKey(det) # この中でステータス変わる
        elif self.status == 2: # キー認証されてすぐの場合
            after = time.time()-self.auth_time # 経過時間
            if after < 3:
                pass
            else:
                self.status = 0 # キー認証待ちへ戻す
                self.setReset()
        elif self.status == 3:
            # 判定する
            result = True
            for i in range(self.num_key):
                if self.auth_key["key{}".format(i)] != reg_key["key{}".format(i)]:
                    result = False
            if result:
                self.status = 4
            else:
                self.status = 10
                self.ng_time = time.time()
        elif self.status == 4:
            pass
        elif self.status == 10:
            after = time.time()-self.ng_time
            if after < 3:
                pass
            else:
                self.status = None # 認証処理前に戻す

        return self.timer, self.status

    def keyReset(self):
        """
        キー情報の初期化
        """
        self.auth_key = {}
        for i in range(self.num_key):
            self.auth_key["key{}".format(i)] = None

        self.key_cnt = 0

    def setReset(self):
        """
        キー認証に必要な情報の初期化
        """
        self.prev_obj = None
        self.timer = self.cnt_time
        self.st_time = time.time()

    def setKey(self, det: list):
        """
        キー認証処理
        """
        obj = self.updateStatus(det)

        if obj != None: # キー認証できる状態
            self.timer = self.cnt_time-(time.time()-self.st_time)
            if self.timer <= 0:
                logger.info("Set")
                self.status = 2 # セットできたよ
                self.auth_time = time.time()
                self.timer = 0
                self.auth_key["key{}".format(self.key_cnt)] = obj[2]
                self.key_cnt += 1

    def updateStatus(self, det: list) -> int:
        """
        キー登録の条件を満たしているか確認
        """
        cnt = 0
        for key in self.auth_key.values():
            if key != None:
                cnt += 1
        if cnt >= self.num_key:
            self.status = 3
            return None
        if len(det) < 1: # 検出有無
            self.status = 0
            return None

        in_frame_num = []
        for _det in det:
            in_frame = ((self.frame[0] < _det[0] < self.frame[2]) and
                        (self.frame[1] < _det[1] < self.frame[3]))
            in_frame_num.append(in_frame)
        if in_frame_num.count(True) > 1: # 枠内の物体が1以上の場合
            self.status = 51
            return None
        elif in_frame_num.count(True) == 0: # 枠内に物体がない場合
            self.status = 0
            return None

        obj = det[in_frame_num.index(True)] # 枠内にある物体の情報を取得
        if obj[2] in self.auth_key.values(): # 既に登録されていないか
            self.status = 50
            return None

        if self.prev_obj == None: # 前回物体を検出しているか
            self.status = 1
            return obj
        elif self.prev_obj == obj[2]:
            self.status = 1
            return obj
        elif self.prev_obj != obj[2]:
            self.status = 0
            return obj