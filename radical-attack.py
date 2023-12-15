import galois
import numpy as np
from lib.utils import dumpToUuid
from lib.construction import stabilizer_construction, qrc_construction
import pickle
from lib.new_attacks import radicalAttack

GF = galois.GF(2)

#print("Please uncomment requested functionality at the end of this file.\n")
    
#### qrc construction
def testQrcAttack(q,m,n,N=10,**kwargs):

    for i in range(N):
        print ("q, n =", q, n)

        H, secret = qrc_construction(n,m,q)
        secret = secret.T[0]

        s,_ = radicalAttack(H,**kwargs)

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

        s,_ = radicalAttack(H,**kwargs)

        if not np.all(s==secret):
            print(f"!! wrong secret.")
            dumpToUuid([H.tolist(),secret.tolist()])
        else:
            print("Success")

        print("",flush=True)


### recover challenge secret

def recoverChallenge(save=False,**kwargs):
    n = 300; m=360;

    with open("challenge/challenge_H.txt") as f:
        H = GF([[int(x) for x in line.strip().split(' ')] for line in f])
    s,_ = radicalAttack(H,**kwargs)

    if save:
        print("\nSaving the secret")
        file =  "secret.pickle"
        with open(file, 'wb') as file:
            pickle.dump(s,file)

    return s
 
recoverChallenge()

# testStabAttack(N=50,n=300,m=360,g=4,rowAlgorithm=3)

# q = 103
# m = 2 * q
# r = int((q+1)/2)
# n = q +r # in [r, q + r]
# testQrcAttack(q=q,n=n,m=m)

exit()
