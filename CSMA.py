import math
import random as rn
from collections import deque

T = 10
D = 10
C = 300000000
S = (2 / 3) * C
R = 1000000
L = 1500
t_prop = D / S
t_tran = L / R
max_collision = 10

class Node(object):
    
    def __init__(self, index, count, queue = deque()):
        self._index = index
        self._count = count
        self._queue = queue
        

    @staticmethod
    def reset(self):
        self._count = 0
        self._queue = deque()

    def get_queue(self):
        return self._queue

    def get_count(self):
        return self._count

    def inc_count(self, x): 
        self._count += x 

    def get_index(self):
        return self._index

    def get_min_arrival(self):
        return self._queue[0]
    
    def print_queue(self):
        print(self._index)
        print()
        print(self._count)
        print()
        print(self._queue)
        print()

def generate_arrival(avg_num): 
    arrival_list = deque()
    count = 0
    arrival_time = 0
    while(1):       
        arr = - math.log(1 - rn.uniform(0, 1)) / avg_num
        if count == 0:
            arrival_time = arr
            arrival_list.append(arrival_time)
        else:
            arrival_time =  arr + arrival_list[count-1]
            if arrival_time >= T:
                break

            arrival_list.append(arrival_time)
        count += 1
    return arrival_list

def generate_node(node_num, avg_num):
    node_list = []
    for i in range(0, node_num):
        node_list.append(Node(i, 0, [generate_arrival(avg_num)]))
    return node_list

def sender(node_list):
    min_arr = list[0]
    for node in node_list:
        if min_arr > node.get_min_arrival():
            min_arr = node
    return min_arr

def collision(node_list):
    is_collision = 0
    sender = sender(node_list)
    sender_index = sender(node_list).get_index()
    sender_arr = sender.get_min_arrival()
    for node in node_list:
        if node.get_index() != sender_index:
            if node.get_min_arrival() < sender_arr + (abs(node.get_index() - sender_index) * t_prop):
                node.inc_count(1)
                is_collision  = 1
    return 0

def is_busy():

    return 0

def exp_backoff(k):
    return 0

def main():
    N = [20, 40, 60, 80, 100]
    A = [7, 10, 20]
    
    node_list = generate_node(5, 7)
    for node in node_list:
        node.print_queue()
        print()

if __name__ == '__main__':
    main()