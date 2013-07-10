"""
    Tools for visualizing disease transmission through large graphs
"""

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from mpl_toolkits.mplot3d import Axes3D
import sys
import locale
import optparse
import os
import string

# Usage message
usgmsg = "Usage: animate_epidemic_tree.py [options] infile.EFO6 demographic_file replicate outfile"


def add_disease_from_EFO(g,file,only_existing=True):
    """
    Add nodes and details about disease state duration from an EFO file to graph g.
    """

    f = open(file,'r')    
    nodes_update = 0
    nodes_list = g.nodes()
   
    for l in f.readlines():
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
            elif not only_existing:
                nodes_update = nodes_update + 1
                g.add_node(id, incubation = incub, symptomatic = symp)
            
    f.close()
    print "Done parsing "+file+" total of "+str(nodes_update)+" nodes updated"
    
def add_socialnet_details(g,file,only_existing=True):

    lines_parsed = 0
    f = open(file,'r')
    
    edges_list = g.edges()
   
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

            ###  If all edges of social network are desired
            if not only_existing:
                g.add_node(id1)
                g.add_node(id2)
                
                g.add_edge(id1,id2,duration=dur,activity=act)
                
            ###  Otherwise only add them if the edge exists in the graph
            elif (id1,id2) in edges_list or (id2,id1) in edges_list:
                g.add_node(id1)
                g.add_node(id2)
                g.add_edge(id1,id2,duration=dur,activity=act)

    f.close()
    print "Done parsing "+file+" total of "+str(lines_parsed)+" lines parsed"
    print "Graph has "+str(len(g.nodes()))+" nodes and "+str(len(g.edges()))+" edges"
    
def build_socialnetwork(g,file):

    lines_parsed = 0
    f = open(file,'r')
    
    edges_list = g.edges()
   
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


            if (id1,id2) in edges_list:
                new_dur = g.edge[id1][id2]["duration"] + dur
                new_act = g.edge[id1][id2]["activity"]
                g.add_edge(id1,id2,duration=new_dur,activity=new_act)
            
            elif (id2,id1) in edges_list:
                new_dur = g.edge[id2][id1]["duration"] + dur
                new_act = g.edge[id2][id1]["activity"]
                g.add_edge(id2,id1,duration=new_dur,activity=new_act)

            else:
                g.add_node(id1)
                g.add_node(id2)
                g.add_edge(id1,id2,duration=dur,activity=act)
                edges_list.append((id1,id2))

    f.close()
    print "Done parsing "+file+" total of "+str(lines_parsed)+" lines parsed"
    print "Graph has "+str(len(g.nodes()))+" nodes and "+str(len(g.edges()))+" edges"
    

def get_vulnerabilities(g,file,replicate=-1):
    """Add vulnerabilities from EFO file to graph g."""

    f = open(file,'r')

    for l in f.readlines():
        l = l.rstrip("\n")
        
        if l.find('#') >= 0:
        	# Process headers
        	print l
        elif len(l.rsplit(" ")) >= 4:
            # Process edge
            e_dest = int(l.rsplit(" ")[0])
            e_rep = int(l.rsplit(" ")[1])
            e_day = int(l.rsplit(" ")[2])
            e_src = int(l.rsplit(" ")[3])
        
            if replicate == -1 or e_rep == replicate:
                # ensure the edges exist            
                g.add_node(e_src)
                g.add_node(e_dest)
                g.add_edge(e_src,e_dest)

                #  Update vulnerability            
                if g.edge[e_src][e_dest].has_key("vul"):
                    g.edge[e_src][e_dest]["vul"] = g.edge[e_src][e_dest]["vul"] + 1
                else:
                    g.edge[e_src][e_dest]["vul"] = 1

                if g.node[e_dest].has_key("vul"):
                    g.node[e_dest]["vul"] = g.node[e_dest]["vul"] + 1
                else:
                    g.node[e_dest]["vul"] = 1
                
            
    f.close()
    print "Done parsing "+file+" a total of "+str(len(g.nodes()))+" nodes and "+str(len(g.edges()))+" edges"


