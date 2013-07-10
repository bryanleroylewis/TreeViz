"""
    Tools for visualizing disease transmission through large graphs
"""

import networkx as nx
import pydot
import matplotlib.pyplot as plt
import sys
import locale
import optparse
import os
import string

# Usage message
usgmsg = "Usage: animate_epidemic_tree.py [options] infile.EFO6 demographic_file replicate outfile"

gephi_layout_script = "gephi-toolkit-0.7.2014-all/gephi-toolkit-demos/gephi_yifanhu_multi_layout/dist/gephi_yifanhu_multi_layout.jar"
layout_label = "_multilevel"
graph_format = ".gexf"

def add_disease_from_EFO(g,file,only_existing=True):
    """
    Add nodes and details about disease state duration from an EFO file to graph g.
    """

    f = open(file,'r')    
    nodes_update = 0
    nodes_list = g.nodes()
   
   
    for l in f.readlines():
 #       l = unicode(l, options.InputEncoding)
        l = l.rstrip("\n")
        if l.find('#') >= 0:
        	# Process headers
        	print l
        elif len(l.rsplit(" ")) == 3:
            # Process node
            
            id = int(l.rsplit(" ")[0])
            incub = int(l.rsplit(" ")[1])
            symp = int(l.rsplit(" ")[2])
            name = "n%s" % str(id)
            
            if id in nodes_list and only_existing:
                nodes_update = nodes_update + 1
                g.add_node(id, incubation = incub, symptomatic = symp)      
            
            
    f.close()
    print "Done parsing "+file+" total of "+str(nodes_update)+" nodes updated"
    
def add_socialnet_details(g,file):

    lines_parsed = 0
    f = open(file,'r')    
   
    for l in f.readlines():
        l = l.rstrip("\n")
        if l.find('#') >= 0:
        	# Process headers
        	print l
        else:
            lines_parsed = lines_parsed + 1
            # Process edges
            id1 = l.rsplit(" ")[0]
            id2 = l.rsplit(" ")[2]
            act = l.rsplit(" ")[3]
            dur = l.rsplit(" ")[4]
            g.add_node(id1)
            g.add_node(id2)
            g.add_edge(id1,id2,duration=dur,activity=act)

    f.close()
    print "Done parsing "+file+" total of "+str(lines_parsed)+" lines parsed"
    print "Graph has "+str(len(g.nodes()))+" nodes and "+str(len(g.edges()))+" edges"

def get_vulnerabilities(g,file,dz_details=True):
    """Add vulnerabilities from EFO file to graph g."""

    f = open(file,'r')

    for l in f.readlines():
        l = l.rstrip("\n")
        
        if l.find('#') >= 0:
        	# Process headers
        	print l
        elif len(l.rsplit(" ")) == 3 and dz_details:
            # Process node
            id = int(l.rsplit(" ")[0])
            incub = int(l.rsplit(" ")[1])
            symp = int(l.rsplit(" ")[2])
            g.add_node(id, incubation = incub, symptomatic = symp)      
        
        elif len(l.rsplit(" ")) == 4:
            # Process edge
            e_dest = int(l.rsplit(" ")[0])
            e_day = int(l.rsplit(" ")[2])
            e_src = int(l.rsplit(" ")[3])
            e_weight = 1
            
            if g.edge[e_src][e_dest].has_key("vul"):
                g.edge[e_src][e_dest]["vul"] = g.edge[e_src][e_dest]["vul"] + 1
            else:
                g.edge[e_src][e_dest]["vul"] = 1

            if g.node[e_dest].has_key("vul"):
                 g.node[e_dest]["vul"] = node[e_dest]["vul"] + 1
            else:
                node[e_dest]["vul"] = 1
            
    f.close()
    print "Done parsing "+file+" for replicate "+str(replicate)+" total of "+str(len(g.nodes()))+" nodes and "+str(len(g.edges()))+" edges"


def get_epidemic_graph(g,file,replicate,dz_details=True):
    """Add nodes and interactions in the EFO file to graph g."""

    f = open(file,'r')    

    for l in f.readlines():
        l = l.rstrip("\n")
        
        if l.find('#') >= 0:
        	# Process headers
        	print l
        elif len(l.rsplit(" ")) == 3 and dz_details:
            # Process node
            
            id = int(l.rsplit(" ")[0])
            incub = int(l.rsplit(" ")[1])
            symp = int(l.rsplit(" ")[2])
            #name = "n%s" % str(id)

            g.add_node(id, incubation = incub, symptomatic = symp)      

        
        elif (len(l.rsplit(" ")) == 4  and l.rsplit(" ")[1] == replicate):
            # Process edge
            e_dest = int(l.rsplit(" ")[0])
            e_iter = int(l.rsplit(" ")[1])
            e_day = int(l.rsplit(" ")[2])
            e_src = int(l.rsplit(" ")[3])
            e_weight = 1
            
            g.add_edge(e_src,e_dest,iter=e_iter)
            g.add_edge(e_src,e_dest,day=e_day)
