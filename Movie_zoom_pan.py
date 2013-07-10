"""
Zoom in on high res images for movies
"""

import os
import sys

file_stem = "movies/MatchTwo_EF_t-five_r-nine_lay-oo_hirez_day"
new_file_stem = "movies/MatchTwo_EF_t-five_r-nine_lay-oo_hrzoom_day"
extension = ".png"

orig_res = [2400,1800]
new_res = [960,720]

###  Centered
start_offset = [int((orig_res[0] - new_res[0])/2), int((orig_res[0] - new_res[0])/2) ]
#start_offset = [720,540]


#end_offset = [450,340]
####  Don't move
end_offset = start_offset


num_steps = 50

x_step = int((end_offset[0] - start_offset[0]) / num_steps)
y_step = int((end_offset[1] - start_offset[1]) / num_steps)

x = start_offset[0]
y = start_offset[1]

for s in range(1,num_steps):
    
    file = file_stem+str(s)+extension
    new_file = new_file_stem+str(s)+extension

    geo = str(new_res[0])+"x"+str(new_res[1])+"+"+str(x)+"+"+str(y)
        
    
    command  = "convert "+file+" -crop "+geo+" "+new_file

    print "Running:  "+command
    os.system(command)

    x = x + x_step
    y = y + y_step

