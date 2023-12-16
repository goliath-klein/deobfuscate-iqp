import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
import json 

cmap = plt.get_cmap('viridis')
colors = cmap(np.arange(0,1,1/3.4))

import matplotlib.font_manager as font_manager
from matplotlib import rcParams
print("You need to download Source Sans Pro, \
    e.g., here: https://fonts.adobe.com/fonts/source-sans, \
    and then enter the path to the correct folder in the following line")

font_dir = ['/Users/dhangleiter/fonts/Source_Sans_Pro']
for font in font_manager.findSystemFonts(font_dir):
    font_manager.fontManager.addfont(font)

SIZE=9
rcParams['font.family'] = 'Source Sans Pro'
rcParams['font.size']=SIZE
rcParams['axes.titlesize']=SIZE
rcParams['axes.labelsize']=SIZE
rcParams['xtick.labelsize']=SIZE
rcParams['ytick.labelsize']=SIZE
rcParams['legend.fontsize']=SIZE
rcParams['figure.titlesize']=SIZE

markers = np.array(['o','D','^'])
marker_size = 5
capsize = 0
markeredgewidth = .5

alpha = 1
lw = 1.25
elinewidth = 1.5

linestyle = dict(
    linewidth=lw,
    dash_capstyle='round',
    solid_capstyle='round',
    linestyle='-',
    alpha=alpha
)
markerstyle = dict(
    markersize=marker_size,
    markeredgewidth=markeredgewidth,
    alpha=.8,
    marker=markers[0],
)
ebar_style = dict(
    elinewidth=elinewidth,
    capsize=capsize,
    # capstyle='round',
)
aspect_ratio = 2/3
pad=0
width = 250 * 0.01389
figsize = (width, aspect_ratio*width)
alpha1 = .7 
alpha2 = .3

fig,ax = plt.subplots(1,1,figsize=figsize)


import pickle 

pickleFilename = f"transition_figure_data.pickle"
with open(pickleFilename, 'rb') as pickleFile:
    plot1 = pickle.load(pickleFile)
    plot2 = pickle.load(pickleFile)
    plot3 = pickle.load(pickleFile)
    plot3er = pickle.load(pickleFile)
    print("--- DONE --- DONE --- DONE ---")


# critical region of binomial test
_,_, bars = ax.errorbar(*plot3, 
    yerr=plot3er,
    color=colors[2],
    linewidth=0,
    **ebar_style,
    label=f"5 % Confidence interval")
# theory curve
theory = ax.plot(*plot1,
    color=colors[1],
    **linestyle,
    label='Prediction')
# data points

    # color=color_tvd_unrec1,
    # markerfacecolor=color_tvd_unrec2,
data,_,_ = ax.errorbar(*plot2,
    linewidth=0,
    **markerstyle,
    color=(237/255,16/255,118/255),
    markeredgecolor=(131/255,28/255,71/255),
    label='Data')
# ax.set_title('Probability of success given $w$')
ax.set_xticks(plot2[0])
ax.set_xlabel(r'$w$')
ax.set_ylabel(r'Success probability')
ax.tick_params(direction='in')
ax.legend(frameon=False)


[bar.set_capstyle('round') for bar in bars]

# plt.show()
fig.tight_layout(pad=pad)
plt.savefig('sigmoid-tests-nice.pdf', bbox_inches = 'tight')
