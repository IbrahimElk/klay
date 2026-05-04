# noinspection PyUnresolvedReferences
from .klay_ext import (
        Circuit,
        NodePtr,
        check_sdnnf,
        check_decomposability,
        check_smooth,
        SDNNFResult,
        SDNNFViolation,
)
NodePtr.__module__ = "klay"

from collections.abc import Sequence
import tempfile
import os
from pathlib import Path


def to_torch_module(self: Circuit,
                    semiring: str = "log",
                    probabilistic: bool = False,
                    eps: float = 0,
                    collapse: bool = False,
                    merge: bool = False
):
    """
    Convert the circuit into a PyTorch module.

    :param semiring:
        The semiring in which the circuit should be evaluated. Supported options are :code:`"log"`, :code:`"real"`, :code:`"mpe"`, or :code:`"godel"`.
    :param probabilistic:
        If enabled, construct a probabilistic circuit instead of an arithmetic circuit.
        This means the inputs to a sum node are multiplied by a probability, and
        we can interpret sum nodes as latent Categorical variables.
    :param eps:
        Epsilon used by log semiring for numerical stability.
    :param collapse:
        If True, remove identity (single-child pass-through) layers introduced
        by klay's strict alternation. Reduces sequential depth without changing
        results.
    :param merge:
        If True, merge consecutive same-type layers into one. Duplicates shared
        sub-computations but minimizes sequential kernel launches, best for GPU.
        Implies collapse=True.
    """
    from .torch.circuit_modules import ProbabilisticCircuitModule
    from .torch.circuit_modules import CircuitModule
    from .optimize import optimize_indices
    ixs_in, ixs_out = self._get_indices()

    layer_types = None
    if collapse or merge:
        ixs_in, ixs_out, layer_types = optimize_indices(
            list(ixs_in), list(ixs_out), collapse=collapse, merge=merge
        )

    if probabilistic:
        return ProbabilisticCircuitModule(ixs_in, ixs_out,
                                          semiring=semiring,
                                          eps=eps,
                                          layer_types=layer_types)
    return CircuitModule(ixs_in, ixs_out,
                         semiring=semiring,
                         eps=eps,
                         layer_types=layer_types)

def to_jax_function(self: Circuit,
                    semiring: str = "log",
                    collapse: bool = False,
                    merge: bool = False
):
    """
    Convert the circuit into a Jax function.

    :param semiring:
        The semiring in which the circuit should be evaluated. Supported options are :code:`"log"`, :code:`"real"`, :code:`"mpe"`, or :code:`"godel"`.
    """
    from .jax import create_knowledge_layer
    from .optimize import optimize_indices
    ixs_in, ixs_out = self._get_indices()
    layer_types = None
    if collapse or merge:
        ixs_in, ixs_out, layer_types = optimize_indices(
                list(ixs_in), list(ixs_out), collapse=collapse, merge=merge)

    return create_knowledge_layer(ixs_in, ixs_out,
                                  semiring=semiring,
                                  layer_types=layer_types)



def add_sdd(self: Circuit, sdd: "SddNode", true_lits: Sequence[int] = (), false_lits: Sequence[int] = ()) -> NodePtr:
    """
    Add an SDD to the Circuit.

    :param sdd:
        PySDD `SDDNode`_ to be added.
    :param true_lits:
        List of literals that are always true and should get propagated away.
    :param false_lits:
        List of literals that are always false and should get propagated away.

    .. _SDDNode: https://pysdd.readthedocs.io/en/latest/classes/SddNode.html
    """
    # Use delete=False for Windows compatibility - the file must be closed
    # before other processes can access it on Windows
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = tmp.name

    try:
        sdd.save(bytes(Path(tmp_path)))
        return self.add_sdd_from_file(tmp_path, true_lits, false_lits)
    finally:
        os.unlink(tmp_path)


Circuit.to_torch_module = to_torch_module
Circuit.to_jax_function = to_jax_function
Circuit.add_sdd = add_sdd
