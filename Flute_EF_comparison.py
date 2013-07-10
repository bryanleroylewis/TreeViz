"""
Script for animating the Epidemic Tree to compare differences between 
Flute and EpiFast
"""

import TreeViz as tv
import networkx as nx
import os
import random 
import numpy as np

gephi_layout_script = "../gephi-toolkit-0.7.2014-all/gephi-toolkit-demos/gephi_yifanhu_multi_layout/dist/gephi_yifanhu_multi_layout.jar"

def build_Flute_graph(flute_outbreak_file,rep):
    ##### Define disease model for arbitrary assignment of durations
    ###  Incubation: 1:0.3 2:0.5 3:0.2
    ###  Infectious: 3:0.3 4:0.4 5:0.2 6:0.1 
    inc = [1,1,1,2,2,2,2,2,3,3]
    inf = [3,3,3,4,4,4,4,5,5,6]
    random.seed(12345)
    
    ###  Add day to edge
    flute = nx.DiGraph()
#    f = open("Individuals1.EFOformat.txt",'r')
    f = open(flute_outbreak_file,'r')
    header = f.readline()
    max_day = 0
    for l in f.readlines():
        l = l.rstrip("\n")
        l = l.rstrip("\r")
        d = l.split(" ")

        if int(d[1]) == rep:
            flute.add_node(str(d[3]))
            flute.add_node(str(d[0]))
        
            flute.node[str(d[3])]["incubation"] = random.choice(inc)
            flute.node[str(d[0])]["incubation"] = random.choice(inc)
            flute.node[str(d[3])]["symptomatic"] = random.choice(inf)
            flute.node[str(d[0])]["symptomatic"] = random.choice(inf)

            if len(d) == 4:
                flute.add_edge(str(d[3]),str(d[0]),day = int(d[2]))
            elif len(d) == 5:
                fl_act = int(d[4])
                if fl_act == 4:
                    ef_act = 5
                elif fl_act == 10 or fl_act == 1:
                    ef_act = 1
                elif fl_act == 5:
                    ef_act = 2
                elif fl_act == 20 or fl_act == 21:
                    ef_act = 0
                elif fl_act > 10 or fl_act == 2 or fl_act == 3:
                    ef_act = 4
                else:
                    ef_act = -1

                flute.add_edge(str(d[3]),str(d[0]),day = int(d[2]))
                flute.add_edge(str(d[3]),str(d[0]),act=ef_act)
       
        if int(d[2]) > max_day:
            max_day = int(d[2])
    
    print flute_outbreak_file + " rep "+str(rep)+" has edges: "+str(len(flute.edges()))+" nodes: "+str(len(flute.nodes()))+" max day:"+str(max_day)

    return flute,max_day

def analyze_Reff_chains():
    fl_m20 = nx.read_gexf("Flute_vs_EpiFast/Flute_match20.gexf")
    reffs_fl_m20 = tv.build_Reff_txm_chain(fl_m20)


    ef_m20 = nx.read_gexf("Flute_vs_EpiFast/Epifast_match20.gexf")
    reffs_ef_m20 = tv.build_Reff_txm_chain(ef_m20)

    max_gens = 31

#    for r in reffs_ef_m20.values():
#        if len(r) == i:
            


