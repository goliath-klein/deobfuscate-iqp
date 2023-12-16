import galois
import numpy as np
from lib.utils import dumpToUuid
from lib.construction import stabilizer_construction, qrc_construction
import pickle
from lib.new_attacks import lazyLinearityAttack

GF = galois.GF(2)

#### qrc construction

def testQrcAttack(q,m,n,N=10,**kwargs):

    for i in range(N):
        print ("q, n =", q, n)

        H, secret = qrc_construction(n,m,q)
        secret = secret.T[0]

        s,_ = lazyLinearityAttack(H,**kwargs)

        if not np.all(s.T==secret):
            print(f"!! wrong secret.")
            dumpToUuid([H.tolist(),secret.tolist()])
        else:
            print("Success")

        print("",flush=True)

#### stabilizer construction

def testStabAttack(N=100,n=300,m=360,g=4,rowAlgorithm=3,**kwargs):
    for i in range(N):
        H, secret = stabilizer_construction(n, m, g, rowAlgorithm=rowAlgorithm)
        secret = secret.T[0]

        s,_ = lazyLinearityAttack(H,**kwargs)

        if not np.all(s==secret):
            print(f"!! wrong secret.")
            dumpToUuid([H.tolist(),secret.tolist()])
        else:
            print("Success")

        print("",flush=True)


# testStabAttack(N=50,n=300,m=360,g=4,rowAlgorithm=3,verbose=True)

q = 103
m = 2 * q
n = q# in [(q+1)/2, (3q+1)/2]
testQrcAttack(q,m,n,verbose=False)

exit()
