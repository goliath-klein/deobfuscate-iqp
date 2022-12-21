from typing import Union, Optional, Tuple
import numpy as np
from numpy.random import default_rng
import galois
from .utils import solvesystem, wrap_seed, rank, lempel_sequence
import itertools

GF = galois.GF(2)

__all__ = [
    "random_main_part", "random_gram", "random_tableau",
    "add_row_redundancy", "add_col_redundancy", "Factorization", 
    "QRCConstruction", "generate_QRC_instance", "generate_stab_instance"
]

def random_main_part(n, g, s, seed = None):
    '''
    Randomly sample g rows that have inner products one with the secret s. 
    Args:
        n (int): number of qubits
        g (int): number of rows
        s (galois.FieldArray): secret vector
        seed (int | np.random.Generator): seed for random sampling
    Return:
        A random main part with g rows.
    '''
    assert len(s) == n, "Inconsistent shapes"
    H = []
    rng = wrap_seed(seed)
    while len(H) < g:
        # seed = int(rng.random() * 10**5)
        row = GF.Random(n, seed = rng)
        if np.dot(row, s) == 1:
            H.append(row)
    H = GF(H)

    return H

def random_gram(n, g, s, seed = None):
    '''
    Generate a random Gram matrix with rank <= g. It is generated by first sampling g rows that are not orthogonal to s, to form H. Then, G = H^T \cdot H
    Args:
        n (int): number of qubits
        g (int): number of rows
        s (galois.FieldArray): secret vector
        seed (int | np.random.Generator): seed for random sampling
    Return:
        A random Gram matrix generated by G = H^T \cdot H
    '''
    rng = wrap_seed(seed)
    H = random_main_part(n, g, s, seed = rng)
    G = H.T @ H

    return G

def random_tableau(n, g, s, seed = None):
    '''
    Generate a random stabilizer tableau whose X-part is the Gram matrix, and Z-part is identity. The Gram matrix has rank <= g. 
    Args:
        n (int): number of qubits
        g (int): number of rows
        s (galois.FieldArray): secret vector
        seed (int | np.random.Generator): seed for random sampling
    Return:
        A random stabilizer tableau. 
    '''
    rng = wrap_seed(seed)
    G = random_gram(n, g, s, seed = rng)
    x = GF.Random((n, 1), seed = rng)
    r = G @ x # to ensure that the overlap is not zero.
    stab_tab = np.hstack((G, GF.Identity(n), r))

    return stab_tab

def add_row_redundancy(H, s, size, seed = None):
    '''
    Given the main part and secret, append redundant rows (number of rows given by size).
    Args:
        H (galois.FieldArray): binary matrix to be appended redundant rows
        s (galois.FieldArray): secret vector
        size (int): number of redundant rows
        seed (int | np.random.Generator): seed for random sampling
    '''
    if size == 0:
        return H
    H_R = []
    n = H.shape[1]
    rng = wrap_seed(seed)
    while len(H_R) < size:
        row = GF.Random(n, seed = rng)
        if np.dot(row, s) == 0 and np.any(row != 0): # exclude all-zero rows
            H_R.append(row)

    return np.append(H, H_R, axis = 0)

def add_col_redundancy(H_M, s, size, seed = None):
    '''
    Given the main part and the secret, append random codewords to the columns of H_M. 
    Args:
        H_M (galois.FieldArray): binary matrix to be appended redundant columns
        s (galois.FieldArray): secret vector
        size (int): number of redundant columns
        seed (int | np.random.Generator): seed for random sampling
    Return:
        Tuple(H_M, s)
    '''
    if size == 0:
        return H_M, s
    ext_col = []
    n = H_M.shape[1]
    rng = wrap_seed(seed)
    while len(ext_col) < size:
        x = GF.Random((n, 1), seed = rng)
        codeword = H_M @ x # random linear combination of cols in H_M
        ext_col.append(codeword)

    ext_col: galois.FieldArray = np.hstack(ext_col)
    s_prime = ext_col.null_space()
    if len(s_prime) == 0:
        s_prime = GF.Zeros(size)
    else:
        s_prime = default_rng().choice(s_prime)

    new_H_M = np.hstack((H_M, ext_col)) # append random cols to the right of H_M
    new_s = np.append(s, s_prime)

    return new_H_M, new_s

def col_add(
    P: 'galois.FieldArray', 
    s: 'galois.FieldArray', 
    i: int, 
    j: int
) -> Tuple['galois.FieldArray', 'galois.FieldArray']:
    '''
    Add the j-th column of P to the i-th column, and add the i-th element of s to the j-th element.
    Args:
        P (galois.FieldArray): binary matrix
        s (galois.FieldArray): secret vector
        i (int): index of the first column
        j (int): index of the second column
    Return:
        Tuple(new_P, new_s)
    '''
    s_i = s[i]
    s_j = s[j]
    s_j = s_i + s_j
    s[j] = s_j

    P_i = P[:, i]
    P_j = P[:, j]
    P_i = P_i + P_j
    P[:, i] = P_i

    return P, s

