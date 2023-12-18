import galois
import numpy as np
import datetime
import pickle 
import matplotlib.pyplot as plt
import json 
cmap = plt.get_cmap('viridis')
colors = cmap(np.arange(0,1,1/3.4))

import matplotlib.font_manager as font_manager
from matplotlib import rcParams

# Comment out for nice font
# font_dir = ['/$YourDirectory/fonts/Source_Sans_Pro']
# for font in font_manager.findSystemFonts(font_dir):
#     font_manager.fontManager.addfont(font)
# rcParams['font.family'] = 'Source Sans Pro'

SIZE=9
rcParams['font.size']=SIZE
rcParams['axes.titlesize']=SIZE
rcParams['axes.labelsize']=SIZE
rcParams['xtick.labelsize']=SIZE
rcParams['ytick.labelsize']=SIZE
rcParams['legend.fontsize']=SIZE
rcParams['figure.titlesize']=SIZE
markers = np.array(['o','D','^'])
marker_size = .6*np.array([1.5,1.5])
elinewidth = .5
capsize = 0

alpha = 1
alpha2 = .5
lw = 1.25
lw2 = 1.75

linestyle = np.empty(4,'object')
linestyle[0] = dict(
    linewidth=lw,
    dash_capstyle='round',
    linestyle='-',
    alpha=alpha
)
linestyle[1] = dict(
    linewidth=lw,
    linestyle='--',
    dash_capstyle='round',
    alpha=alpha2,
)

aspect_ratio = 2/3
pad=.5
width = 300 * 0.01389
figsize = (width, aspect_ratio*width)

fig,ax = plt.subplots(1,1,figsize=figsize)
alpha1 = .7 
alpha2 = .3

Instances = 100
step = 2
today = '2023-11-24'
pickleFilename =  "data/"+ today+\
                 f"_qrc_test_kernelAttack_adaptiveRange_step={step}_nTries={Instances}.pickle"
with open(pickleFilename, 'rb') as pickleFile:
    print("Reading   ", pickleFilename, " ...")
    Pars = pickle.load(pickleFile)
    Results = pickle.load(pickleFile)
    print("--- DONE --- DONE --- DONE ---")

cols = ['blue','orange','green','red']
qVals = Pars['qVals']
step = Pars['step']
plotRanges = Pars['plotRanges']

for i in range(4):
    q = qVals[i]
    # Opening JSON file
    f = open(f'data/fix_SB_{q}.json')
    # returns JSON object as 
    # a dictionary
    xCheng = []
    succes_prob = []
    data = json.load(f)
    for key in data.keys():
        xCheng.append(int(key))

        success = []
        for el in data[key]:
            success.append(el[0])
        succes_prob.append(np.array(success).mean())
    plt.plot(xCheng,succes_prob,**linestyle[1],color =colors[i],label=qVals[i])


for i in range(4):
    x = np.arange(*plotRanges[str(qVals[i])],step)
    ax.plot(x,np.mean(Results[i],axis=1),**linestyle[0],color=colors[i],label=qVals[i])
    print('q =',qVals[i])
    print('Start of success',np.min(x[np.nonzero(np.mean(Results[i],axis=1))]))
    
ax.set_xlabel(r'Number of qubits $n$')
ax.set_ylabel(r'Success probability')
ax.tick_params(direction='in')

ax.legend(frameon=False)
fig.tight_layout()
fig.savefig('fig/'+today+'_QRC_meyer_vs_radical_high_res.pdf')


