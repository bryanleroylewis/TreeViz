"""
Script for animating the pertussis epidemic in Floyd
"""

import TreeViz as tv
import networkx as nx
import os
import random
import time
import datetime


random.seed(12345)

gephi_layout_script = "gephi-toolkit-0.7.2014-all/gephi-toolkit-demos/gephi_yifanhu_multi_layout/dist/gephi_yifanhu_multi_layout.jar"


g = nx.DiGraph()
f = open("Floyd_pertussis/Floyd_pertussis_contactinvestigation.csv" ,'r')
header = f.readline()
max_day = 0
node_id = 1

min_date = datetime.datetime(*time.strptime("Feb 16 2011","%b %d %Y")[0:6])

for l in f.readlines():
    l = l.rstrip("\n")
    l = l.rstrip("\r")
    d = l.split(",")
    
    g.add_node(node_id)
    g.node[node_id]["class"] = int(d[0])
    g.node[node_id]["family"] = int(d[1])
    g.node[node_id]["extra"] = str(d[2])
    g.node[node_id]["relation"] = str(d[3])
    g.node[node_id]["symptom_date"] = str(d[4])

    if not str(d[4]) == '':
        symp_date = datetime.datetime(*time.strptime(str(d[4]),"%a %b %d %H:%M:%S %Z %Y")[0:6])
        onset_day = symp_date - min_date
        g.node[node_id]["onset_day"] = onset_day.days
    
    g.node[node_id]["cough"] = str(d[5])
    g.node[node_id]["whoop"] = str(d[6])
    g.node[node_id]["vomit"] = str(d[7])
    g.node[node_id]["run_nose"] = str(d[8])
    g.node[node_id]["coryza"] = str(d[9])
    g.node[node_id]["vax"] = str(d[10])
    g.node[node_id]["prophylax"] = str(d[11])
    g.node[node_id]["proph_date"] = str(d[12])
    g.node[node_id]["zip"] = str(d[13])

    node_id = node_id + 1

nodes = g.nodes()

for i in range(0,len(nodes)):
    n_id = nodes[i]
    n = g.node[n_id]
    
    ## Add parents, spouses and siblings
    if n["extra"].find("parent") > -1:
        p_num = int(n["extra"].partition(" parent")[0])
        print "Adding "+str(p_num)+" parents  for " + str(n_id) 
        for x in range(0,p_num):
            g.add_node(node_id)
            g.node[node_id]["family"] = n["family"]
            g.node[node_id]["relation"] = "parent"
            g.add_edge(n_id,node_id,relation="parent")
            node_id = node_id + 1
            
            

    if n["extra"].find("sib") > -1:
        p_num = int(n["extra"].partition(" sib ")[0].partition(" parents ")[2])
        print "Adding "+str(p_num)+" siblings"
        for x in range(0,p_num):
            g.add_node(node_id)
            g.node[node_id]["family"] = n["family"]
            g.node[node_id]["relation"] = "sibling"
            g.add_edge(n_id,node_id,relation="sibling")
            node_id = node_id + 1

    if n["extra"].find("spouse") > -1:
        g.add_node(node_id)
        g.node[node_id]["family"] = n["family"]
        g.node[node_id]["relation"] = "spouse"
        g.add_edge(n_id,node_id,relation="spouse")
        node_id = node_id + 1

    if n["extra"].find("unknown") > -1:
        random_node = random.randint(1,node_id)
        g.add_edge(n_id,random_node,relation="unknown")


    #### Look to add edges    
    for j in range(i+1,len(nodes)):
        m_id = nodes[j]
        m = g.node[m_id]

        ###  Link those asssociated with classes and friends
        if m["extra"].find("friend of") > -1:
            if m["extra"].find("friend of fam") > -1:
                friend = int(m["extra"].partition("friend of fam ")[2])
                if friend == n["family"]:
                    g.add_edge(m_id,n_id,relation="friend of fam")
            if m["extra"].find("friend of class") > -1:
                friend = int(m["extra"].partition("friend of class ")[2])
                if friend == n["class"]:
                    g.add_edge(m_id,n_id,relation="friend of class")

        if n["extra"].find("friend of") > -1:
            if n["extra"].find("friend of fam") > -1:
                friend = int(n["extra"].partition("friend of fam ")[2])
                if friend == n["class"]:
                    g.add_edge(m_id,n_id,relation="friend of fam")
            if n["extra"].find("friend of class") > -1:
                friend = int(n["extra"].partition("friend of class ")[2])
                if friend == n["class"]:
                    g.add_edge(m_id,n_id,relation="friend of class")

        ###  Special cases 
        ###     -multiple classes
        if m["extra"].find("multiple classes") > -1:
            friend = random.randint(1,4)
            if friend == n["class"]:
                g.add_edge(m_id,n_id,relation="friend of many classes")
            friend = random.randint(1,4)
            if friend == n["class"]:
                g.add_edge(m_id,n_id,relation="friend of many classes")

        if n["extra"].find("multiple classes") > -1:
            friend = random.randint(1,4)
            if friend == m["class"]:
                g.add_edge(m_id,n_id,relation="friend of many classes")
            friend = random.randint(1,4)
            if friend == m["class"]:
                g.add_edge(m_id,n_id,relation="friend of many classes")


                

        if m["class"] > 0 and m["class"] == n["class"]:
           g.add_edge(m_id,n_id,relation="class")

        if m["family"] > 0 and m["family"] == n["family"]:
            g.add_edge(m_id,n_id,relation=m["relation"])


nx.write_gexf(g,"Floyd_pertussis/Floyd_outbreak2.gexf")
