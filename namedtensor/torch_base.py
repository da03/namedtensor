import torch
from .torch_helpers import NamedTensor
import opt_einsum as oe

_build = {"ones", "zeros", "randn"}

_unary = {
    "abs",
    "acos",
    "asin",
    "atan",
    "ceil",
    "cos",
    "cosh",
    "exp",
    "expm1",
    "log",
    "rsqrt",
    "sigmoid",
    "sign",
    "sin",
    "sinh",
    "sqrt",
    "tan",
    "tanh",
    "tril",
    "triu",
}


_noshift = {
    "abs",
    "acos",
    "asin",
    "atan",
    "byte",
    "ceil",
    "clamp",
    "clone",
    "contiguous",
    "cos",
    "cosh",
    "cpu",
    "cuda",
    "double",
    "exp",
    "expm1",
    "float",
    "floor",
    "fmod",
    "frac",
    "half",
    "int",
    "long",
    "log",
    "pow",
    "reciprical",
    "round",
    "rsqrt",
    "short",
    "sigmoid",
    "sign",
    "sin",
    "sinh",
    "sqrt",
    "sub",
    "to",
    "tan",
    "tanh",
    "tril",
    "triu",
    "trunc",
}


def make_tuple(names):
    if isinstance(names, tuple):
        return names
    else:
        return (names,)


class NTorch(type):
    def __getattr__(cls, name):
        if name in _build:

            def call(names, *args, **kwargs):
                return cls.build(getattr(torch, name), names, *args, **kwargs)

            return call
        elif name in _noshift:

            def call(ntensor, *args, **kwargs):
                return getattr(ntensor, name)(*args, **kwargs)

            return call

    @classmethod
    def dot(cls, names, *tensors):
        args = []
        ids = {}
        seen_names = []
        for t in tensors:
            group = []
            for name in t._schema._names:
                if name not in ids:
                    ids[name] = len(ids)
                    seen_names.append(name)
                group.append(ids[name])
            args.append(t._tensor)
            args.append(group)
        names = make_tuple(names)
        keep = [n for n in seen_names if n not in names]
        args.append([ids[n] for n in keep])
        return cls.tensor(oe.contract(*args, backend="torch"), keep)

    @staticmethod
    def narrow(tensor1, start, end, **kwargs):
        key, value = next(iter(kwargs.items()))
        return tensor1._new(
            tensor1._tensor.narrow(tensor1._schema.get(key), start, end),
            updates=kwargs,
        )

    @staticmethod
    def build(init, names, *args, **kwargs):
        tensor = init(tuple(names.values()), *args, **kwargs)
        names = tuple(names.keys())
        return NamedTensor(tensor, names)

    @staticmethod
    def tensor(*args, **kwargs):
        return NamedTensor(*args, **kwargs)


class ntorch(metaclass=NTorch):
    pass