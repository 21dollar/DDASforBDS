import os
import random
from random import randint

from DBIT import DbitDao, DbitRepository
from network import NetworkNode

from utils import *


class DO(NetworkNode):
    def __init__(self):
        super(DO, self).__init__('DO', '127.0.0.1')
        self.pk = (0, 0)
        self.sk = (0, 0)
        self.DbitRepository = DbitRepository()
        self.setUp()

    def setUp(self):
        p, q = load_private_key(self.name)
        N, g = load_public_key(self.name)
        self.pk = (N, g)
        self.sk = (p, q)

        release_public_key(self.name)


    def tagGen(self, filename):
        DO_filename = os.path.join(self.name, filename)
        data = read_pad_data(DO_filename)

        m = split_message(data)

        t = [concat_int_blocks(mi, i, i, 1) for i, mi in enumerate(m, start=1)]
        N, g = self.pk
        T = [pow(g, ti, N) for ti in t]

        print('|   mi  | R | L | V | T          ')
        print('|=======|===|===|===|====== = = =')
        for i, (mi, Ti) in enumerate(zip(m, T), start=1):
            print('| %5d | %d | %d | %d | %s '%(mi, i, i, 1, hex(Ti)))
        
        self.DbitRepository.clear()
        self.DbitRepository.insert(DbitDao(i, i, 1, Ti) for i, Ti in enumerate(T, start=1))

        release_tags(T)

        SP_filename = os.path.join('SP', filename)
        write_unpad_data(SP_filename, data)


    def insert(self, data : bytes, after_Ri : int):
        afterBlock = self.DbitRepository.selectByR(after_Ri)[0]
        m = split_message(data)

        self.DbitRepository.incLiIfMoreThan(afterBlock.L, diff=len(m))
        Ndbit = self.DbitRepository.count()

        t = [concat_int_blocks(mi, Ndbit + i, afterBlock.L + i, 1) for i, mi in enumerate(m, start=1)]
        N, g = self.pk
        T = [pow(g, ti, N) for ti in t]

        self.DbitRepository.insert(
            DbitDao(Ndbit + i, afterBlock.L + i, 1, Ti) 
            for i, Ti in enumerate(T, start=1)
        )

    def append(self, data : bytes):
        m = split_message(data)
        Ndbit = self.DbitRepository.count()
        t = [concat_int_blocks(mi, Ndbit + i, Ndbit + i, 1) for i, mi in enumerate(m, start=1)]
        N, g = self.pk
        T = [pow(g, ti, N) for ti in t]

        self.DbitRepository.insert(
            DbitDao(Ndbit + i, Ndbit + i, 1, Ti) 
            for i, Ti in enumerate(T, start=1)
        )

    def update(self, data : bytes, update_Ri : int):
        updateBlock = self.DbitRepository.selectByR(update_Ri)[0]
        m = split_message(data)[0]
        Ndbit = self.DbitRepository.count()

        t = concat_int_blocks(m, Ndbit + 1, updateBlock.L, 2)
        N, g = self.pk
        T = pow(g, t, N)

        self.DbitRepository.insert(
            DbitDao(Ndbit + 1, updateBlock.L, 2, T)
        )

    def delete(self, delete_Ri : int):
        self.DbitRepository.updateViByR(delete_Ri, -1)

    def print_DBIT(self):
        print(self.DbitRepository)


class TPA(NetworkNode):
    def __init__(self):
        super(TPA, self).__init__('TPA', '127.0.0.1')
        self.r = 0
        self.s = 0

    def challenge(self):
        N, g = load_public_key()
        k = N.bit_length()
        self.r = randint(1, 2**k - 1)
        self.s = randint(1, N)
        gs = pow(g, self.s, N)
        chal = (self.r, gs)
        print('chal = (r, gs) =', chal)
        self.send_to('SP', chal)

    def checkProof(self):
        name, R = self.recv_from()
        print(name, '->', self.name, ':', R)

        N, g = load_public_key()
        tags = load_tags()
        n = len(tags)

        random.seed(self.r)
        a = [randint(1, N) for _ in range(n)]
        print('a =', a)

        prod = 1
        for tag, ai in zip(tags, a):
            prod = prod * pow(tag, ai, N) % N

        R_ = pow(prod, self.s, N)
        print("R' =", R_)

        if R == R_:
            print("R == R'")
            return "success"
        else:
            print("R != R'")
            return "failure"


    
class SP(NetworkNode):
    def __init__(self):
        super(SP, self).__init__('SP', '127.0.0.1')

    def genProof(self, filename):
        name, chal = self.recv_from()
        print(name, '->', self.name, ':', chal)
        r, gs = chal

        N, g = load_public_key()

        SP_filename = os.path.join(self.name, filename)
        data = read_pad_data(SP_filename)

        m = split_message(data)
        n = len(m)

        #TODO: исправить на запрос из бд или откуда-нибудь
        t = [concat_int_blocks(mi, i, i, 1) for i, mi in enumerate(m, start=1)]

        random.seed(r)
        a = [randint(1, N) for _ in range(n)]
        print('a =', a)

        S = sum(ai*ti for ai, ti in zip(a, t))

        R = pow(gs, S, N)
        self.send_to('TPA', R)
        print('R =', R)



do = DO()
tpa = TPA()
sp = SP()

do.setUp()
do.tagGen('file.txt')
print()

#PROOFING
print('=== PROOFING ===')
print('TPA:')
tpa.challenge()
print()

print('SP:')
sp.genProof('file.txt')
print()

print('TPA:')
print(tpa.checkProof())
print('\n')


#UPDATE OPERATIONS:
print('=== UPDATE OPERATIONS ===')
print('BEFORE:')
do.print_DBIT()
print()

print('INSERT: after R = 4')
do.insert(b'al', 4)
do.print_DBIT()
print()

print('APPEND:')
do.append(b'!')
do.print_DBIT()
print()

print('UPDATE: R = 3')
do.update(b'oo', 3)
do.print_DBIT()
print()

print('DELETE: R = 4')
do.delete(4)
do.print_DBIT()
print()
