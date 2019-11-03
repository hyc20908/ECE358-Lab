import math
import random as rn
from collections import deque

T = 10
D = 10
C = 300000000
S = (2 / 3) * C
R = 1000000
L = 1500
t_p = 512 / R
t_prop = D / S
t_tran = L / R
max_collision = 10
trans_packets = 0
succ_packets = 0
node_list = []

class Node(object):
    
    def __init__(self, index, c_count, b_count, queue = deque()):
        self._index = index
        self._c_count = c_count
        self._b_count = b_count
        self._queue = queue
        

    @staticmethod
    def destroy(self):
        self._c_count = 0
        self._b_count = 0
        self._queue = deque()

    def reset_c(self):
        self._c_count = 0

    def reset_b(self):
        self._b_count = 0

    def get_queue(self):
        return self._queue

    def get_c_count(self):
        return self._c_count

    def get_b_count(self):
        return self._b_count

    def inc_c_count(self, x): 
        self._c_count += x 

    def inc_b_count(self, y): 
        self._b_count += y 

    def get_index(self):
        return self._index

    def get_head(self):
        return self._queue[0]

    def set_head(self, z):
        self._queue[0] = z

    def pop(self):
        self._queue.popleft()

    def print(self):
        print("The node index is:")
        print(self._index)
        print()
        print("The collision counter is:")
        print(self._c_count)
        print()
        print("The bus busy counter is:")
        print(self._b_count)
        print()
        print("The queue of the current node is:")
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
    global node_list
    node_list = []
    for i in range(0, node_num):
        node_list.append(Node(i, 0, 0, generate_arrival(avg_num)))
    return node_list

def get_sender():
    min_arr = node_list[0]
    for node in node_list:
        if min_arr.get_head() > node.get_head():
            min_arr = node
    return min_arr

def is_busy(node, mode):
    #get sender information
    sender = get_sender()
    sender_index = sender.get_index()
    sender_time = sender.get_head()

    prop_time = abs(sender_index - node.get_index()) * t_prop
    
    #bus is busy, current node waits
    for packet in node.get_queue():
        if(sender_time + prop_time < packet < sender_time + prop_time + t_tran):
            if mode == 1:
                node.inc_b_count(1)
                if node.get_b_count > 10:
                    node.pop()
                    node.reset_b()
                else:
                    i = node.get_c_count()
                    t_wait = rn.uniform(0, (pow(2, i) - 1)) * t_p

                    #update the node packets with the wait time
                    packet = packet + t_wait
                    
            else:
                packet = sender_time + prop_time + t_tran

def check_collision(node):
    sender = get_sender()
    sender_index = sender.get_index()
    sender_time = sender.get_head()

    is_collision = 0
    # check if the collision happens and handle collision
    if node.get_head() < sender_time + (abs(node.get_index() - sender_index) * t_prop):
        node.inc_c_count(1)
        is_collision = 1
        trans_packets += 1
        handle_collision(node)
    
    return is_collision

def handle_collision(node):
    # if the collision counter gets 10, drop the packet at current node
    if node.get_c_count > 10:
        node.pop()
        node.reset_c()
    else:
        exp_backoff(node)

def exp_backoff(node):
    i = node.get_c_count()
    t_wait = rn.uniform(0, (pow(2, i) - 1)) * t_p
    #update the node packets with the wait time

    for packet in node.get_queue():
        if packet.get_head() < t_wait:
            packet = t_wait

def main():
    N = [20, 40, 60, 80, 100]
    A = [7, 10, 20]
    global succ_packets

    node_list = generate_node(5, 7)
    # for node in node_list:
    #     node.print()
    #     print()

    sender = get_sender()
    sender_time = sender.get_head()

    while(sender_time <= T):

        for node in node_list:
            if(node.get_queue()):
                # Persistent mode
                is_busy(node, 0)
                is_collision = check_collision(node)

        if is_collision == 1:
            handle_collision(sender)
            sender.inc_c_count(1)
        else:
            succ_packets += 1
    
    efficiency = succ_packets / trans_packets
    throughput = (L * succ_packets) / ((sender_time + L / R) * pow(10, -6))

    print("The Efficiency is: ", efficiency)
    print("The Throughput is: ", throughput, "Mbps" )




if __name__ == '__main__':
    main()