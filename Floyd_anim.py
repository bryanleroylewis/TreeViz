"""
Script for animating the pertussis epidemic in Floyd
"""

import TreeViz as tv
import networkx as nx
import matplotlib.pyplot as plt
import os
import random
import time
import datetime


epicurve = ({ 0: [0,0,0]})
curr_count = 0
curr_incub = {}
curr_symp = {}
curr_recover = {}
np = {}
shape = []

layout = "gexf"
g = nx.read_gexf("Floyd_pertussis/Floyd_outbreak_fa2.gexf")
outstem = "Floyd_pertussis/movie/Floyd_fa_anim_"+ layout
min_date = datetime.datetime(*time.strptime("Feb 16 2011","%b %d %Y")[0:6])



######

if layout == "gexf":
    for n in g.nodes():                
        x = g.node[n]["viz"]["position"]["x"]
        y = g.node[n]["viz"]["position"]["y"]
        
        curr_pos = [x,y]
        np.update({n:curr_pos})
        
        shape.append(random.choice("so^>v<dph8"))
        
        
    ###  Choose duration to animate
    for day in range(1,60):
        inf_list = []
        
        date_add = datetime.timedelta(days=day)
        date = min_date + date_add
        
        
        inf_list = []
        non_inf_list = g.nodes()
        
        for n in g.nodes():
            if "onset_day" in g.node[n] and g.node[n]["onset_day"] < day:
                curr_count = curr_count + 1
                curr_symp.update({n:100})
                inf_list.append(n)
                non_inf_list.remove(n)
                        
        for n in inf_list:
            ####  Draw infected nodes in red
            if g.node[n]["relation"].find("student") > -1:
                nx.draw_networkx_nodes(g, pos=np, nodelist = [n], node_size=35, node_color = "red", node_shape='o', with_labels=True, linewidths=0,edgecolors="none")
            elif g.node[n]["relation"].find("teacher") > -1:
                nx.draw_networkx_nodes(g,pos=np, nodelist = [n], node_size=35, node_color = "red", node_shape="s", with_labels=True, linewidths=0, edgecolors="none")
            elif g.node[n]["relation"].find("parent") > -1:
                nx.draw_networkx_nodes(g,pos=np, nodelist = [n], node_size=35, node_color = "red", node_shape="^", with_labels=True,linewidths=0,edgecolors="none")
            elif g.node[n]["relation"].find("sibling") > -1:
                nx.draw_networkx_nodes(g, pos=np, nodelist = [n], node_size=35, node_color = "red", node_shape="v", with_labels=True,linewidths=0,edgecolors="none")
            else:
                nx.draw_networkx_nodes(g,pos=np, nodelist = [n], node_size=35, node_color = "red", node_shape="+", with_labels=True, linewidths=0, edgecolors="none")
                        
        for n in non_inf_list:
            ####  Draw infected nodes in red
            if g.node[n]["relation"].find("student") > -1:
                nx.draw_networkx_nodes(g, pos=np, nodelist = [n], node_size=25, node_color = "grey", node_shape='o', with_labels=True, linewidths=0, edgecolors="none")
            elif g.node[n]["relation"].find("teacher") > -1:
                nx.draw_networkx_nodes(g, pos=np, nodelist = [n], node_size=25, node_color = "grey", node_shape="s", with_labels=True, linewidths=0, edgecolors="none")
            elif g.node[n]["relation"].find("parent") > -1:
                nx.draw_networkx_nodes(g, pos=np, nodelist = [n], node_size=25, node_color = "grey", node_shape="^", with_labels=True, linewidths=0, edgecolors="none")
            elif g.node[n]["relation"].find("sibling") > -1:
                nx.draw_networkx_nodes(g, pos=np, nodelist = [n], node_size=25, node_color = "grey", node_shape="v", with_labels=True, linewidths=0, edgecolors="none")
            else:
                nx.draw_networkx_nodes(g, pos=np, nodelist = [n], node_size=25, node_color = "grey", node_shape="d", with_labels=True, linewidths=0, edgecolors="none")

        ###  Draw grey edges first
        nx.draw_networkx_edges(g, pos=np, edgelist = g.edges(), width=1, alpha=0.45,arrows=False)
        
        nx.draw_networkx_edges(g, pos=np, edgelist = (g.subgraph(inf_list)).edges(), width=1, edge_color="red", alpha=0.55, arrows=False)

        


        
        ####  Labelling the plot
        plt.figtext(0.02,0.97,s = date.strftime("%b %d") , size = 'large')
        plt.axis('off')
        plt.savefig(outstem+"_day"+str(day)+".png",dpi=150)
    
        print "Plotted day:" + date.strftime("%b %d") 
        plt.close()


if layout == "dynamic":
    ###  Choose duration to animate
    for day in range(1,60):
        inf_list = []
        
        date_add = datetime.timedelta(days=day)
        date = min_date + date_add
        
        for n in g.nodes():
            if "onset_day" in g.node[n] and g.node[n]["onset_day"] < day:
                curr_count = curr_count + 1
                curr_symp.update({n:100})
                inf_list.append(n)
            
            
        np = nx.spectral_layout(g.subgraph(inf_list))
        
        nx.draw_networkx_nodes(g.subgraph(inf_list),pos=np,nodelist = inf_list,node_size=35,node_color = "red", with_labels=False,linewidths=0,edgecolors="none")
        
        nx.draw_networkx_edges(g.subgraph(inf_list), pos=np, edgelist = (g.subgraph(inf_list)).edges(), width=1, edge_color="red", alpha=0.55, arrows=False)
        
        ####  Labelling the plot
        plt.figtext(0.02,0.97,s = date.strftime("%b %d") , size = 'large')
        plt.axis('off')
        plt.savefig(outstem+"_day"+str(day)+".png",dpi=300)
    
        print "Plotted day:" + date.strftime("%b %d") 
        plt.close()

