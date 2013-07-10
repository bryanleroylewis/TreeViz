import networkx as nx
import pydot

#g = nx.readwrite.gexf.read_gexf("baseline98_anim.gexf")
g = nx.readwrite.graphml.read_graphml("baseline98_anim.graphml")

print "Read in graph with nodes: "+str(len(g.nodes()))

##  For specifying a subgraph
layout_nodes = []
for a,b,d in g.edges_iter(data=True):
    if int(d["day"]) < 35:
        layout_nodes.append(a)
        layout_nodes.append(b)
print "Grabbed "+str(len(layout_nodes))+" nodes to subgraph and layout"

s = g.subgraph(layout_nodes)
nx.readwrite.graphml.write_graphml(s,"baseline98_under35.graphml")



pos = nx.pydot_layout(s,prog="sfdp")
        


