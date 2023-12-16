import galois
import numpy as np
from lib.utils import dumpToUuid
from lib.new_attacks import hammingRazor

GF = galois.GF(2)

def recoverChallengeHammingRazor(**kwargs):
    n = 300; m=360;

    with open("challenge/challenge_H.txt") as f:
        H = GF([[int(x) for x in line.strip().split(' ')] for line in f])

    return hammingRazor(H,**kwargs)


print(recoverChallengeHammingRazor(p=.25,endurance=60,verbose=True))
