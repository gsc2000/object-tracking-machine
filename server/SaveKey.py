import os
import sys
import libs.Util as Util

import time
import json

# loggerの設定
logger = Util.childLogger(__name__)

class Savekey():
    def __init__(self, config: dict, regi_frame: tuple) -> None:
        # キーの読み込み
        # --------------------------------------------------
        self.path = config["KEY"]["PATH"]
        regi_key = open(self.path, 'r')
        self._regi_key: dict = json.load(regi_key) # 現状のキー設定
        self.key_cnt = 0
        self.num_key = config["KEY"]["NUM"]

        self.count = config["KEY"]["COUNT"] # 登録までのカウント
        self.timer = config["KEY"]["COUNT"] # カウンター
        self.regi_frame = regi_frame # 登録枠

        self.prev_obj = None # 前回まで映っていた物体

        self.ret_timer = 0

        self.status = None # キー登録の状態
        # None: キー登録処理開始前
        # 0: キー登録待ち
        # 1: キー登録中
        # 2: キー登録直後
        # 3: 全てのキー登録直後
        # 4: 全てのキー登録済み
        # 50: 今回の物体は登録済み
        # 51: いっぱい検出している

    def run(self, det: list):
        logger.debug(self.status)
        # logger.debug(det)
        if self.status == None: # 登録開始
            self.keyReset()
            self.status = 0 # キー登録待ちへ変更
        elif self.status == 0 or self.status == 50 or self.status == 51: # キー登録待ち
            self.setReset()
            self.setKey(det) # この中でステータス変わる
        elif self.status == 1: # キー登録処理中
            self.setKey(det) # この中でステータス変わる
        elif self.status == 2: # キーが登録されてすぐの場合
            regi_after = time.time()-self.ret_timer # 経過時間
            if regi_after < 3:
                return self.timer, self.status
            else:
                self.status = 0 # キー登録待ちへ戻す
                return self.timer, self.status
        elif self.status == 3:
            # JSON保存
            with open(self.path, 'w') as f:
                json.dump(self._regi_key, f, indent=4)
            self.status = 4
            pass
        elif self.status == 4:
            pass

        return self.timer, self.status

    @property
    def regi_key(self):
        return self._regi_key

    def keyReset(self):
        """
        キー情報の初期化
        """
        self._regi_key = {}
        for i in range(self.num_key):
            self._regi_key["key{}".format(i)] = None

        self.key_cnt = 0

    def setReset(self):
        """
        キー登録に必要な情報の初期化
        """
        logger.debug("Reset")
        self.prev_obj = None
        self.timer = self.count
        self.st_timer = time.time()

    def setKey(self, det: list):
        """
        キー登録処理
        """
        obj = self.updateStatus(det)

        if obj != None: # キー設定できる状態
            self.timer = self.count-(time.time()-self.st_timer)
            # print((time.time()-self.st_timer))
            if self.timer <= 0:
                logger.info("Set")
                self.status = 2 # セットできたよ
                self.ret_timer = time.time()
                self.timer = 0
                self._regi_key["key{}".format(self.key_cnt)] = obj[2]
                self.key_cnt += 1

    def updateStatus(self, det: list) -> int:
        """
        キー登録の条件を満たしているか確認
        """
        cnt = 0
        for _key in self._regi_key.values():
            if _key != None:
                cnt += 1
        if cnt >= self.num_key:
            self.status = 3
            return None
        if len(det) < 1: # 検出有無
            self.status = 0
            return None

        in_frame_num = []
        for _det in det:
            in_frame = ((self.regi_frame[0] < _det[0] < self.regi_frame[2]) and
                        (self.regi_frame[1] < _det[1] < self.regi_frame[3]))
            in_frame_num.append(in_frame)
        if in_frame_num.count(True) > 1: # 枠内の物体が1以上の場合
            self.status = 51
            return None
        elif in_frame_num.count(True) == 0: # 枠内に物体がない場合
            self.status = 0
            return None

        obj = det[in_frame_num.index(True)] # 枠内にある物体の情報を取得
        if obj[2] in self._regi_key.values(): # 既に登録されていないか
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
