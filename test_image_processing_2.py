#https://stackoverflow.com/questions/18204782/runtimeerror-on-windows-trying-python-multiprocessing

#sharing complex object between processes:
#https://stackoverflow.com/questions/3671666/sharing-a-complex-object-between-processes

#from threading import Thread, Event
from time import sleep
from time import time
import datetime
import random

from multiprocessing import Process, Manager, Event
from multiprocessing.managers import BaseManager

class PuttLog(object):
    def __init__(self):
        self.var = [0]

    def set(self, value):
        self.var.append(value)
        #self.var = value

    def get(self):
        return self.var

    def getlast(self):
        last = len(self.var) - 1
        return self.var[last]

def print_dict(dict):
    for keys,values in dict.items():
        print(keys)
        print(values)


def add_value(obj, event):
    #i = iterator
    rand_time = 0
    while True:
        #obj.set(str(i) + identifier)
        #i += iterator
        if event.is_set():
            break
        rand_time = 100*random.uniform(0,1)
        remainder =  rand_time % 5
        sleep_time = float(5 + remainder)
        #print('sleep time: ' + str(sleep_time))
        sleep(sleep_time)
        
        distance = float(8 + remainder)
        timestamp = datetime.datetime.now()
        outcome = 'miss'

        rand_outcome = random.uniform(0,1)
        #print('rand_outcome: ' + str(rand_outcome))
        if (rand_outcome > .40):
            outcome = 'make'

        last_putt = {}
        last_putt['timestamp'] = timestamp
        last_putt['distance'] = distance
        last_putt['outcome'] = outcome

        print_dict(last_putt)
        obj.set(last_putt)
        
                
        
    #print('Stop printing')

if __name__ == '__main__':
    event = Event() #global variable to signal end of processing
    BaseManager.register('PuttLog', PuttLog)
    manager = BaseManager()
    manager.start()
    puttlog = manager.PuttLog()

    jobs = []

    process1 = Process(target=add_value, args=[puttlog, event])
    #process2 = Process(target=add_value, args=[inst, 10, 'second', event])

    jobs.append(process1)
    #jobs.append(process2)

    for j in jobs:
        j.start()


    # t0 = time()
    # while time()-t0 < 20:
    #     try:
    #         sleep(5)
    #         last_putt = puttlog.getlast()

    #         print('last putt: ')
    #         print_dict(last_putt)

    #     except KeyboardInterrupt:
    #         event.set()
    #         break
    # event.set()

    for j in jobs:
        j.join()

    #print(inst)
    #array = puttlog.get()
    #for x in array:
        #print_dict(x)
    #print(puttlog.get())
