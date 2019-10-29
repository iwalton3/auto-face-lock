import logging
import os
import threading
import time

from conf import settings

log = logging.getLogger("blank")

class AutoBlank(threading.Thread):
    def __init__(self):
        self.is_blank = False
        threading.Thread.__init__(self)
    
    def run(self):
        while True:
            if self.is_blank:
                os.system(settings.blank_cmd)
            time.sleep(settings.blank_interval)
    
    def blank(self):
        self.is_blank = True
        os.system(settings.blank_cmd)
    
    def unblank(self):
        self.is_blank = False
        os.system(settings.unblank_cmd)

