"""
Build social network with edges weighted by vulnerability for 
"""

import networkx as nx
import TreeViz as tv

g = nx.DiGraph()

tv.get_vulnerabilities(g,"baseline.EFO6")
##tv.add_socialnet_details(g,file,only_existing=True)


###  Weight edges by a particular attribute
for (src,dest,data) in g.edges_iter(data=True):
    g.edge[src][dest]["weight"] = data["vul"]

nx.write_gexf(g,"social_network_weighted_vul.gexf")
