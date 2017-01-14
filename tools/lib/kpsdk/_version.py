# Keypirinha launcher (keypirinha.com)
# Copyright 2013-2017 Jean-Charles Lefebvre <polyvertex@gmail.com>

import re

__all__ = ["Version"]

class Version:
    """
    A helper class that allows to parse and validate the version numbers of
    Keypirinha and its packages.
    """
    ZERO = (0, )

    MAJOR_MULTIPLIER = 10000000
    MINOR_MULTIPLIER = 10000
    PATCH_MULTIPLIER = 1

    def __init__(self, init_value=None):
        self.tupl = self.ZERO
        if init_value is not None:
            self.set(init_value)

    def __repr__(self):
        return "{}('{}')".format(self.__class__.__name__, str(self))

    def __str__(self):
        return self.getstr()

    def __len__(self):
        return len(self.tupl)

    def __bool__(self):
        return self.tupl > self.ZERO

    def __lt__(self, other):
        return self._cmp(other, "__lt__")

    def __le__(self, other):
        return self._cmp(other, "__le__")

    def __eq__(self, other):
        return self._cmp(other, "__eq__")

    def __ne__(self, other):
        return self._cmp(other, "__ne__")

    def __gt__(self, other):
        return self._cmp(other, "__gt__")

    def __ge__(self, other):
        return self._cmp(other, "__ge__")

    def set(self, init_value):
        # build tuple
        if isinstance(init_value, self.__class__):
            elems = list(init_value.tupl)
        elif isinstance(init_value, list):
            elems = init_value
        elif isinstance(init_value, tuple):
            elems = list(init_value)
        elif isinstance(init_value, int):
            elems = None
            if init_value > 0:
                elems = [0, 0, 0]
                elems[0], init_value = divmod(init_value, self.MAJOR_MULTIPLIER)
                elems[1], init_value = divmod(init_value, self.MINOR_MULTIPLIER)
                elems[2], init_value = divmod(init_value, self.PATCH_MULTIPLIER)
                assert(init_value == 0)
        elif isinstance(init_value, str):
            elems = None
            # quite flexible regex to deal with git-style tag names (i.e. "v1.2.3")
            rem = re.match(r"^[vV]?(\d+(?:\.\d+)*)(?:\-([a-zA-Z0-9][\w\-\.]+))?$", init_value, re.ASCII)
            if rem:
                elems = list(map(int, rem.group(1).split(".")))
        else:
            raise TypeError("unsupported init_value type")

        # validate tuple and setup member
        # * Note that combined version is an uint32_t (i.e. max is 429,496,7295)
        #   so Major version must be <=428 (i.e. not <=429) to ensure that Minor
        #   and Patch are not out of boundaries.
        if (isinstance(elems, list) and
                1 <= len(elems) <= 3 and
                all(isinstance(n, int) for n in elems) and
                0 <= elems[0] <= 428 and
                (len(elems) < 2 or 0 <= elems[1] <= 999) and
                (len(elems) < 3 or 0 <= elems[2] <= 9999)):
            while not elems[-1]:
                elems.pop()
            self.tupl = tuple(elems)
        else:
            raise ValueError("invalid init_value")

    def getstr(self, prefix="v", suffix="", sep=".", full=False):
        return prefix + sep.join(map(str, self.gettuple(full=full))) + suffix

    def getwinstr(self):
        # Microsoft's version format: "M,m,p,0"
        return self.getstr(prefix="", suffix="", sep=",", full=4)

    def getint(self):
        ft = self.gettuple(full=True)
        return (
            (ft[0] * self.MAJOR_MULTIPLIER) +
            (ft[1] * self.MINOR_MULTIPLIER) +
            (ft[2] * self.PATCH_MULTIPLIER))

    def gettuple(self, full=False):
        count = len(self.tupl) if not full else 3
        if isinstance(full, int) and full > len(self.tupl):
            count = full
        return self.tupl + (0, ) * (count - len(self.tupl))

    def _cmp(self, other, opname):
        if isinstance(other, self.__class__):
            valid_other = other
        else:
            valid_other = self.__class__(other)
        ft = self.gettuple(full=True)
        op = getattr(ft, opname)
        return op(valid_other.gettuple(full=True))

if __name__ == "__main__":
    if not __debug__:
        raise Exception("debug mode not enabled")
    assert(not Version())
    assert(Version("2") == Version(20000000))
    assert(Version("2.3") < Version(4289999999))
    assert(Version("2.3") < 4289999999)
    assert(Version("2.3") == (2, 3))
    assert(Version("2.3") == (2, 3, 0))
    assert(Version("v2.3") == (2, 3))
    assert(Version("428.999.9999") == Version(4289999999))
    assert(Version() < Version("0.1"))
    assert(Version(Version("2.3")) == Version("2.3"))
