import math
import random as rn
from collections import deque

T = 100
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
        if len(self._queue) > 0:
            return self._queue[0]
        else:
            return -1

    def set_head(self, z):
        self._queue[0] = z

    def pop_head(self):
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
        if len(node.get_queue()) == 0 or len(min_arr.get_queue()) == 0:
            continue
        if min_arr.get_head() > node.get_head():
                min_arr = node
    return min_arr

def is_busy(node, mode, sender):

    index = 0
    #get sender and node information
    node_packets = node.get_queue()
    sender_index = sender.get_index()
    sender_time = sender.get_head()
    index = 0

    prop_time = abs(sender_index - node.get_index()) * t_prop

    for packet in node_packets:
        #print('sender time: ', sender_time)
        #bus is busy, current node waits
        if(sender_time + prop_time < packet < sender_time + prop_time + t_tran):
            # print('-------------------------------------------------------busy')
            # inpersistent mode
            if mode == 1:
                node.inc_b_count(1)
                #busy counter exceeds 10, drop the packet, reset counters
                if node.get_b_count() > 10:
                    node.pop_head()
                    node.reset_b()
                    node.reset_c()
                else:
                    i = node.get_b_count()
                    t_wait = rn.uniform(0, (pow(2, i) - 1)) * t_p
                    #update the node packets with the wait time
                    #node.get_queue()[index] = sender_time + prop_time + t_tran + t_wait
                    node.get_queue()[index] += t_wait
            #persistent mode        
            else:
                node.get_queue()[index] = sender_time + prop_time + t_tran
        index += 1

def check_collision(node, sender):
    #get sender information
    sender_index = sender.get_index()
    sender_time = sender.get_head()
    #print('sender time:', sender_time)
    is_collision = 0

    prop_time = abs(sender_index - node.get_index()) * t_prop
    # check if the collision happens and handle collision
    # print('Node head: ', node.get_head(), ' Sender time: ', sender_time, ' tp:', abs(node.get_index() - sender_index) * t_prop)
    # print("Node index:", node.get_index(), "Sender index", sender_index, "propagation:", t_prop)
    # collision happens
    
    if node.get_head() < sender_time + prop_time:
        is_collision = 1
        handle_collision(node)
    
    return is_collision

def handle_collision(node):
    global trans_packets

    node.inc_c_count(1)
    trans_packets += 1
    # if the collision counter gets 10, drop the packet at current node
    if node.get_c_count() > 10:
        # print('i reached 10')
        node.pop_head()
        node.reset_c()
        node.reset_b()
    else:
        exp_backoff(node)

def exp_backoff(node):
    node_index = 0

    node_packets = node.get_queue()

    t_wait = rn.uniform(0, (pow(2, node.get_c_count()) - 1)) * t_p

    #update the node packets with the wait time
    for n_packet in node_packets:
        if n_packet < t_wait:
            node_packets[node_index] += t_wait
        node_index += 1
        

def main():
    N = [20, 40, 60, 80, 100]
    A = [7, 10, 20]
    mode = [0]# 0 for persisten, 1 for non-persistent
    global succ_packets
    global trans_packets

    for i in mode:
        print("----------In Persistent Mode----------") if i == 0 else print("----------In Non-persistent Mode----------")
        # if i == 0:
        #     f = open("persistent.csv", "w")
        # else:
        #     f = open("non_persistent.csv", "w")
        # f.write("A, N, Efficiency, throughput")
        
        for j in A:
            for k in N:
                succ_packets = 0
                trans_packets = 0
                
                print("The current A is: ", j, "The current N is: ", k)
                node_list = generate_node(k, j)
                # for node in node_list:
                #     node.print()
                sender_time = 0
                is_collision = 0

                #end loop if timed out or packets are run out
                while(sender_time <= T and sender_time != -1):
                    #update sender
                    sender = get_sender()
                    
                    for node in node_list:
                        if node.get_queue():
                            # Persistent mode
                            if is_collision == 1:
                                check_collision(node, sender)
                            else:
                                is_collision = check_collision(node, sender)
                            is_busy(node, i, sender)
                            
                    if is_collision == 1:
                        trans_packets += 1
                    else:
                        sender.pop_head()
                        succ_packets += 1
                        trans_packets += 1

                    sender_time = sender.get_head()
                
                efficiency = succ_packets / trans_packets
                throughput = (succ_packets / T) * t_tran

                # f.write("\n{}, {}, {}, {}".format(j, k, efficiency, throughput))
                print("transmitted: ", trans_packets, "succeed: ", succ_packets)
                print("The Efficiency is: ", efficiency, "The Throughput is: ", throughput, "Mbps" )
                print()
    # f.close

if __name__ == '__main__':
    main()