#            g.add_edge(e_src,e_dest,weight=e_weight)
            
            node_start = int(e_day) + int(g.node[int(e_dest)]["incubation"])
            node_end = int(e_day) + int(g.node[int(e_dest)]["symptomatic"])
           # g.node[e_dest]["label"] = str(node_start)+"_"+str(node_end)
            
    f.close()
    print "Done parsing "+file+" for replicate "+str(replicate)+" total of "+str(len(g.nodes()))+" nodes and "+str(len(g.edges()))+" edges"


def parse_demographics(g,file):
    """Add demographic details to nodes"""

    demographics_added = 0
    graph_nodes = g.nodes()

    f = open(file,'r')
    
    header_line = f.readline()
    header_line = header_line.rstrip("\n")
    header = header_line.split("\t") 
    
    for l in f.readlines():
        l = l.rstrip("\n")
        d = l.split("\t")
    
        ###  define location of unique identifier, ie node id
        pid = int(d[0])
        
        if pid in graph_nodes:
            demographics_added = demographics_added + 1
            for c in range(1,len(header)-1):
                g.node[pid][header[c]] = d[c]
    
    f.close()

    print "Done parsing "+file+" and added demographics to "+str(demographics_added)+" nodes"
   
    return g


def get_nodes_for_plotting(g,day):
    """
        Grabs nodes involved in a transmission event on a specified day and returns info needed for netoworkx_draw functions
    """

    inf_nodes = []
    node_size = []
    node_colors = []
    node_position = {}
    
    size_scaler = 15

    for a,b,d in g.edges_iter(data=True):
        if int(d["day"]) == day:
        
            if a not in inf_nodes:
                inf_nodes.append(a)
                size = (g.node[a]["size"]*g.node[a]["size"]) / size_scaler
                node_size.append(size)
                curr_pos = [g.node[a]["x"],g.node[a]["y"]]
                node_position.update({a:curr_pos})
                #node_colors.append((g.node[a]["r"]/256, g.node[a]["g"]/256, g.node[a]["b"]/256))
                node_colors.append("red")

            if b not in inf_nodes:
                inf_nodes.append(b)
                size = (g.node[b]["size"]*g.node[b]["size"]) / size_scaler
                node_size.append(size)
                curr_pos = [g.node[b]["x"],g.node[b]["y"]]
                node_position.update({b:curr_pos})
#                node_colors.append((g.node[b]["r"]/256, g.node[b]["g"]/256, g.node[b]["b"]/256))
                node_colors.append("yellow")               

    return inf_nodes, node_size, node_position, node_colors

def make_plot(nx,plt,day,s,n,np,ns,nc):
        import matplotlib.figure as mf
        
        #fig = mf.Figure(figsize=(8,8))
        nx.draw_networkx_nodes(s,pos=np,node_size=ns,node_color = nc, with_labels=False,linewidths=0,edgecolors="none")
        nx.draw_networkx_edges(s,pos=np, width=1, alpha=0.65)

        
        plt.xlim(-8500,8500)
        plt.ylim(-8500,8500)
        plt.axis('off')
        
#        a=plt.axes([.82,.82,.15,.15])
        
#        plt.plot((1,2,3,4),(2,3,4,1))
#        plt.setp(a,xticks=[],yticks= [])
                
        plt.savefig("test_subplot"+str(day)+".png",dpi=150)

        print "Plotted day:" + str(day) 
        plt.close()

def get_new_infections(g,day):
    """ Extract all new infections for the given day
    returns a list of node ids """

    new_infs = []
    for a,b,d in g.edges_iter(data=True):
        if int(d["day"]) == day:
            new_infs.append(b)
    return new_infs

def update_incubating(g,day,new_infs,curr_incub):
    """Updates the list of nodes in the incubating state.  The dict curr_incub keeps   track of all incubating nodes and the day they will leave incubation.
    returns the current dict of incubating nodes and a list of node ids that will enter the symptomatic state """
    
    new_symptomatics = []
    for n in new_infs:
        end_day = day + int(g.node[n]["incubation"])
        curr_incub.update({n:end_day})
        
    for n in curr_incub.keys():
        if day > curr_incub[n]:
            del(curr_incub[n])
            new_symptomatics.append(n)
            
    return curr_incub,new_symptomatics

def update_symptomatic(g,day,new_symptomatics,curr_symps):
    """Updates the list of nodes in the symptomatic state.  The dict curr_symps keeps   track of all incubating nodes and the day they will leave symptomaticness.
    returns the current dict of symptomatic nodes and a list of node ids that will enter the recovered state """
    new_recover = []
    for n in new_symptomatics:
        end_day = day + int(g.node[n]["symptomatic"])
        curr_symps.update({n:end_day})
        
    for n in curr_symps.keys():
        if day > curr_symps[n]:
            del(curr_symps[n])
            new_recover.append(n)
            
    return curr_symps,new_recover

def update_recovered(day,new_recover,curr_recover):
    """ Updates the list of nodes in the recovered state.  The dict curr_recover keeps   track of all recovered nodes and the day they will leave recovered (to avoid clutter).
    returns the current dict of recovered nodes"""
    
    days_in_recovery = 10
    
    for n in new_recover:
        end_day = day + days_in_recovery
        curr_recover.update({n:end_day})
        
    for n in curr_recover.keys():
        if day > curr_recover[n]:
            del(curr_recover[n])
  
    return curr_recover

