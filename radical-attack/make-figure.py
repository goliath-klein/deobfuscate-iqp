import numpy as np
import matplotlib.pyplot as plt
import scipy as sp

plt.rcParams['figure.figsize'] = (9,6)

n=300
m=360
g=4

# Critical region of a two-sided binomial test
#
# returns [l,u] s.t. any X=k outside of [l,u] would be rejected
# at level alpha for H0: X ~ Bin(n,p).
#
# (Chosen greedily to minimize u-l).
#
# Is there a simple way to get these out of scipy stats package?

def binomtest(n,p,alpha=.05):
    def binom(k,n,p):
        return( sp.special.comb(n,k)*p**k*(1-p)**(n-k) )

    def coverage(l,u,n,p):
        return( sum([binom(k,n,p) for k in range(int(l),int(u+1))]) )

    if binom(np.ceil(p*n),n,p) >= binom(np.floor(p*n),n,p):
        l = u = int(np.ceil(p*n))
    else:
        l = u = int(np.floor(p*n))

    while coverage(l,u,n,p) < (1-alpha):
        if (l==0) or (binom(u+1,n,p) >= binom(l-1,n,p)):
            u += 1
        else:
            l -= 1

        assert( l >= 0 )
        assert( u <= n )

    return( (l, u) )

# Simplified estimate of Prob[ success | w ]
def succEstimate(w):
    return( (1-2.**(-w))**(g+m-n) )

# critical region for binomial test
def binombars(k,N,w):
    p = succEstimate(w)
    interval = binomtest(N, p, alpha=.05)
    # max(_,0) gets rid of tiny negativities due to numerical errors
    return( [max(p-interval[0]/N,0), max(interval[1]/N-p,0)] ) 


# Import list of w's. Files are generated from raw data by analysis.sh
with open('w-for-failed-cases.lst', 'r') as f:
    wf=np.array([[int(x) for x in line.strip().split(' ')][0] for line in f])
    
with open('w-for-successful-cases.lst', 'r') as f:
    ws=np.array([[int(x) for x in line.strip().split(' ')][0] for line in f])



## For the theory curve
minw = 0; maxw=20  # min and max values of w to consider
wrange = np.arange(minw,maxw,.1) # fine-grained grid for the theory curve

## Draw the theory curve
fig, ax = plt.subplots()
ax.plot(wrange, [succEstimate(w) for w in wrange])
ax.set_title('Theoretical estimate of probability of success conditioned on $w$')
ax.set_xticks(range(minw,maxw+1))
ax.set_xlabel('$w$')

plt.savefig('sigmoid.pdf', bbox_inches = 'tight')


## Draw figure including data points

wsdata  = range(minw,maxw,2) # for m1, g even, only even w's can occur

# list with elements (w, #successes|w, #attempts|w)
wkns = [(w, sum(ws==w), sum(ws==w)+sum(wf==w)) for w in wsdata]

# empirical frequencies
ps = [k/n for (_,k,n) in wkns]

# critical region for binomial tests centered around theory curve
er = np.array([binombars(k,N,w) for (w,k,N) in wkns])


fig, ax = plt.subplots()

# theory curve
ax.plot(wrange, [succEstimate(w) for w in wrange])

# data points
ax.plot(wsdata, ps, 'o')

# critical region of binomial test
ax.errorbar(wsdata, [succEstimate(w) for w in wsdata], yerr=np.array(er).T, fmt='none')

ax.set_title('Probability of success given $w$')
ax.set_xticks(wsdata)
ax.set_xlabel('$w$')

plt.savefig('sigmoid-tests.pdf', bbox_inches = 'tight')