def obfuscation(P, s, times, seed = None):
    '''
    Perform column operations on P and s.
    '''
    rng = wrap_seed(seed)
    n = P.shape[1]
    for _ in range(times):
        i, j = rng.choice(n, size = 2, replace = False)
        P, s = col_add(P, s, i, j)

    return P, s


class Factorization:
    def __init__(
        self, 
        tab: 'galois.GF(2)', 
        s: Optional['galois.GF(2)'] = None,
        random_state: Optional[Union[int, np.random.Generator]] = None
    ):
        '''
        Given a stabilizer tableau, return a factorization of the Gram matrix satisfying the weight and codeword constraints.
        '''
        self.tab = tab.copy()
        self.n = len(self.tab)
        G = tab[:, :self.n]
        assert np.all(G == G.T), "G must be symmetric"
        self.G = G 
        self.rng = wrap_seed(random_state)
        if s is None:
            s = self.self_consistent_eqn(one_sol=True) 
        self.s = s
        self.H_rand = None

    def get_weight(self): 
        '''
        Get weight constraint from the stabilizer tableau.
        '''
        weight_dict = {"00": 0, "01": 1, "10": 2, "11": 3}
        weights = []
        r = self.tab[:, 2*self.n]
        for i in range(self.n):
            weight = f"{r[i]}" + f"{self.G[i, i]}"
            weights.append(weight_dict[weight])
        return np.array(weights)

    def forward_evolution(self, row):
        '''
        Evolve the stabilizer tableau after applying e^{i pi X_p /4}. Internal use only.
        '''
        indices = row.nonzero()[0]
        for idx in indices: # update phase
            if self.tab[idx, idx] == 1:
                self.tab[idx, 2*self.n] += GF(1)
        for idx in itertools.product(indices, repeat = 2): # update gram matrix
            self.tab[idx] += GF(1)
        self.G = self.tab[:, :self.n]
        # self.__init__(self.tab, self.s)

    def backward_evolution(self, row):
        '''
        Evolve the stabilizer tableau after applying e^{-i pi X_p /4}. Internal use only.
        '''
        indices = row.nonzero()[0]
        for idx in indices: # update phase
            if self.tab[idx, idx] == 0:
                self.tab[idx, 2*self.n] += GF(1)
        for idx in itertools.product(indices, repeat = 2): # update gram matrix
            self.tab[idx] += GF(1)
        self.G = self.tab[:, :self.n]
        # self.__init__(self.tab, self.s)

    def randomization(self, n_rows):
        '''
        Randomization of stabilizer tableau
        '''
        if n_rows == 0:
            return 
        H_rand = random_main_part(self.n, n_rows, self.s, seed = self.rng)
        for row in H_rand:
            self.backward_evolution(row)
        if self.H_rand is None:
            self.H_rand = H_rand
        else:
            self.H_rand = np.vstack((self.H_rand, H_rand))

    def init_factor(self, n_rows = None):
        '''
        Construct the initial factorization, based on [Lempel 75]. 
        '''
        row_sum = np.sum(self.G, axis = 1)
        N1 = np.nonzero(row_sum)[0] # idx for odd-parity rows

        E = GF.Zeros((len(N1), self.n))
        for i in range(len(N1)):
            E[i, N1[i]] = 1 # part corresponding to N1
        
        for i in range(self.n): # part corresponding to N2
            for j in range(i+1, self.n):
                if self.G[i, j] == 1:
                    tmp = GF.Zeros((1, self.n))
                    tmp[0, [i, j]] = 1, 1
                    E = np.append(E, tmp, axis = 0)
        if n_rows is None:
            lempel_seq = lempel_sequence(E)
            idx = self.rng.choice(len(lempel_seq))
            return lempel_seq[idx]
        else:
            H_init = lempel_sequence(E, n_rows)
            return H_init

    def satisfy_weight_constraint(self, E):
        '''
        Make the factor satisfy the weight constraint. 
        '''
        weights = np.sum(E.view(np.ndarray), axis = 0) % 4 # weights of columns of E mod 4
        weight_diff = (self.get_weight() - weights) % 4
        if np.all(weight_diff == 0) == True:
            return E
        rows = GF.Zeros((2, self.n))
        for i in range(self.n):
            if weight_diff[i] != 0:
                rows[:, i] = GF.Ones(2)
        E = np.append(E, rows, axis = 0)
        return E
    
    def self_consistent_eqn(self, one_sol = False):
        '''
        Generte solutions of self-consistent equation G.s = (|c_1|, ..., |c_n|)^T. 
        If one_sol = True, output a random vector from the solution space
        '''
        w = GF([self.G[i, i] for i in range(self.n)])
        candidate = solvesystem(self.G, w, all_sol=True) # solutions of G.s = w
        if one_sol == True:
            idx = self.rng.choice(len(candidate))
            return candidate[idx]
        else:
            return candidate

    def injecting_ones(self, E):
        '''
        Injection subroutine to inject the all-one codeword.
        '''
        indicator = E @ self.s.reshape(-1, 1) # indicator to separate two parts
        F = E[indicator.nonzero()[0]] # F.s = 1
        Z = E[np.where(indicator == 0)[0]] # Z.s = 0
        if len(Z) % 2 != 0:
            zeros = GF.Zeros((1, self.n))
            Z = np.append(Z, zeros, axis = 0)
        x = GF.Zeros(self.n)
        flip_idx = self.rng.choice(self.s.nonzero()[0]) # only a special case
        x[flip_idx] = 1
        ones = GF.Ones((len(Z), 1))
        Z = Z + ones @ x.reshape(1, -1)
        return np.append(F, Z, axis = 0)

    def final_factor(self, n_rows = None, rand_rows = 0):
        '''
        Combine the subroutines to generate the final factorization.
        Args:
            idx: index of the lempel sequence
            rand_rows: for stabilizer tableau randomization
        '''
        self.randomization(rand_rows)
        if n_rows is not None:
            E_init = self.init_factor(n_rows - rand_rows)
        else:
            E_init = self.init_factor()
        E = self.satisfy_weight_constraint(E_init)
        H = self.injecting_ones(E)
        H = self.satisfy_weight_constraint(H)
        if self.H_rand is None:
            return H
        else:
            return np.vstack((self.H_rand, H))


