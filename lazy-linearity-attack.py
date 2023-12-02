import galois
import numpy as np
from lib.utils import rank, solvesystem, dumpToUuid,wrap_seed
from lib.construction import initialization, stabilizer_construction, qrc_construction, sample_parameters
from lib.attack import property_check,iter_column_space,get_H_s
import pickle

#print("Please uncomment requested functionality at the end of this file.\n")

GF = galois.GF(2)


def lazyLinearityAttack(
        H: "galois.FieldArray", 
        g_thres: int = 5, 
        endurance: int = 1000, 
        ambition: int = 8, 
        seed = None,
        verbose = True
    ):
    rng = wrap_seed(seed)
    count = 0
    kers = []

    while count < endurance:
        if verbose:
            print('count=',count)
        d = GF.Random(H.shape[1], seed = rng)
        H_d = get_H_s(H, d)
        G_d = H_d.T @ H_d
        ker_Gd = G_d.null_space()
        if verbose:
            print("Dimension of ker(G_d): ", len(ker_Gd))
        ker_Gd_space = iter_column_space(ker_Gd.T)

        if len(ker_Gd) > ambition:
            if verbose:
                print('Kernel too big, unambitiously skipping it.')
            count+=1
        else:
            for s_i in ker_Gd_space:
                count += 1
                check_res = property_check(H, s_i, g_thres)
                if check_res:
                    if verbose:
                        print('Found a secret.')
                    return s_i, count
                if count >= endurance:
                    break
    if verbose:
        print('Ran out of steam')
    return None, endurance


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

    exit()

#### stabilizer construction

def testStabAttack(N=100,n=300,m=360,g=4,rowAlgorithm=3):
    for i in range(N):
        H, secret = stabilizer_construction(n, m, g, rowAlgorithm=rowAlgorithm)
        secret = secret.T[0]

        s,_ = lazyLinearityAttack(H)

        if not np.all(s==secret):
            print(f"!! wrong secret.")
            dumpToUuid([H.tolist(),secret.tolist()])
        else:
            print("Success")

        print("",flush=True)


#testStabAttack(N=50,n=300,m=360,g=4,rowAlgorithm=3)
q = 103
m = 2 * q
n = q# in [(q+1)/2, (3q+1)/2]
testQrcAttack(q,m,n,verbose=False)

exit()
