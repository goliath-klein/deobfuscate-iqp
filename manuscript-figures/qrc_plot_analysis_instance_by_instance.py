import galois
import numpy as np
import datetime
import pickle 
import matplotlib.pyplot as plt
import json 
cmap = plt.get_cmap('viridis')
colors = cmap(np.arange(0,1,1/3.5))
print(colors)
colors = colors[::-1]

import matplotlib.font_manager as font_manager
from matplotlib import rcParams

# font_dir = ['/$YOURDIRECTORY/fonts/Source_Sans_Pro']
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
linestyle[2] = dict(
    linewidth=lw,
    linestyle=':',
    dash_capstyle='round',
    alpha=alpha2,
)
linestyle[3] = dict(
    linewidth=lw,
    linestyle=':',
    dash_capstyle='round',
    alpha=.3*alpha,
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
E = 1000
A = 8
Qs = [103,127,151,167]#,223]
kfold = 1
gt = 1
date = '2023-12-04'

for i,q in enumerate(Qs[::-1]):

    pickleFilename =  "data/"+ date +\
                 f"_qrc_instance_by_instance_step={step}_nTries={Instances}"+\
                 f"_q={q}_ambition_{A}_endurance_{E}_gt_{gt}_kfold_{kfold}.pickle"

    # pickleFilename =  f"data/{date}_qrc_instance_by_instance_step={step}_nTries={Instances}_q={q}_ambition_{A}_endurance_{E}.pickle"
    # pickleFilename = f"data/{date}_qrc_instance_by_instance_step={step}_nTries={Instances}_q={q}_maxit={maxit}.pickle"
    with open(pickleFilename, 'rb') as pickleFile:
        print("Reading   ", pickleFilename, " ...")
        Pars = pickle.load(pickleFile)
        Results = pickle.load(pickleFile)
        ResultsMeyer = pickle.load(pickleFile)
        # kernelInstances = pickle.load(pickleFile)
        # meyerInstances = pickle.load(pickleFile)
        # failInstances = pickle.load(pickleFile)
        print("--- DONE --- DONE --- DONE ---")
    
    # cols = ['blue','orange','green','red']
    q = Pars['q']
    step = Pars['step']
    x = Pars['nVals']
    print()
    combinedResults = np.zeros((len(x),Instances))
    success_radical = np.nonzero(Results)
    success_meyer = np.nonzero(ResultsMeyer)
    combinedResults[success_radical] =1
    combinedResults[success_meyer] = 1

    # x = np.arange(*plotRanges[str(q)],step)
    ax.plot(x,np.mean(Results,axis=1),color=colors[i],**linestyle[1],label='Radical Attack')
    ax.plot(x,np.mean(ResultsMeyer,axis=1),color=colors[i],**linestyle[0],label='Meyer Attack')
    # ax.plot(x,np.mean(combinedResults,axis=1),color=colors[i],**linestyle[0],label='Combined Attack')

    
ax.set_xlabel(r'Number of qubits $n$')
ax.set_ylabel(r'Success probability')
ax.tick_params(direction='in')

ax.legend(frameon=False)
# ax.set_title(f'{Instances} instances/point, k = {kfold}')
# plt.show()
fig.tight_layout(pad=pad)
fig.savefig(f'fig/{date}_QRC_meyer_vs_radical_instance_by_instance_Qs={Qs}_N={Instances}_step_{step}_kfold_{kfold}_ambition_{A}_endurance_{E}.pdf')