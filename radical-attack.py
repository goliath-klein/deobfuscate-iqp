import galois
import numpy as np
from lib.utils import rank, solvesystem, dumpToUuid
from lib.construction import initialization, stabilizer_construction, qrc_construction, sample_parameters
import pickle

#print("Please uncomment requested functionality at the end of this file.\n")

GF = galois.GF(2)

def radicalAttack(H):
    print("Attack commencing...")
    n = H.shape[1]
    G = H.T @ H
    toKer = G.null_space().T

    dimKer = n-rank(G)
    if dimKer == 0:
        print("!! dim ker G = 0, aborting")
        return (False,False)

    print("dim ker G =", dimKer)

    hammings = [sum(v.tolist()) for v in (H@toKer).T]
    if  not all([x%4==0 for x in hammings]):
        # This is a minimalist hack.
        # One should actually construct a basis of a maximal doubly-even subspace.
        # But it does work for us on the challenge data set 
        # (though this might depend on the specific implementation of null_space())
        print("!! Some generators aren't doubly-even. Will throw them out.")
        toKer = ((toKer.T)[[h % 4==0 for h in hammings]]).T

        if toKer.size == 0:
            print("!! nothing left after throwing out singly-even generators")
            return (False,False)
    
    coordinateOccupation = sum(np.array((H@toKer).T))
    S = GF([1 if x>0 else 0 for x in coordinateOccupation])

    sol = solvesystem(H,S)
    if (len(sol)==0):
        print("!! Can't realize support pattern linearly")
        s=False
    else:
        s=sol[0]

    return (s,S)


#### qrc construction

def testQrcAttack(N=10):
    for q in [103,127, 151, 167,223]:
        r = int((q+1)/2)
        m = 2*q
        n = r+q

        for i in range(N):
            print ("q, n =", q, n)

            H, secret = qrc_construction(n,m,q)
            secret = secret.T[0]

            s,_ = radicalAttack(H)

            if not np.all(s==secret):
                print(f"!! wrong secret.")
                dumpToUuid([H.tolist(),secret.tolist()])
            else:
                print("Success")

            print("",flush=True)

    exit()

#### stabilizer construction

def testStabAttack(N=100,n=300,m=360,g=4,rowAlgorithm=3):
    for i in range(N):
        H, secret = stabilizer_construction(n, m, g, rowAlgorithm=rowAlgorithm)
        secret = secret.T[0]

        s,_ = radicalAttack(H)

        if not np.all(s==secret):
            print(f"!! wrong secret.")
            dumpToUuid([H.tolist(),secret.tolist()])
        else:
            print("Success")

        print("",flush=True)


### recover challenge secret

def recoverChallenge(save=False):
    n = 300; m=360;

    with open("challenge/challenge_H.txt") as f:
        H = GF([[int(x) for x in line.strip().split(' ')] for line in f])

    s, S = radicalAttack(H)

    m1 = sum(S.tolist())

    Hs = GF([H[i] * S[i] for i in range(m)])
    r = rank(Hs)
    g = rank(Hs.T@Hs)
    Gs = Hs.T@Hs
    D = Hs@Gs.null_space().T
    d = rank(D)

    print(f"\nFound a code with parameters g={g}, d={d}, m_1={m1}, and doubly-even radical.")

    Rs = H - Hs
    print("\nIn notation of accompanying paper: rank(BC) - m2 =", (m-m1)-rank(Rs@Gs.null_space().T) )

    print("\nThe code is hiding behind the secret")
    print(s)

    if save:
        print("\nSaving the secret")
        file =  "secret.pickle"
        with open(file, 'wb') as file:
            pickle.dump(s,file)

    return s
 
recoverChallenge()
# # testStabAttack(N=50,n=300,m=360,g=4,rowAlgorithm=3)
#testQrcAttack()

exit()
