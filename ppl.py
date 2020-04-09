import sys
import time
import os
import networkx as nx
import random
#import pylab
import queue as Q
import json
import threading
import multiprocessing
import getopt

index_file_path = "ppl.idx"
max_length = 999999999

class PrunedLandmarkLabeling(object):
    def __init__(self, map_file_name = "", order_mode = 0, validation = False, is_multi_process = False):
        super(PrunedLandmarkLabeling, self).__init__()
        if (not validation):
            if (map_file_name != ""):
                self.graph = self.read_graph(map_file_name)
                if (is_multi_process):
                    # self.index = self.build_index_multi_thread(order_mode)
                    self.index = self.build_index_multi_process(order_mode)
                else:
                    self.index = self.build_index(order_mode)
            else:
                self.index = self.load_index(index_file_path)
        else:
            self.graph = self.read_graph(map_file_name)
            self.index = self.load_index(index_file_path)

    def write_index(self):
        f = open(index_file_path, 'w')
        # f.writelines(str(len(self.graph.nodes)) + "\n")
        # print("Index:")
        # for k in self.index:
        #     print(k)
        #     print(self.index[k])
        write_data = json.dumps(self.index)
        print("Index Size: %d Bytes" % len(write_data))
        f.write(write_data)
        f.write('\n')
        f.write(json.dumps(self.vertex_order))
        f.close()

    def read_graph(self, map_file_name):
        G = nx.DiGraph()
        f = open(map_file_name, 'r')
        data = f.readlines()
        f.close()
        for idx, lines in enumerate(data):
            if (idx < 2):
                continue
            src, dest, dist, is_one_way = lines.split(" ")
            G.add_weighted_edges_from([(src, dest, int(dist))])
            if (int(is_one_way) == 0):
                G.add_weighted_edges_from([(dest, src, int(dist))])

        # print("G.edges:")
        # print(G.edges())
        # print("G.nodes:")
        # print(G.nodes())
        # print("")
        return G

    def query(self, src, dest):
        #src_idx = self.index.get(src,None)
        #dest_idx = self.index.get(dest,None)
        #if src_idx and dest_idx:
        #    src_list = src_idx.get("backward",None)
        #    dest_list = dest_idx.get("forward",None)
        src_list = self.index[src]["backward"]
        dest_list = self.index[dest]["forward"]
        i = 0
        j = 0
        result = max_length
        while i < len(src_list) and j < len(dest_list):
            if (src_list[i][0] == dest_list[j][0] and result > src_list[i][1] + dest_list[j][1]):
                result = src_list[i][1] + dest_list[j][1]
            elif self.vertex_order[src_list[i][0]] > self.vertex_order[dest_list[j][0]]:
                i += 1
            else:
                j += 1
        #for (src, s_dist) in src_list:
        #    for (dest, d_dist) in dest_list:
        #        if (src == dest and result > s_dist + d_dist):
        #            result = s_dist + d_dist
        #print(src_list)
        #print(dest_list)
        return result

    def load_index(self, index_file_path):
        f = open(index_file_path, 'r')
        data = f.readlines()
        result = json.loads(data[0])
        self.vertex_order = json.loads(data[1])
        f.close()
        return result

    def gen_test_order(self):
        result = {}
        nNodes = len(self.graph.nodes())
        for idx, v in enumerate(self.graph.nodes()):
            result[v] = nNodes - idx
        # result['c'] = 6
        # result['d'] = 5
        # result['e'] = 4
        # result['f'] = 3
        # result['a'] = 2
        # result['b'] = 1
        return result

    def gen_random_order(self):
        result = {}
        nNodes = len(self.graph.nodes())
        # print(list(self.graph.nodes()))
        nodes_list = list(self.graph.nodes())
        random.shuffle(nodes_list)
        # print(nodes_list)
        for idx, v in enumerate(nodes_list):
            result[v] = nNodes - idx
        return result

    def gen_degree_base_order(self):
        result = {}
        #print(self.graph.nodes())
        nNodes = len(self.graph.nodes())
        nodes_list = list(sorted(self.graph.degree, key=lambda x: x[1], reverse=True))
        #print(list(sorted(self.graph.degree, key=lambda x: x[1], reverse=True)))
        for idx, v in enumerate(nodes_list):
            result[v[0]] = nNodes - idx
        #    print(v[0], result[v[0]])
        return result

    def gen_betweeness_base_order(self):
        result = {}
        nNodes = len(self.graph.nodes())
        nodes_list = nx.betweenness_centrality(self.graph, weight="weight")
        nodes_list = list(sorted(nodes_list.items(), key=lambda item:item[1], reverse = True))
        # print(nodes_list)
        for idx, v in enumerate(nodes_list):
            result[v[0]] = nNodes - idx
        # print(result)
        return result

    def gen_order(self, mode = 0):
        if (mode == 0):
            self.vertex_order = self.gen_test_order()
        if (mode == 1):
            self.vertex_order = self.gen_random_order()
        if (mode == 2):
            self.vertex_order = self.gen_degree_base_order()
        if (mode == 3):
            self.vertex_order = self.gen_betweeness_base_order()
        self.vertex_order = {k: v for k, v in sorted(self.vertex_order.items(), key=lambda item: -item[1])}
        # print("vertex order: ")
        # print(self.vertex_order)
        # print("")

    def need_to_expand(self, src, dest, dist = -1):
        # print("nx: %s -> %s: %d" % (src, dest, v))
        our_result = self.query(src, dest)
        v = dist
        # print("pll: %s -> %s: %d" % (src, dest, our_result))
        if (our_result <= v):
            return False
        return True

    def build_index(self, order_mode = 0):
        self.gen_order(order_mode)
        self.index = {}
        has_process = {}
        pq = Q.PriorityQueue()
        for v in self.graph.nodes():
            self.index[v] = {"backward": [], "forward": []}
            has_process[v] = False

        i = 0
        nNode = len(self.graph.nodes())
        for order_item in self.vertex_order.items():
            cur_node = order_item[0]
            i += 1
            # Calculate Forward
            print("Caculating %s (%d/%d) forward ... " % (cur_node, i, nNode))
            pq.put((0, cur_node))
            for k in has_process:
                has_process[k] = False
            while (not pq.empty()):
                cur_dist, src = pq.get()
                # print("Pop: (%s %d)"%(src,cur_dist))
                if (has_process[src] or self.vertex_order[cur_node] < self.vertex_order[src] or not self.need_to_expand(cur_node, src, cur_dist)):
                    has_process[src] = True
                    continue
                has_process[src] = True
                self.index[src]["forward"].append((cur_node, cur_dist))
                edges = self.graph.out_edges(src)
                # print(src)
                # print(edges)
                for _, dest in edges:
                    weight = self.graph.get_edge_data(src, dest)['weight']
                    if (has_process[dest]):
                        continue
                    pq.put((cur_dist + weight, dest))
                    # print("Push: (%s, %d)"%(dest, cur_dist + weight))

            # Calculate Backward
            print("Caculating %s (%d/%d) backward..." % (cur_node, i, nNode))
            pq.put((0, cur_node))
            for k in has_process:
                has_process[k] = False
            while (not pq.empty()):
                cur_dist, src = pq.get()
                # print("Pop: (%s %d)"%(src,cur_dist))
                if (has_process[src] or self.vertex_order[cur_node] < self.vertex_order[src] or not self.need_to_expand(src, cur_node, cur_dist)):
                    continue
                has_process[src] = True
                self.index[src]["backward"].append((cur_node, cur_dist))
                edges = self.graph.in_edges(src)
                # print(src)
                # print(edges)
                for dest, _ in edges:
                    weight = self.graph.get_edge_data(dest, src)['weight']
                    if (has_process[dest]):
                        continue
                    pq.put((cur_dist + weight, dest))
                    # print("Push: (%s, %d)"%(dest, cur_dist + weight))

            # print("")
        self.write_index()
        return self.index

    def build_forward_index(self, cur_node):
        has_process = {}
        pq = Q.PriorityQueue()
        pq.put((0, cur_node))
        for k in self.graph.nodes():
            has_process[k] = False
        while (not pq.empty()):
            cur_dist, src = pq.get()
            # print("[Forward] Pop: (%s %d)"%(src,cur_dist))
            if (has_process[src] or self.vertex_order[cur_node] < self.vertex_order[src] or not self.need_to_expand(cur_node, src, cur_dist)):
                has_process[src] = True
                continue
            has_process[src] = True
            self.index[src]["forward"].append((cur_node, cur_dist))
            edges = self.graph.out_edges(src)
            # print(src)
            # print(edges)
            for _, dest in edges:
                weight = self.graph.get_edge_data(src, dest)['weight']
                if (has_process[dest]):
                    continue
                pq.put((cur_dist + weight, dest))
                # print("[Forward] Push: (%s, %d)"%(dest, cur_dist + weight))

    def build_backward_index(self, cur_node):
        has_process = {}
        pq = Q.PriorityQueue()
        pq.put((0, cur_node))
        for k in self.graph.nodes():
            has_process[k] = False
        while (not pq.empty()):
            cur_dist, src = pq.get()
            # print("[Backward] Pop: (%s %d)"%(src,cur_dist))
            if (has_process[src] or self.vertex_order[cur_node] < self.vertex_order[src] or not self.need_to_expand(src, cur_node, cur_dist)):
                continue
            has_process[src] = True
            self.index[src]["backward"].append((cur_node, cur_dist))
            edges = self.graph.in_edges(src)
            # print(src)
            # print(edges)
            for dest, _ in edges:
                weight = self.graph.get_edge_data(dest, src)['weight']
                if (has_process[dest]):
                    continue
                pq.put((cur_dist + weight, dest))
                # print("[Backward] Push: (%s, %d)"%(dest, cur_dist + weight))

    def build_index_multi_thread(self, order_mode = 0):
        self.gen_order(order_mode)
        self.index = {}
        for v in self.graph.nodes():
            self.index[v] = {"backward": [], "forward": []}

        nNode = len(self.graph.nodes())
        for i, order_item in enumerate(self.vertex_order.items()):
            cur_node = order_item[0]
            print("Caculating %s (%d/%d)... " % (cur_node, i, nNode))   
            forward_thread = threading.Thread(target=self.build_forward_index, args=(cur_node,))
            backward_thread = threading.Thread(target=self.build_backward_index, args=(cur_node,))
            forward_thread.start()
            backward_thread.start()
            forward_thread.join()
            backward_thread.join()
            # print("")
        self.write_index()
        return self.index

    def build_index_multi_process(self, order_mode = 0):
        self.gen_order(order_mode)
        self.index = {}
        for v in self.graph.nodes():
            self.index[v] = {"backward": [], "forward": []}

        nNode = len(self.graph.nodes())
        for i, order_item in enumerate(self.vertex_order.items()):
            cur_node = order_item[0]
            print("Caculating %s (%d/%d)... " % (cur_node, i, nNode))
            forward_process = multiprocessing.Process(target=self.build_forward_index, args=(cur_node,))
            backward_process = multiprocessing.Process(target=self.build_backward_index, args=(cur_node,))
            forward_process.start()
            backward_process.start()
            forward_process.join()
            backward_process.join()
            # print("")
        self.write_index()
        return self.index
    
    def validation(self, times = 10):
        node_list = list(self.graph.nodes())
        nx_times = 0.0
        pll_times = 0.0
        pass_cases = 0
        # print(node_list)
        for _ in range(times):
            src = random.choice(node_list)
            dest = random.choice(node_list)
            print("Testing %s -> %s:" % (src, dest))
            start_time = time.time()
            try:
                nx_result = nx.shortest_path_length(self.graph, source=src, target=dest, weight="weight")
            except:
                nx_result = max_length
            interval_time = time.time()
            my_result = self.query(src, dest)
            end_time = time.time()
            print("nx: %d, time: %f" % (nx_result, interval_time - start_time))
            print("ppl: %d, time: %f" % (my_result, end_time - interval_time))
            nx_times += interval_time - start_time
            pll_times += end_time - interval_time
            if (my_result == nx_result):
                pass_cases += 1

        print("Total Test Times: %d" % times)
        print("Networkx Average Time: %f" % (nx_times / times))
        print("PLL Average Time: %f" % (pll_times / times))
        print("Pass Cases: %d/%d" % (pass_cases, times))
        return 0

