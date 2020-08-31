# Copyright: copyright.txt
import logging
from conbyte.concolic_types.concolic import Concolic, MetaFinal
from conbyte.global_utils import py2smt, unwrap
from conbyte.concolic_types.concolic_bool import ConcolicBool

log = logging.getLogger("ct.con.int")

"""
Classes:
    ConcolicInt
"""

class ConcolicInt(int, Concolic, metaclass=MetaFinal):
    def __new__(cls, value, expr=None, engine=None):
        assert type(value) is int
        obj = super().__new__(cls, value)
        obj.expr = expr if expr is not None else py2smt(value)
        obj.engine = engine if engine is not None else Concolic._find_engine_in_expression(expr)
        # if isinstance(obj.expr, list):
        #     obj.expr = global_utils.add_extended_vars_and_queries('Int', obj.expr)
        log.debug("  ConInt, value: %s, expr: %s" % (obj, obj.expr))
        return obj

    def __abs__(self):
        value = int.__int__(self).__abs__()
        expr = ["ite", [">=", self, 0], self, ["-", 0, self]]
        return ConcolicInt(value, expr)

    # def __bool__(self):
    #     return int.__bool__(self)

    def __ceil__(self):
        if self.engine:
            return self
        else:
            return ConcolicInt(int.__int__(self))

    # def __divmod__(self, value):
    #     return int.__int__(self).__divmod__(value)

    def __eq__(self, other):
        if not isinstance(other, int): return ConcolicBool(False)
        value = int.__int__(self).__eq__(int.__int__(other))
        if not isinstance(other, ConcolicInt): other = ConcolicInt(other)
        expr = ["=", self, other]
        return ConcolicBool(value, expr)

    def __float__(self):
        from .concolic_float import ConcolicFloat
        value = int.__float__(self)
        return ConcolicFloat(value, ['to_real', self])

    def __floor__(self):
        if self.engine:
            return self
        else:
            return ConcolicInt(int.__int__(self).__floor__())

    def __format__(self, format_spec):
        return int.__int__(self).__format__(format_spec)

    def __ge__(self, other):
        value = int.__int__(self).__ge__(int.__int__(other))
        if not isinstance(other, ConcolicInt): other = ConcolicInt(other)
        expr = [">=", self, other]
        return ConcolicBool(value, expr)

    def __gt__(self, other):
        value = int.__int__(self).__gt__(int.__int__(other))
        if not isinstance(other, ConcolicInt): other = ConcolicInt(other)
        expr = [">", self, other]
        return ConcolicBool(value, expr)

    def __hash__(self):
        return hash(int.__int__(self))

    def __index__(self): # must return the primitive version for the use of low-level C functions
        return int.__int__(self)

    def __int__(self):
        if self.engine:
            return self
        else:
            return ConcolicInt(int.__int__(self))

    def __invert__(self):
        return ConcolicInt(int.__int__(self).__invert__())

    def __le__(self, other):
        value = int.__int__(self).__le__(int.__int__(other))
        if not isinstance(other, ConcolicInt): other = ConcolicInt(other)
        expr = ["<=", self, other]
        return ConcolicBool(value, expr)

    def __lt__(self, other):
        value = int.__int__(self).__lt__(int.__int__(other))
        if not isinstance(other, ConcolicInt): other = ConcolicInt(other)
        expr = ["<", self, other]
        return ConcolicBool(value, expr)

    def __ne__(self, other):
        value = int.__int__(self).__ne__(int.__int__(other))
        if not isinstance(other, ConcolicInt): other = ConcolicInt(other)
        expr = ["not", ["=", self, other]]
        return ConcolicBool(value, expr)

    def __neg__(self):
        value = -int.__int__(self)
        expr = ["-", 0, self]
        return ConcolicInt(value, expr)

    def __pos__(self):
        raise NotImplementedError

    def __pow__(self, value, mod=None):
        return int.__int__(self).__pow__(value, mod)
        raise NotImplementedError

    def __rand__(self, value):
        return int.__int__(self).__rand__(value)
        raise NotImplementedError

    def __rdivmod__(self, value):
        return int.__int__(self).__rdivmod__(value)
        raise NotImplementedError

    def __rfloordiv__(self, value):
        raise NotImplementedError

    def __rlshift__(self, value):
        return int.__int__(self).__rlshift__(value)
        raise NotImplementedError

    def __ror__(self, value):
        return int.__int__(self).__ror__(value)
        raise NotImplementedError

    def __round__(self):
        raise NotImplementedError

    def __rpow__(self, value, mod=None):
        raise NotImplementedError

    def __rrshift__(self, value):
        raise NotImplementedError

    def __rxor__(self, value):
        raise NotImplementedError

    # def __sizeof__(self):
        # raise NotImplementedError

    def __str__(self):
        from conbyte.concolic_types.concolic_str import ConcolicStr # put here to avoid circular import
        value = int.__str__(self)
        expr = ["int.to.str", self]
        return ConcolicStr(value, expr)

    def __truediv__(self, other):
        x = self.__float__()
        if isinstance(other, ConcolicInt):
            y = other.__float__()
        elif type(other) is float:
            from .concolic_float import ConcolicFloat
            y = ConcolicFloat(other)
        else:
            raise NotImplementedError
        return x / y # operation between two concolic floats

    def __trunc__(self):
        raise NotImplementedError

    def as_integer_ratio(self):
        raise NotImplementedError

    def bit_length(self):
        raise NotImplementedError

    def conjugate(self):
        raise NotImplementedError

    @classmethod
    def from_bytes(cls, bytes, byteorder, signed=False):
        raise NotImplementedError

    # def to_bytes(self, length, byteorder, signed=False):
        # raise NotImplementedError

    # custom method to get the primitive value
    def parent(self):
        return int.__int__(self)

    def __lshift__(self, value):
        return ConcolicInt(int.__int__(self).__lshift__(value))
        raise NotImplementedError

    # def __rshift__(self, value):
    #     raise NotImplementedError

