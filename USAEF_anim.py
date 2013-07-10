"""
Script for animating the epidemic at USAEF 2010 
"""

import TreeViz as tv
import networkx as nx
import os
import random 


random.seed(12345)

gephi_layout_script = "gephi-toolkit-0.7.2014-all/gephi-toolkit-demos/gephi_yifanhu_multi_layout/dist/gephi_yifanhu_multi_layout.jar"


usaef = nx.DiGraph()
f = open("USAEF/EpiData.csv",'r')
header = f.readline()
max_day = 0
for l in f.readlines():
    l = l.rstrip("\n")
    l = l.rstrip("\r")
    d = l.split(", ")
    
    usaef.add_edge(str(d[1]),str(d[0]),day = float(d[3]))

#nx.write_gexf(usaef,"USAEF.gexf")

#tv.run_gephi_layout(gephi_layout_script,"USAEF",".gexf","_ml")

usaef = nx.read_gexf("USAEF_openord_huprop.gexf")

epicurve = ({ 0: [0,0,0], 1: [0,0,0]})

for i in range(1,42):
    curr_infs={}
    for a,b,d in usaef.edges_iter(data=True):
        if int(d["day"]) <= i:
            curr_infs.update({a:i})
    epicurve = tv.draw_graph(usaef,i,"USAEF/USAEF_graph",curr_infs,curr_infs,curr_infs,epicurve,fixed_size=25,colors=["black","black","black"])