def main():

    anim = False
    analysis = True    
    
    
    ###  Build from scratch EFO file:
    # tv.get_epidemic_graph(ef_m20, "Epifast_match40_dzdetails.EFOact", 2, EFOact=True)
    
    ### Command like the following can call a headless gephi script to lay it out
    #gephi_layout_script = "
    #tv.run_gephi_layout(gephi_layout_script, "EpiFast.00003.rep21",".gexf","_ml")
    
    ###  Once laid out in Gephi, read them in    
    ef_m20 = nx.read_gexf("Flute_vs_EpiFast/Epifast_match20_oofa2.gexf")
    ef_m40 = nx.read_gexf("Flute_vs_EpiFast/Epifast_match40_oofa2.gexf")

    fl_m20 = nx.read_gexf("Flute_vs_EpiFast/Flute_match20_oofa2.gexf")
    fl_m40 = nx.read_gexf("Flute_vs_EpiFast/Flute_match40_oofa2.gexf")
    
    
    
    if(analysis):

        ###  Add more for each different epidemic efm40, flm20,flm40
        efm20_day_reff = tv.initialize_Reff_generation(ef_m20,[])
        efm20_gen_reff = tv.initialize_Reff_generation(ef_m20,[])
        efm40_day_reff = tv.initialize_Reff_generation(ef_m40,[])
        efm40_gen_reff = tv.initialize_Reff_generation(ef_m40,[])

        flm20_day_reff = tv.initialize_Reff_generation(fl_m20,[])
        flm20_gen_reff = tv.initialize_Reff_generation(fl_m20,[])
        flm40_day_reff = tv.initialize_Reff_generation(fl_m40,[])
        flm40_gen_reff = tv.initialize_Reff_generation(fl_m40,[])



        efm20_ii = tv.find_init_infections(ef_m20)
        for n in efm20_ii:                        
            efm20_day_reff = tv.update_Reff_day_by_day(efm20_day_reff,ef_m20,0,n)
        for n in efm20_ii:                        
            efm20_gen_reff = tv.update_Reff_generation(efm20_gen_reff,ef_m20,0,n)

        efm40_ii = tv.find_init_infections(ef_m40)
        for n in efm40_ii:                        
            efm40_day_reff = tv.update_Reff_day_by_day(efm40_day_reff,ef_m40,0,n)
        for n in efm40_ii:                        
            efm40_gen_reff = tv.update_Reff_generation(efm40_gen_reff,ef_m40,0,n)

        flm20_ii = tv.find_init_infections(fl_m20)
        for n in flm20_ii:                        
            flm20_day_reff = tv.update_Reff_day_by_day(flm20_day_reff,fl_m20,0,n)
        for n in flm20_ii:                        
            flm20_gen_reff = tv.update_Reff_generation(flm20_gen_reff,fl_m20,0,n)

        flm40_ii = tv.find_init_infections(fl_m40)
        for n in flm40_ii:                        
            flm40_day_reff = tv.update_Reff_day_by_day(flm40_day_reff,fl_m40,0,n)
        for n in flm40_ii:                        
            flm40_gen_reff = tv.update_Reff_generation(flm40_gen_reff,fl_m40,0,n)




        ### Write matrices to a file
        np.savetxt('Flute_vs_EpiFast/ef_m20_day_reff_dist.txt',efm20_day_reff,fmt='%d')
        np.savetxt('Flute_vs_EpiFast/ef_m20_gen_reff_dist.txt',efm20_gen_reff,fmt='%d')
        np.savetxt('Flute_vs_EpiFast/ef_m40_day_reff_dist.txt',efm40_day_reff,fmt='%d')
        np.savetxt('Flute_vs_EpiFast/ef_m40_gen_reff_dist.txt',efm40_gen_reff,fmt='%d')

        np.savetxt('Flute_vs_EpiFast/fl_m20_day_reff_dist.txt',flm20_day_reff,fmt='%d')
        np.savetxt('Flute_vs_EpiFast/fl_m20_gen_reff_dist.txt',flm20_gen_reff,fmt='%d')
        np.savetxt('Flute_vs_EpiFast/fl_m40_day_reff_dist.txt',flm40_day_reff,fmt='%d')
        np.savetxt('Flute_vs_EpiFast/fl_m40_gen_reff_dist.txt',flm40_gen_reff,fmt='%d')
      

    if(anim):
    
        ###  Add other lines for other epidemics efm40, flm20, flm40
        tv.anim_graph(ef_m20_oofa2, "Flute_vs_EpiFast/movies/EF_mTwenty", 250, act_colored_edges=True)
    

if __name__ == '__main__':
    main()

