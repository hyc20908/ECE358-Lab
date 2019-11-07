import math
import random as rn
from collections import deque

T = 30
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
is_collision = 0
master_packet = 88
insta = 100

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
        if len(self._queue) > 0:
            return self._queue[0]
        else:
            return -1

    def set_head(self, z):
        self._queue[0] = z

    def pop_head(self):
        self._queue.popleft()

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
        if len(node.get_queue()) == 0 or len(min_arr.get_queue()) == 0:
            continue
        if min_arr.get_head() > node.get_head():
            min_arr = node
    return min_arr

def is_busy(node, mode, sender, max_index):

    #get sender and node information
    sender_index = sender.get_index()
    sender_time = sender.get_head()

    prop_time = abs(sender_index - node.get_index()) * t_prop
    delay_time = abs(sender_index - max_index) * t_prop

    #bus is busy, current node waits
    if(sender_time + prop_time < node.get_head() < sender_time + delay_time + t_tran):
        # inpersistent mode
        if mode == 1:
            node.inc_b_count(1)
            b_counter = node.get_b_count()
            #busy counter exceeds 10, drop the packet, reset counters
            if b_counter > 10:
                node.pop_head()
                node.reset_b()
                node.reset_c()
            else:
                t_wait = (rn.uniform(0, (pow(2, b_counter) - 1)) * t_p) / 1000000
                #update the node packets with the wait time
                node.get_queue()[0] = sender_time + delay_time + t_tran + t_wait
                
        #persistent mode
        else:
            node.get_queue()[0] = sender_time + delay_time + t_tran

def check_collision(node, sender, max_index):
    global is_collision

    #get sender information
    sender_index = sender.get_index()
    sender_time = sender.get_head()

    prop_time = abs(sender_index - node.get_index()) * t_prop

    # hit collision
    if node.get_head() < sender_time + prop_time:
        is_collision = 1
        handle_collision(node, max_index, sender_index, sender_time)
    
    #return is_collision

def handle_collision(node, max_index, sender_index, sender_time):
    global trans_packets

    node.inc_c_count(1)
    trans_packets += 1
    # if the collision counter gets 10, drop the packet at current node
    if node.get_c_count() > 10:
        node.pop_head()
        node.reset_c()
        node.reset_b()
    else:
        exp_backoff(node, max_index, sender_index, sender_time)

def exp_backoff(node, max_index, sender_index, sender_time):
    node_index = 0
    node_packets = node.get_queue()

    t_wait = rn.uniform(0, (pow(2, node.get_c_count()) - 1)) * t_p

    #update the node packets with the wait time
    for n_packet in node_packets:
        if n_packet < t_wait:
            node_packets[node_index] = sender_time + abs(sender_index - max_index) * t_prop + t_wait
        node_index += 1

def main():
    N = [20, 40, 60, 80, 100]
    A = [7, 10, 20]
    mode = [0, 1]# 0 for persisten, 1 for non-persistent
    global succ_packets
    global trans_packets
    global is_collision

    for i in mode:
        print("----------In Persistent Mode----------") if i == 0 else print("----------In Non-persistent Mode----------")
        if i == 0:
            f = open("persistent.csv", "w")
        else:
            f = open("non_persistent.csv", "w")
        f.write("A, N, Efficiency, throughput")
        
        for j in A:
            for k in N:
                succ_packets = 0
                trans_packets = 0
                is_collision = 0
                simu_time = 0
                m = master_packet/insta
                
                node_list = generate_node(k, j)
                
                sender = get_sender()
                sender_time = sender.get_head()
                sender_index = sender.get_index()
                max_index = sender_index
                
                #end loop if timed out or packets are run out
                while(simu_time < T and sender_time != -1):
                    #reset collision counter and update sender
                    is_collision = 0
                    
                    for node in node_list:
                        if(abs(sender_index - node.get_index()) > abs(max_index - node.get_index())):
                            max_index = abs(sender_index - node.get_index())

                    for node in node_list:
                        if node.get_queue():
                            check_collision(node, sender, max_index)
                            is_busy(node, i, sender, max_index)

                    # no collision, successul packets increment by 1      
                    if is_collision == 0:
                        sender.pop_head()
                        succ_packets += 1

                    max_time = sender_time + max_index * t_prop
                    if (simu_time < max_time):
                        simu_time = max_time

                    sender = get_sender()
                    sender_time = sender.get_head()
                    sender_index = sender.get_index()

                total_packets = trans_packets + succ_packets*m

                efficiency = succ_packets / total_packets
                throughput = (succ_packets / T) * t_tran

                f.write("\n{}, {}, {}, {}".format(j, k, efficiency, throughput))
                print(j, k, " Efficiency: ", efficiency, "Throughput: ", throughput, "Mbps" )
    f.close

if __name__ == '__main__':
    main()