import threading
import ctypes

from . import Utility

logger = Utility.childLogger(__name__)

class SubThread(threading.Thread):
    '''
    サブスレッド
    '''
    def __init__(self, name):
        super().__init__()
        self.daemon = True
        self.name = name
    
    def run(self):
        '''
        サブスレッドでの処理内容
        try分で処理すること
        '''
        pass
    
    def get_id(self):
        '''
        サブスレッドのIDを取得
        '''
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id
    
    def kill(self):
        '''
        サブスレッド強制終了
        '''
        # thread_id = self.get_id()
        resu = ctypes.pythonapi.PyThreadState_SetAsyncExc(self.native_id,
                                                          ctypes.py_object(SystemExit))
        if resu > 1: 
            ctypes.pythonapi.PyThreadState_SetAsyncExc(self.native_id, 0)
            logger.info('Failure_in_raising_exception')

# class Monitoring(SubThread):
#     def __init__(self, error_q: queue.Queue, lock: threading.Lock):
#         super().__init__("Monitor")
#         self.error_q = error_q
#         self.lock = lock
    
#     def run(self):
#         while True:
#             while not self.error_q.empty():
#                 error_data = self.error_q.get(block=False) # Queueのエラー内容を取得
#                 name = error_data[0]
#                 LOGGER.info("Error thread: {}".format(name))

#                 self.lock.acquire()
#                 for error_thread in threading.enumerate():
#                     if error_thread.getName() == name:
#                         LOGGER.info("kill thread: {}".format(error_thread.getName()))
#                         error_thread.kill()
#                 self.lock.release()

def ActiveThread():
    '''
    起動中のサブスレッドを取得
    '''
    active_thread = []
    for tmp_thread in threading.enumerate():
        active_thread.append(tmp_thread.getName())
    
    return active_thread