import galois
import numpy as np
from lib.utils import rank, solvesystem, dumpToUuid

#print("Please uncomment requested functionality at the end of this file.\n")

GF = galois.GF(2)

def recoverChallengeHammingRazor(p,endurance):
    n = 300; m=360;

    with open("challenge/challenge_H.txt") as f:
        H = GF([[int(x) for x in line.strip().split(' ')] for line in f])

    # return array with 1's on support of a
    def compress(a):
        return((a>0).astype(int))

    support = np.zeros(m)

    for _ in range(endurance):
        Sc = np.random.rand(m) > p
        HSc = H[Sc,:]

        K = HSc.null_space().T

        support = compress(support + np.array(H@K)@np.ones(K.shape[1]))

    print(f"Found {sum(support)} candidates for redundant rows")

    sol = solvesystem(H,GF(np.ones(m,int)-support))
    if (len(sol)==0):
        print("!! Can't realize support pattern linearly")
        s=False
    else:
        s=sol[0]
        print("Hamming's Razor believes the secret to be")
        print(s)

    return (s)


recoverChallengeHammingRazor(p=.25,endurance=60)