class QRCConstruction:
    def __init__(self, q):
        # a valid q can be obtained from lib.construction.q_helper
        assert (q+1)%8 == 0, "(q + 1) must divide 8"
        self.q = q # size parameter
        self.n = int((q+1)/2) # num of qubits
        self.P_s = self.init_main() # initial main part
        self.s, _ = solvesystem(self.P_s, GF.Ones(q)) # initial secret

    def quad_res(self):
        '''
        Generate the list of quadratic residues modulo 1.
        '''
        QRs = []
        for m in range(self.q):
            QRs.append(m**2% self.q)
        QRs.pop(0)
        return list(set(QRs))

    def init_main(self):
        '''
        Generate initial main part
        '''
        P_s = GF.Zeros((self.q, self.n))
        QRs = self.quad_res() # the list of quadratic residues
        for col in range(self.n):
            for qr in QRs:
                P_s[(qr - 1 + col)%self.q, col] = 1
        return P_s


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


def generate_QRC_instance(
    q: int, 
    rd_row: int = 0, 
    rd_col: int = 0,
    verbose: bool = False
):
    '''
    Args:
        q: size parameter for QRC
        rd_row: number of redundant rows
        rd_col: number of redundant columns
        verbose: whether to print the info
    '''
    QRC = QRCConstruction(q) # initialization
    H_M = QRC.P_s
    s = QRC.s
    H_M, s = add_col_redundancy(H_M, s, rd_col)
    H = add_row_redundancy(H_M, s, rd_row)
    H, s = obfuscation(H, s, 1000)
    if verbose:
        print("rank of H_M:", rank(H_M), "\trank of H:", rank(H), "\tshape of H:", H.shape)

    return H, s


def generate_stab_instance(
    n: int,
    g: int,
    exp_nullity: int = 0,
    verbose: bool = False
):
    '''
    Generate an instance of stabilizer construction, s.t. the number of rows in the main part and the redundant part are the same. 
    Args:
        n_init: number of columns (qubits)
        g: the rank of the Gram matrix
        exp_nullity: the expected nullity, which is n-m/2
        verbose: whether to print the info
    '''
    n_cols_main = default_rng().choice(range(int(n/2), n+1))
    s = GF.Random(n_cols_main)
    tab = random_tableau(n_cols_main, g, s)
    stab_ins = Factorization(tab, s)

    n_rows_main = n - exp_nullity
    n_rand_rows = default_rng().choice(range(int(n_rows_main/5)))
    H_M = stab_ins.final_factor(n_rows = n_rows_main, rand_rows = n_rand_rows)
    shape_before = H_M.shape
    rd_col = n - n_cols_main
    H_M, s = add_col_redundancy(H_M, s, rd_col)
    H = add_row_redundancy(H_M, s, H_M.shape[0])
    H, s = obfuscation(H, s, 1000)
    if verbose:
        print("shape of H_M before adding redundancy:", shape_before)
        print("rank of H_M:", rank(H_M), "\trank of H:", rank(H), "\tshape of H:", H.shape)

    return H, s