def build_vul_weighted_socnet(g,EFO_file,dz_details=False):
    """
    Build social network with edges weighted by vulnerability for 
    """

    get_vulnerabilities(g,EFO_file)

    if dz_details:
        add_socialnet_details(g,EFO_file,only_existing=True)


    ###  Weight edges by a particular attribute
    for (src,dest,data) in g.edges_iter(data=True):
        g.edge[src][dest]["weight"] = data["vul"]

    nx.write_gexf(g,EFO_file+"_vul.gexf")

    return g


def get_epidemic_graph(g,file,replicate,dz_details=True,EFOact=False):
    """Add nodes and interactions in the EFO file to graph g."""

    f = open(file,'r')    

    for l in f.readlines():
        l = l.rstrip("\n")
        
        if l.find('#') >= 0 or l.find('ID') >=0:
        	# Process headers
        	print l
        elif len(l.rsplit(" ")) == 3 and dz_details:
            # Process node
            
            id = int(l.rsplit(" ")[0])
            incub = int(l.rsplit(" ")[1])
            symp = int(l.rsplit(" ")[2])
            #name = "n%s" % str(id)

            g.add_node(id, incubation = incub, symptomatic = symp)      

        ###  Normal EFO file with 4 fields, infected_id rep day infecter_id        
        elif (len(l.rsplit(" ")) == 4  and int(l.rsplit(" ")[1]) == replicate):
            # Process edge
            e_dest = int(l.rsplit(" ")[0])
            e_iter = int(l.rsplit(" ")[1])
            e_day = int(l.rsplit(" ")[2])
            e_src = int(l.rsplit(" ")[3])
            e_weight = 1
            
            g.add_edge(e_src,e_dest,iter=e_iter)
            g.add_edge(e_src,e_dest,day=e_day)

        ###  EFOact file which includes activity with 5 fields, infected_id rep day infecter_id act       
        elif    (EFOact ==  True and 
                 len(l.rsplit(" ")) >= 5 and
                 int(l.rsplit(" ")[1]) == replicate):
            # Process edge
            e_dest = int(l.rsplit(" ")[0])
            e_iter = int(l.rsplit(" ")[1])
            e_day = int(l.rsplit(" ")[2])
            e_src = int(l.rsplit(" ")[3])
            e_act = int(l.rsplit(" ")[4])
            e_weight = 1
            
            g.add_edge(e_src,e_dest,iter=e_iter)
            g.add_edge(e_src,e_dest,day=e_day)
            g.add_edge(e_src,e_dest,act=e_act)
            
            
    f.close()
    print "Done parsing "+file+" for replicate "+str(replicate)+" total of "+str(len(g.nodes()))+" nodes and "+str(len(g.edges()))+" edges"

def build_episimdemic_dendogram_graph(g,file):
    """Add nodes and interactions in the dz_dendogram file to graph g."""

    f = open(file,'r')    

    for l in f.readlines():
        l = l.rstrip("\n")
        
        if l.find('#') >= 0 or l.find('ID') >=0 or len(l.rsplit(" ")) <2:
        	# Process headers
        	print l
        else:
            # Process edge
            e_dest = int(l.rsplit(" ")[0])
            e_time = int(l.rsplit(" ")[2])
            e_loc_id = "_".join((l.rsplit(" ")[7],l.rsplit(" ")[8]))
            e_act = int(l.rsplit(" ")[9])
            e_src = int(l.rsplit(" ")[5])
            e_weight = 1
            
            g.add_edge(e_src,e_dest,time=e_time)
            g.add_edge(e_src,e_dest,loc_id=e_loc_id)
            g.add_edge(e_src,e_dest,act=e_act)


    f.close()
    print "Done parsing "+file+" found total of "+str(len(g.nodes()))+" nodes and "+str(len(g.edges()))+" edges"


