"""
Script for animating the Epidemic Tree differences in Montgomery County
"""

import TreeViz as tv
import networkx as nx
import os

gephi_layout_script = "gephi-toolkit-0.7.2014-all/gephi-toolkit-demos/gephi_yifanhu_multi_layout/dist/gephi_yifanhu_multi_layout.jar"
layout_label = "_multilevel"
graph_format = ".gexf"



def main():

    base_stem = "mean_graphs/combined"
    graph_format = ".gexf"
    layout_label = "_multilevel"

    nvul_threshold = 1
    evul_threshold = 1

    rep_to_get = 3

    vul_stem = "_vul-n"+str(nvul_threshold)+"e"+str(evul_threshold)
    rep_stem = "_rep"+str(rep_to_get)
    
    outstem = base_stem+vul_stem+rep_stem

    ###  If we haven't already layed out the graph, get it and save it
    if(not os.access(outstem+layout_label+graph_format,2)):
    
        ###  Get the non-layed out version if possible
        if(os.access(outstem+graph_format,2)):
            g = nx.readwrite.gexf.read_gexf(outstem+graph_format)
        
        else: 
            g = nx.DiGraph()

            os.system("growlnotify -t TreeViz -m \"Getting started: reading from baseline\"")
#           tv.get_vulnerabilities(g,"baseline.EFO6",rep_to_get)

            os.system("growlnotify -t TreeViz -m \"reading school closure triggers\"")
            tv.get_vulnerabilities(g,"sc50_trig75.EFO6",rep_to_get)
            tv.get_vulnerabilities(g,"sc50_trig85.EFO6",rep_to_get)
            tv.get_vulnerabilities(g,"sc50_trig95.EFO6",rep_to_get)
            tv.get_vulnerabilities(g,"sc50_trig105.EFO6",rep_to_get)
            tv.get_vulnerabilities(g,"sc50_trig115.EFO6",rep_to_get)
            tv.get_vulnerabilities(g,"sc50_trig125.EFO6",rep_to_get)
    
            tv.remove_init_infector(g)
            tv.remove_orphans(g)
        
            os.system("growlnotify -t TreeViz -m \"Filtering with node threshold "+str(nvul_threshold)+" and edge threshold "+str(evul_threshold)+"  \"")
            tv.filter_vulnerabilities(g,nvul_threshold,evul_threshold)
    
    #	 os.system("growlnotify -t TreeViz -m \"Adding details from social network\"")
    #	 tv.add_socialnet_details(g,"socialnet/va_mont_county.socnet.sorted.txt")
    
            print "Writing: "+outstem+graph_format
            nx.readwrite.gexf.write_gexf(g, outstem+graph_format)

        os.system("growlnotify -t TreeViz -m \"Starting gephi layout \"")
        tv.run_gephi_layout(gephi_layout_script,outstem,graph_format,layout_label)

        g.clear()
        g = nx.readwrite.gexf.read_gexf(outstem+layout_label+graph_format)

    else:
        os.system("growlnotify -t TreeViz -m \"Found and starting reading "+outstem+layout_label+graph_format+" to get the layout \"")
        g = nx.readwrite.gexf.read_gexf(outstem+layout_label+graph_format)

    os.system("growlnotify -t TreeViz -m \"Reading in demographics\"")
    tv.parse_demographics(g,"va_mont_county_person_info")

    
    epi = nx.DiGraph()
    
    epi_to_anim = "sc50_trig75.EFO6"
    epi_name = epi_to_anim.rstrip("\.EFO6")
    tv.get_epidemic_graph(epi,epi_to_anim,rep_to_get,dz_details=False)
    tv.remove_init_infector(epi)
    tv.remove_orphans(epi)  ###  Should be redundant

    anim_stem = outstem+"__"+epi_name

    tv.add_data_to_epi(epi,g)

    ###  Prep for animation    
    curr_incub = {}
    curr_symp = {}
    curr_recover = {}
    new_incub = []
    new_symptomatic = []
    new_recover = []
    
    epicurve = ({ 0: [0,0,0], 1: [0,0,0]})

    ###  Choose duration to animate
    for day in range(1,100):
        
#        n,ns,np,nc = get_nodes_for_plotting(g,day)
#        s = g.subgraph(n)
#        make_plot(nx,plt,day,s,n,np,ns,nc)

        new_infs = tv.get_new_infections(epi,day)
        curr_incub, new_symptomatic = tv.update_incubating(epi,day,new_infs,curr_incub)
        curr_symp,new_recover = tv.update_symptomatic(epi,day,new_symptomatic,curr_symp)
        curr_recover = tv.update_recovered(day,new_recover,curr_recover) 

        epicurve = tv.draw_graph(epi,day,anim_stem,curr_incub,curr_symp,curr_recover,epicurve,size_scaler = 15)



if __name__ == '__main__':
    main()

