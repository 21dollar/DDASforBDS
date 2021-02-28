from BaseRepository import BaseRepository, BaseDao

class DbitDao(BaseDao):
    def __init__(self, R, L, V, T):
        self.R = R
        self.L = L
        self.V = V
        self.T = T

    def __str__(self):
        return ' %2d | %2d | %2d | %2s ' % (self.R, self.L, self.V, self.T)
        
    def __repr__(self):
        return self.__str__()
        
    def dump(self):
        return (self.R, self.L, self.V, hex(self.T)[2:])

class DbitRepository(BaseRepository):
    TABLE_NAME = 'DBIT'
    TABLE_PARAM = ['R', 'L', 'V', 'T']
    BASE_TYPE = DbitDao

    def __init__(self):
        super(DbitRepository, self).__init__()

    #=== COSTOM QUERIES ===

    def deleteByR(self, Ri):
        query = f'''delete {self.TABLE_NAME} where R = (?)'''
        self.query(query, Ri)

    def selectByR(self, Ri):
        query = f'''select * from {self.TABLE_NAME} where R = (?)'''
        return self.queryForObject(query, Ri, wrapper=DbitDao)

    def incLiIfMoreThan(self, Li, diff = 1):
        query = f'''update {self.TABLE_NAME} set L = L + (?) where L > (?)'''
        self.query(query, diff, Li)

    def updateViByR(self, Ri, Vi):
        query = f'''update {self.TABLE_NAME} set V = (?) where R = (?)'''
        self.query(query, Vi, Ri)