def parse_demographics(g,file):
    """Add demographic details to nodes"""

    demo_count = 0
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
            demo_count = demo_count + 1
            for c in range(1,len(header)-1):
                g.node[pid][header[c]] = d[c]
    
    f.close()

    print "Done parsing "+file+" and added demographics to "+str(demo_count)+" nodes"
   
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

def update_recovered(day,new_recover,curr_recover,days_in_recovery=3):
    """ Updates the list of nodes in the recovered state.  The dict curr_recover keeps   track of all recovered nodes and the day they will leave recovered (to avoid clutter).
    returns the current dict of recovered nodes"""
    
    
    for n in new_recover:
        end_day = day + days_in_recovery
        curr_recover.update({n:end_day})
        
    for n in curr_recover.keys():
        if day > curr_recover[n]:
            del(curr_recover[n])
  
    return curr_recover

def draw_graph(g, day, outstem, curr_incub, curr_symp, curr_recover, epicurve, size_scaler = 33, fixed_size=0, colors=["grey","#800000","#FFD700"], draw_arrow=True, include_components = True,act_colored_edges=False):
    """Draws graph for prevalent infections (showing incubating and symptomatic states as different colors).  Needs maintained list of incubating and symptomatic infections.
    """

    ns = []
    np = {}
    xcoords = []
    ycoords = []
    
    degs =[]
    
    E = len(curr_incub.keys()) 
    I = len(curr_symp.keys()) 
    R = len(curr_recover.keys())
    
    nodes_to_draw =  curr_recover.keys() + curr_symp.keys() +  curr_incub.keys()

    node_colors =  [colors[0]]*R + [colors[1]]*I + [colors[2]]*E
    
    max_degree = len(nx.degree_histogram(g))
    
    ##  Get the positions and sizes of the nodes to draw
    for n in nodes_to_draw:
        if fixed_size == 0:
            size = ((g.out_degree(n)+1)/float(max_degree))*size_scaler
        if fixed_size > 0:
            size = fixed_size
            
        ns.append(size)
        degs.append(g.out_degree(n))
        
        x = g.node[n]["viz"]["position"]["x"]
        y = g.node[n]["viz"]["position"]["y"]
        
        curr_pos = [x,y]
        np.update({n:curr_pos})
        
    nx.draw_networkx_nodes(g,pos=np,nodelist = nodes_to_draw,node_size=ns,node_color = node_colors, with_labels=False,linewidths=0,edgecolors="none")

    if act_colored_edges==False:
        nx.draw_networkx_edges(g,pos=np, edgelist = (g.subgraph(nodes_to_draw)).edges(), width=0.5, alpha=0.65, arrows=draw_arrow)
    else:
        actmap = mcolors.ListedColormap(['#CD5C5C','#00FFFF','#000000','#BA55D3','#008000'],"actmap", N=5)
        e_colors = [e[2]['act'] for e in g.subgraph(nodes_to_draw).edges_iter(data=True)]
        nx.draw_networkx_edges(g,pos=np, edgelist = (g.subgraph(nodes_to_draw)).edges(), edge_color = e_colors, edge_cmap = actmap,width=1, alpha=0.65, arrows=draw_arrow)


    ##  Define the canvas
    if len(nodes_to_draw) > 0:
        for n in g.nodes_iter():
            xcoords.append(g.node[n]["viz"]["position"]["x"])
            ycoords.append(g.node[n]["viz"]["position"]["y"])

        plt.xlim(round(min(xcoords),-2),round(max(xcoords),-2))
        plt.ylim(round(min(ycoords),-2),round(max(ycoords),-2))
    
    plt.axis('off')
    
    ####  Labelling the plot
    plt.figtext(0.02,0.97,s = "Day: "+str(day), size = 'large')

    
    s = g.subgraph(nodes_to_draw) #  subgraph to get stats on what is visualized
    
    if include_components:
        components = nx.connected_components(s.to_undirected())
    
        plt.figtext(0.02,0.05,s = "Number of components: "+str(len(components)),size='small')
        component_sizes = []
        for l in components:
            component_sizes.append(len(l))
        plt.figtext(0.02,0.03,s = "Sizes: "+str(component_sizes),size='xx-small')
    
    
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
   
    plt.savefig(outstem+"_day"+str(day)+".png",dpi=300)

    print "Plotted day:" + str(day) 
    plt.close()
 
    return epicurve

