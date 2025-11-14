"""
RegAlloc sencillo para MIPS:
- Usa $t0..$t9 para temporales.
- Mapa nombre_TAC -> registro.
- Si se agotan, "presta" uno en uso (mejorar a futuro con spill).
"""

class _Pool:
    def __init__(self):
        self.all = ["$t0","$t1","$t2","$t3","$t4","$t5","$t6","$t7","$t8","$t9"]
        self.free = self.all[:]
        self.inuse = []

    def acquire(self):
        if self.free:
            r = self.free.pop(0)
            self.inuse.append(r)
            return r
        # Sencillo: presta el primero en uso (mejorar con spills reales)
        return self.inuse[0] if self.inuse else "$t9"

    def release(self, reg):
        if reg in self.inuse:
            self.inuse.remove(reg)
            if reg not in self.free and reg in self.all:
                self.free.append(reg)

class RegAlloc:
    def __init__(self):
        self.pool = _Pool()
        self.name2reg = {}

    def reset(self):
        self.pool = _Pool()
        self.name2reg = {}

    def get(self, name):
        if name in self.name2reg:
            return self.name2reg[name]
        r = self.pool.acquire()
        self.name2reg[name] = r
        return r

    def free_name(self, name):
        if name in self.name2reg:
            r = self.name2reg.pop(name)
            self.pool.release(r)
