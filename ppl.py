import sys
import time
import os

index_file_path = "ppl.idx"

class PrunedLandmarkLabeling(object):
    def __init__(self, map_file_name = "", order_mode = 0):
        super(PrunedLandmarkLabeling, self).__init__()
        if (map_file_name != ""):
            self.graph = self.read_graph(map_file_name)
            self.index = self.build_index(map_file_name, order_mode)
        else:
            self.index = self.load_index(index_file_path)

    def query(self, src, dest):
        return 0

    def load_index(self):
        return []

    def gen_random_order(self):
        return []

    def gen_degree_base_order(self):
        return []

    def gen_order(self, mode = 0):
        if (mode == 0):
            self.vertex_order = gen_random_order()
        if (mode == 1):
            self.vertex_order = gen_degree_base_order()

    def build_index(self, map_file_name, order_mode):
        return []


if __name__ == "__main__":
    if (len(sys.argv) < 2 or not sys.argv[1] in ("build", "query")):
        print("Usage: python ppl.py [ build | query ]")
        sys.exit(2)
    
    if (sys.argv[1] == "build"):
        if (len(sys.argv) < 4):
            print("Usage: python ppl.py build [map_file_name] [order_mode]")
            sys.exit(2)

        start_time = time.time()
        ppl = PrunedLandmarkLabeling(sys.argv[2], sys.argv[3])      
        print("Total time: %f" % (time.time() - start_time))
    else:
        if (len(sys.argv) < 4):
            print("Usage: python ppl.py query [src_vertex] [dest_vertex]")
            sys.exit(2)
        start_time = time.time()
        ppl = PrunedLandmarkLabeling()
        print(ppl.query(sys.argv[2], sys.argv[3]))
        print("Total time: %f" % (time.time() - start_time))



    