def anim_graph(epi,anim_stem,max_day,act_colored_edges=False):
    curr_incub = {}
    curr_symp = {}
    curr_recover = {}
    new_incub = []
    new_symptomatic = []
    new_recover = []
    
    epicurve = ({ 0: [0,0,0], 1: [0,0,0]})
    
    
    if max_day > 0:
        print "Plotting "+str(max_day)+" days"
    else:
        max_day = 175
    
    ###  Tidy up graph
    if 'Infected' in epi.node:
        epi.remove_node('Infected')
    if 'Infector' in epi.node:
        epi.remove_node('Infector')
    
    
    ###  Choose duration to animate
    for day in range(1,max_day):
        
        new_infs = get_new_infections(epi,day)
        curr_incub, new_symptomatic = update_incubating(epi,day,new_infs,curr_incub)
        curr_symp,new_recover = update_symptomatic(epi,day,new_symptomatic,curr_symp)
        curr_recover = update_recovered(day,new_recover,curr_recover,days_in_recovery=5) 
    
        epicurve = draw_graph(epi,day,anim_stem,curr_incub,curr_symp,curr_recover,epicurve,fixed_size=15, draw_arrow = False, act_colored_edges=act_colored_edges)

def draw_graph_3d(g,iters=250):

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    plt.axis('off')

    pos3d = nx.spring_layout(g,dim=3,iterations=iters)
    xs = []
    ys = []
    zs = []
    
    for u,v in g.edges_iter():
        xs = [pos3d[u][0],pos3d[v][0]]
        ys = [pos3d[u][1],pos3d[v][1]]
        zs = [pos3d[u][2],pos3d[v][2]]
    
        ax.plot(xs,ys,zs,color=[0,0,0,.1],lw=.5)
    
    ax.scatter([pos3d[n][0] for n in pos3d],[pos3d[n][1] for n in pos3d],[pos3d[n][2] for n in pos3d])
    
    plt.axis('off')

    plt.show()
    
    


def filter_vulnerabilities(g,node_threshold,edge_threshold):
    """  Remove edges and nodes with vulnerabilities less than the threshold """
    
    rm_edges = 0
    rm_nodes = 0
    edges_to_rm = []
    nodes_to_rm = []

    for s,d in g.edges_iter():
        if g.edge[s][d]["vul"] < int(edge_threshold):
            edges_to_rm.append((s,d))
            rm_edges = rm_edges + 1

    for n in g.nodes_iter():
        if g.node[n]["vul"] < int(node_threshold):
            nodes_to_rm.append(n)
            rm_nodes = rm_nodes + 1

    g.remove_edges_from(edges_to_rm)
    g.remove_nodes_from(nodes_to_rm)

    print "Removed "+str(rm_edges)+" edges and "+str(rm_nodes)+" nodes with node vul < "+str(node_threshold) + "edge vul < "+str(edge_threshold)

def remove_orphans(g):
    """ Removes all nodes with degree == 0 """
    
    nodes_to_rm = []
    orphan_count = 0
    for n,d in g.degree_iter():
        if d == 0:
            g.remove_node(n)
            orphan_count = orphan_count + 1

    print "Removed "+str(orphan_count)+" nodes with degree == 0"

def remove_init_infector(g):
    """ Removes the -1 node that signifies an intialized infection source """
    
    g.remove_node(-1)

    print "Removed node -1, all initialized infections"