def usage(argv = []):
    print("Usage: python pll.py [ build | query | test ]")

def build(argv):
    map_file_name = ""
    order_mode = 0
    is_multi_process = False
    help_msg = "python pll.py build -i [input_file] -o [order_mode] -m(use multi-process)"
    try:
        options, args = getopt.getopt(argv, "hi:o:m", ["help", "input=", "order_mode=", "multi_process"])
        for name, value in options:
            if name in ("-h", "--help"):
                print(help_msg)
                return 2
            if name in ("-i", "--input"):
                map_file_name = value
            if name in ("-o", "--order_mode"):
                order_mode = int(value)
            if name in ("-m", "--multi_process"):
                is_multi_process = True
    except:
        print(help_msg)
        return 2
    
    if (map_file_name == ""):
        print(help_msg)
        return 2

    start_time = time.time()
    ppl = PrunedLandmarkLabeling(map_file_name, order_mode, False, is_multi_process)
    print("Total time: %f" % (time.time() - start_time))
    return 0

def query(argv):
    help_msg = "python pll.py query -s [src_vectex] -t [target_vectex]"
    src_vertex = ""
    target_vertex = ""
    try:
        options, args = getopt.getopt(argv, "hs:t:", ["help", "src=", "target="])
        for name, value in options:
            if name in ("-h", "--help"):
                print(help_msg)
                return 2
            if name in ("-s", "--src"):
                src_vertex = value
            if name in ("-t", "--target"):
                target_vertex = value
    except:
        print(help_msg)
        return 2

    start_time = time.time()
    ppl = PrunedLandmarkLabeling()
    print(ppl.query(src_vertex, target_vertex))
    print("Total time: %f" % (time.time() - start_time))
    return 0


def test(argv):
    help_msg = "python pll.py test -t [times] -m [map_file]"
    times = 10
    map_file_name = ""
    try:
        options, args = getopt.getopt(argv, "ht:m:", ["help", "times=", "map_file="])
        for name, value in options:
            if name in ("-h", "--help"):
                print(help_msg)
                return 2
            if name in ("-t", "--target"):
                times = int(value)
            if name in ("-m", "--map_file"):
                map_file_name = value
    except:
        print(help_msg)
        return 2

    if (map_file_name == ""):
        print(help_msg)
        return 2

    ppl = PrunedLandmarkLabeling(map_file_name, 0, True)
    ppl.validation(times)
    return 0

action = {
        "build": build,
        "query": query,
        "test": test,
        "help": usage
    }

if __name__ == "__main__":
    if (len(sys.argv) < 2):
        usage()
        sys.exit(2)
    
    action = {
        "build": build,
        "query": query,
        "test": test,
        "help": usage
    }

    sys.exit(action.get(sys.argv[1], usage)(sys.argv[2:]))


    

