""" 
Collection of plotting functions
"""

import numpy as np
import matplotlib.pyplot as plt

def histogram_bar_plots(data,title="A Plot",xlab="The x-axis",ylab="Number",xtick_prefix=""):
    """  Expects a 2-D array, each row is a histogram, with x(bin)=array index and y=height of histrogram bar.
    """

    data_plot = np.transpose(data)
    N = len(data_plot[0])
    ind = np.linspace(0,N-1,N)
    buffer_space = 0.1
    width = (1-buffer_space) / N
    pos = ind
    
    colors = plt.cm.jet(range(1,256,int(256/(N-1))))

    fig = plt.figure()
    ax = fig.add_subplot(111)

    for d in data_plot:
      
        rects1 = ax.bar(pos, d, width, color=colors,linewidth=0)
        pos = pos + width
        
    # add some
    ax.set_ylabel(ylab)
    ax.set_xlabel(xlab)
    ax.set_title(title)
    ax.set_xticks(ind+((1-buffer_space)/2))

    x_tick_names = []
    for i in range(1,N+1):
        x_tick_names.append(xtick_prefix+str(i))

    ax.set_xticklabels(x_tick_names)
    
    plt.show()
    
def multi_pie_plotting(data,title="A Plot",dimx=5,dimy=5):
    """  Expects a 2-D array, each row is a frequency count within a single pie.  The number of rows will be spread out in a grid
    """

    rows = len(data)
    cols = len(data[0])
    row_num = 1
    
    colors = plt.cm.jet(range(1,256,int(256/(cols-1))))
    
   # global_sum = sum(data)
    max_sum = 0
    for d in data:
        if sum(d) > max_sum:
            max_sum = sum(d)
    
    names = []
    for i in range(1,cols+1):
        names.append("Re="+str(i))
    
    fig = plt.figure()
    fig.colorbar()
    
    for d in data:
        tot = sum(d)

        max_prop = tot / max_sum
        
        # make a square figure and axes
        subplot_pos = int(str(dimy) + str(dimx) + str(row_num))
        print str(subplot_pos)
        ax = fig.add_subplot(subplot_pos)
        ax.axis('off')
 #       ax.axis([0.1, 0.1, 0.8, 0.8],frameon=False)
        
        ax.pie(d, labels=names, autopct='%1f%%', colors=colors)
        plt.title('Generation '+str(row_num))
        
        
        row_num = row_num + 1
        
        plt.show()
       # raw_input()