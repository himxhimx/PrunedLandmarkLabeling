import osmnx as ox
import matplotlib.cm as cm
import networkx as nx
import numpy as np
import pandas as pd

ox.config(log_console=True, use_cache=True)

place = 'Macau'
gdf = ox.gdf_from_place(place)
area = ox.project_gdf(gdf).unary_union.area
G = ox.graph_from_place(place, network_type='drive_service')
print(len(G.nodes), len(G.edges))
edges = ox.graph_to_gdfs(G, nodes=False, edges=True)

f= open("macau.map","w")

f.write("d\n%d %d\n" % (len(G.nodes), len(G.edges)))
        
D={}
ID={}
for index, row in edges.iterrows(): 
    if row["u"] not in D:
        ID[len(D)]=row["u"]
        D[row["u"]]=len(D)

    if row["v"] not in D:
        ID[len(D)]=row["v"]
        D[row["v"]]=len(D)

    #print(not row["oneway"])
    if row["oneway"]:
        f.write("%d %d %d %d\n" % (D[row["u"]], D[row["v"]], row["length"]*1000, 1))
    else:
        f.write("%d %d %d %d\n" % (D[row["u"]], D[row["v"]], row["length"]*1000, 0))
        
f.close()

# find the route between these nodes then plot it
import random
n=len(G.nodes)
#origin_node = ox.get_nearest_node(G, location_point)
#destination_node = list(G.nodes())[-1]
import time
start_time = time.time()
#print(ox.stats.basic_stats(G))
for i in range(10):
    origin_node=list(G.nodes())[random.randrange(n)]
    destination_node=list(G.nodes())[random.randrange(n)]
    route = nx.shortest_path(G, origin_node, destination_node)
    #print(route)

t = (time.time() - start_time)/10
print("--- %s seconds per query---" % t)
#fig, ax = ox.plot_graph_route(G, route)

# project the network to UTM (zone calculated automatically) then plot the network/route again
G_proj = ox.project_graph(G)
fig, ax = ox.plot_graph_route(G_proj, route)