def find_init_infections(g):
    """ For graphs without nodes of -1, find the nodes with no in_degree """
    
    init_infections = []
    for n in g.nodes():
        if(g.in_degree(n) == 0):
            init_infections.append(n)
    return init_infections

def find_txm_chain_terminators(g):
    """ Find all the nodes with no out_degree, ie those at the end of a chain transmission """
    
    terminal_nodes = []
    for n in g.nodes():
        if(g.out_degree(n) == 0):
            terminal_nodes.append(n)
    return terminal_nodes

def run_gephi_layout(gephi_layout_script,outstem,graph_format,layout_label):
    """ Use headless gephi script to layout the graph """
    
    command = "java -Xms1G -Xmx2G -jar " + gephi_layout_script +" "+ outstem+graph_format +" "+ outstem+layout_label+graph_format
 
    print "Running: "+command 
    os.system(command)

def add_data_to_epi(epi,data):
    """  Adds data from the nodes in the data graph (like position and demographic details) to the stripped down epi graph (representing a particular outbreak) """
   
    for a,b in epi.edges_iter():
        epi.node[a].update(data.node[str(a)])
        epi.node[b].update(data.node[str(b)])

def initialize_Reff_generation(g,Reff_dist):
    max_deg = 0
    max_gen = 0  ##  Too hard to calc a priori

    for n in g.nodes_iter():
        if(g.out_degree(n) > max_deg):
            max_deg = g.out_degree(n)
    
    Reff_dist.append([0]*(max_deg+1))

    return Reff_dist

def update_Reff_generation(Reff_dist,g,curr_gen,node_id):
    out_deg = g.out_degree(node_id)
    gen = curr_gen + 1

    ### if there isn't a row for the generation add it
    while len(Reff_dist) <= gen:
        max_deg = len(Reff_dist[0])
        Reff_dist.append([0]*max_deg)
    
    Reff_dist[gen][out_deg] = Reff_dist[gen][out_deg] + 1
    
    out_edges = g.edges(node_id)
    
    if(len(out_edges) > 0):
        for e in g.edges(node_id):
            Reff_dist = update_Reff_generation(Reff_dist,g,gen,e[1])
    
    return Reff_dist

def update_Reff_day_by_day(Reff_dist,g,curr_gen,node_id):
    out_deg = g.out_degree(node_id)
    if(curr_gen > 0):
        day = g.in_edges(node_id,data=True)[0][2]['day']
    else:
        day = 1

    gen = curr_gen + 1

    ### if there isn't a row for the day add it
    while len(Reff_dist) <= day:
        max_deg = len(Reff_dist[0])
        Reff_dist.append([0]*max_deg)
    
    Reff_dist[day][out_deg] = Reff_dist[day][out_deg] + 1
    
    out_edges = g.edges(node_id)
    
    if(len(out_edges) > 0):
        for e in g.edges(node_id):
            Reff_dist = update_Reff_day_by_day(Reff_dist,g,gen,e[1])
    
    return Reff_dist

def build_Reff_txm_chain(g):
    
    Reff_chains = {}
    terminal_nodes = find_txm_chain_terminators(g)

    for start_node in terminal_nodes:
        n = start_node
        reff_chain = [0]
        
        while len(g.in_edges(n)) > 0:
            n = g.in_edges(n)[0][0]
            reff = g.out_degree(n)
            reff_chain.insert(0,reff)
        
        Reff_chains[start_node] = reff_chain
    
    return Reff_chains
        


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

        new_infs = get_new_infections(epi,day)
        curr_incub, new_symptomatic = update_incubating(epi,day,new_infs,curr_incub)
        curr_symp,new_recover = update_symptomatic(epi,day,new_symptomatic,curr_symp)
        curr_recover = update_recovered(day,new_recover,curr_recover) 

        epicurve = draw_graph(epi,day,outstem,curr_incub,curr_symp,curr_recover,epicurve)


if __name__ == '__main__':
    main()
