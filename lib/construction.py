import numpy as np
from numpy.random import default_rng
import galois

from lib.utils import check_element, rank, sample_column_space, hamming_weight, solvesystem, rand_inv_mat
from lib.gen_matrix import sample_D, sample_F

GF = galois.GF(2)


def sample_parameters(n, m, g):
    for _ in range(30):
        tmp = [i for i in range(g, m, 2) if i >= 4 and i > g] # m1 = g mod 2, m1 > g
        m1 = default_rng().choice(tmp)
        d = default_rng().choice(range(1, int((m1-g)/2)+1)) # g + 2*d <= m1
        if g + d <= n and n - g - d <= m - m1:
            break

    return m1, d


def add_row_redundancy(H_s: "galois.FieldArray", s: "galois.FieldArray", m2: int):
    """
    Generating R_s so that R_s.s = 0 and the joint row space of H_s and R_s is n
    """
    n = H_s.shape[1]
    r = rank(H_s)

    row_space_H_s = H_s.row_space()
    s_null_space = s.reshape((1, -1)).null_space()

    full_basis = row_space_H_s
    for p in s_null_space:
        if not check_element(row_space_H_s.T, p):
            full_basis = np.concatenate((full_basis, p.reshape(1, -1)), axis=0)

    R_s = full_basis[r:] # guarantee that rank(H) = n

    while R_s.shape[0] < m2:
        p = sample_column_space(s_null_space.T)
        if hamming_weight(p) != 0:
            R_s = np.concatenate((R_s, p.T), axis=0)

    return R_s


def initialization(n, m, g, m1=None, d=None):
    """
    Initialization of the construction, where H_s = (F, D, 0) 
    """
    if m1 is None or d is None:
        m1, d = sample_parameters(n, m, g)
    print("m1, d:", m1, d)
    D = sample_D(m1, d)
    zeros = GF.Zeros((m1, n-g-D.shape[1]))
    if g == 0:
        H_s = np.concatenate((D, zeros), axis=1)
    else:
        F = sample_F(m1, g, D)
        H_s = np.concatenate((F, D, zeros), axis=1)

    u = GF.Ones((m1, 1))
    s = solvesystem(H_s, u)[0]

    R_s = add_row_redundancy(H_s, s, m-m1)
    H = np.concatenate((H_s, R_s), axis=0)

    return H, s.reshape(-1, 1)


def obfuscation(H: "galois.FieldArray", s: "galois.FieldArray"):
    """
    H <-- P H Q and s <-- Q^{-1} s, 
    where P is a random permutation matrix 
    and Q is a random invertible matrix
    """
    H = default_rng().permutation(H).view(GF) # row permutations

    Q = rand_inv_mat(H.shape[1])
    H = H @ Q # column operations
    s = np.linalg.inv(Q) @ s

    return H, s


def stabilizer_construction(n, m, g, m1=None, d=None):
    """
    Generate an IQP matrix H and a secret s, so that the correlation function is 2^{-g/2}
    """
    H, s = initialization(n, m, g, m1, d)
    H, s = obfuscation(H, s)

    return H, s


def quad_res_mod_q(q):
    '''
    Generate the list of quadratic residues modulo q.
    '''
    QRs = []
    for m in range(q):
        QRs.append(m**2 % q)
    QRs.pop(0)
    return list(set(QRs))


def qrc_construction(n, m, q):
    """
    construct QRC-IQP instance
    """
    m1 = q
    r = int((q+1)/2) # dim of QRC

    H_s = GF.Zeros((q, r))
    QRs = quad_res_mod_q(q) # the list of quadratic residues
    for i in range(r):
        for qr in QRs:
            H_s[(qr - 1 + i)%q, i] = 1

    if n > r:
        zeros = GF.Zeros((q, n-r))
        H_s = np.concatenate((H_s, zeros), axis=1)

    u = GF.Ones((m1, 1))
    s = solvesystem(H_s, u)[0]

    R_s = add_row_redundancy(H_s, s, m-m1)
    H = np.concatenate((H_s, R_s), axis=0)

    H, s = obfuscation(H, s)

    return H, s.reshape(-1, 1)


def is_prime(n):
    if n % 2 == 0 and n > 2: 
        return False
    return all(n % i for i in range(3, int(np.sqrt(n)) + 1, 2))

def q_helper(N):
    '''
    Return the list of valid q smaller than N for QRC.
    '''
    assert type(N) == int, "N must be integer"
    a = np.arange(7, N, 8)
    foo = np.vectorize(is_prime)
    pbools = foo(a)
    q_list = np.extract(pbools, a)
    return q_list

    # [7, 23, 31, 47, 71, 79, 103, 127, 151, 167, 191, 199, 223,  239, 263, 271, 311, 359, 367, 383, 431, 439, 463, 479, 487, 503,  599, 607, 631, 647, 719, 727, 743, 751, 823, 839, 863, 887, 911,  919, 967, 983, 991]