def draw_graph(g,day,outstem,curr_incub,curr_symp,curr_recover,epicurve):
    """Draws graph for prevalent infections (showing incubating and symptomatic states as different colors).  Needs maintained list of incubating and symptomatic infections.
    """


    size_scaler = 15
    ns = []
    np = {}
    
    E = len(curr_incub.keys()) 
    I = len(curr_symp.keys()) 
    R = len(curr_recover.keys())
    
    nodes_to_draw = curr_incub.keys() + curr_symp.keys() + curr_recover.keys()

    node_colors = ["yellow"]*E + ["red"]*I + ["grey"]*R
    
    ##  Get the positions and sizes of the nodes to draw
    for n in nodes_to_draw:
        size = (g.node[n]["size"]*g.node[n]["size"]) / size_scaler
        ns.append(size)
        curr_pos = [g.node[n]["x"],g.node[n]["y"]]
        np.update({n:curr_pos})
        
    s = g.subgraph(nodes_to_draw)
    nx.draw_networkx_nodes(s,pos=np,node_size=ns,node_color = node_colors, with_labels=False,linewidths=0,edgecolors="none")

    nx.draw_networkx_edges(s,pos=np, width=1, alpha=0.65)

        
    plt.xlim(-8500,8500)
    plt.ylim(-8500,8500)
    plt.axis('off')
    
    ####  Subplotting of the epicurve
    
    epicurve.update({day:[0,0,0]})
    epicurve[day][0] = E
    epicurve[day][1] = I
    epicurve[day][2] = R
    
    Es = []
    Is = []
    Rs = []

    days = range(min(epicurve.keys()),max(epicurve.keys()))

    for i in days:
        Es.append(epicurve[i][0])
        Is.append(epicurve[i][1])
        Rs.append(epicurve[i][2])
        
    
    a=plt.axes([.82,.82,.15,.15],frameon=False)
        
    plt.plot(days,Es,'y-')
    plt.plot(days,Is,'r-')
    plt.plot(days,Rs,color='grey',linestyle='-')
    
    plt.setp(a,xticks=[],yticks= [])
   
    plt.savefig(outstem+str(day)+".png",dpi=150)

    print "Plotted day:" + str(day) 
    plt.close()
 
    return epicurve

def fork_layout_run(program, *args):
    pid = os.fork()
    if not pid:
        os.execvp(program, (program,) +  args)
    return os.wait()[0]



def main():

    parser = optparse.OptionParser(usage=usgmsg)
    options, args = parser.parse_args()

    if len(args) < 4:
        usage()
        sys.exit(1)

    EFOfile = args[0]
    demofile = args[1]
    replicate = args[2]
    outstem = args[3]

    g = nx.DiGraph()
    
    get_epidemic_graph(g,EFOfile, replicate)
    g = parse_demographics(g,demofile)
  
    ##  Bypass the above by reading directly from archive  
    #print "Reading: "+outstem+graph_format
    #g = nx.readwrite.graphml.read_graphml("baseline98_anim.graphml")
    
    ###  Output graph if it might be useful
    print "Writing: "+outstem+graph_format
    #nx.readwrite.graphml.write_graphml(g, outstem+graph_format)
    nx.readwrite.gexf.write_gexf(g, outstem+graph_format)
    
    ###  Use headless gephi script to layout the graph
    command = "java -Xms1G -Xmx2G -jar " + gephi_layout_script +" "+ outstem+graph_format +" "+ outstem+layout_label+graph_format
 
    print "Running: "+command 
    os.system(command)

#    fork_layout_run("java",command)


    # Clear the old one (free memory) and read in the new layed out graph
    print "Reading: "+outstem+layout_label+graph_format
    g.clear()
    #g = nx.readwrite.graphml.read_graphml(outstem+layout_label+graph_format)
    g = nx.readwrite.gexf.read_gexf(outstem+layout_label+graph_format)

    ###  Prep for animation    
    curr_incub = {}
    curr_symp = {}
    curr_recover = {}
    new_incub = []
    new_symptomatic = []
    new_recover = []
    
    epicurve = ({ 0: [0,0,0], 1: [0,0,0]})

    ###  Choose duration to animate
    for day in range(1,200):
        
#        n,ns,np,nc = get_nodes_for_plotting(g,day)
#        s = g.subgraph(n)
#        make_plot(nx,plt,day,s,n,np,ns,nc)

        new_infs = get_new_infections(g,day)
        curr_incub, new_symptomatic = update_incubating(g,day,new_infs,curr_incub)
        curr_symp,new_recover = update_symptomatic(g,day,new_symptomatic,curr_symp)
        curr_recover = update_recovered(day,new_recover,curr_recover) 

        epicurve = draw_graph(g,day,outstem,curr_incub,curr_symp,curr_recover,epicurve)


if __name__ == '__main__':
    main()