ops = [("add", "+", "+"),
       ("sub", "-", "-"),
       ("mul", "*", "*"),
       ("mod", "%", "mod"),
    #    ("truediv", "/", "div"),
       ("floordiv", "//", "div"),
       ("and", "&", "&"),
       ("or", "|", "|"),
       ("xor", "^", "^")] #,
    #    ("lshift", "<<", "bvshl"),
    #    ("rshift", ">>", "bcshr")]

def make_method(method, op, op_smt):
    code = "def %s(self, other):\n" % method
    code += "   value = int.__int__(self) %s int(other)\n" % op
    code += "   if not isinstance(other, ConcolicInt):\n"
    code += "      other = ConcolicInt(other)\n"
    code += "   expr = [\"%s\", self, other]\n" % op_smt
    code += "   return ConcolicInt(value, expr)\n"
    locals_dict = {}
    exec(code, globals(), locals_dict)
    setattr(ConcolicInt, method, locals_dict[method])

for (name, op, op_smt) in ops:
    method = "__%s__" % name
    make_method(method, op, op_smt)
    # rmethod = "__r%s__" % name
    # make_method(rmethod, op, op_smt)

rops = [("radd", "+", "+"),
       ("rsub", "-", "-"),
       ("rmul", "*", "*"),
       ("rmod", "%", "mod"),
       ("rtruediv", "/", "div")]

def make_rmethod(method, op, op_smt):
    code = "def %s(self, other):\n" % method
    code += "   if type(other) is int:\n"
    code += "      other = ConcolicInt(other)\n"
    code += "      value = int.__int__(other) %s int.__int__(self)\n" % op
    code += "      expr = [\"%s\", other, self]\n" % op_smt
    code += "      return ConcolicInt(value, expr)\n"
    code += "   else:\n"
    code += "      value = other %s int.__int__(self)\n" % op
    code += "      if type(value) is int:\n"
    code += "         return ConcolicInt(value)\n"
    code += "      else:\n"
    code += "         return value\n"
    locals_dict = {}
    exec(code, globals(), locals_dict)
    setattr(ConcolicInt, method, locals_dict[method])

for (name, op, op_smt) in rops:
    method = "__%s__" % name
    make_rmethod(method, op, op_smt)
