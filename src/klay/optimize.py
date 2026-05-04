"""Index-level optimizations for klay circuits."""

import numpy as np


def get_layer_types(n_layers):
    return [i % 2 == 0 for i in range(n_layers)]


def is_identity_layer(csr):
    """Check whether every node in a layer has exactly one child."""
    csr = np.asarray(csr)
    if len(csr) < 2:
        return False
    return np.all(np.diff(csr) == 1)


def collapse_identity_layers(ixs_in, ixs_out, layer_types):
    """Remove layers where every node is a single-child pass-through."""
    ixs_in = [np.asarray(a, dtype=np.int64) for a in ixs_in]
    ixs_out = [np.asarray(a, dtype=np.int64) for a in ixs_out]
    layer_types = list(layer_types)

    i = 0
    while i < len(ixs_in):
        if is_identity_layer(ixs_out[i]):
            mapping = ixs_in[i]

            if i + 1 < len(ixs_in):
                ixs_in[i + 1] = mapping[ixs_in[i + 1]]

            ixs_in.pop(i)
            ixs_out.pop(i)
            layer_types.pop(i)
        else:
            i += 1

    return ixs_in, ixs_out, layer_types


def merge_same_type_layers(ixs_in, ixs_out, layer_types):
    """Merge consecutive layers that have the same type (both sum or both product)."""
    ixs_in = [np.asarray(a, dtype=np.int64) for a in ixs_in]
    ixs_out = [np.asarray(a, dtype=np.int64) for a in ixs_out]
    layer_types = list(layer_types)

    i = 0
    while i + 1 < len(ixs_in):
        if layer_types[i] == layer_types[i + 1]:
            csr_i = ixs_out[i]
            in_i = ixs_in[i]
            csr_next = ixs_out[i + 1]
            in_next = ixs_in[i + 1]

            n_nodes = len(csr_next) - 1
            new_in_parts = []
            new_csr = np.empty(n_nodes + 1, dtype=np.int64)
            new_csr[0] = 0

            running = 0
            for j in range(n_nodes):
                children = in_next[csr_next[j]:csr_next[j + 1]]
                for c in children:
                    grandchildren = in_i[csr_i[c]:csr_i[c + 1]]
                    new_in_parts.append(grandchildren)
                    running += len(grandchildren)
                new_csr[j + 1] = running

            ixs_in[i] = np.concatenate(new_in_parts) if new_in_parts else np.array([], dtype=np.int64)
            ixs_out[i] = new_csr

            ixs_in.pop(i + 1)
            ixs_out.pop(i + 1)
            layer_types.pop(i + 1)
        else:
            i += 1

    return ixs_in, ixs_out, layer_types


def optimize_indices(ixs_in, ixs_out, collapse=True, merge=False):
    """Apply index-level optimizations."""
    n = len(ixs_in)
    layer_types = get_layer_types(n)

    if merge:
        collapse = True

    if collapse:
        ixs_in, ixs_out, layer_types = collapse_identity_layers(ixs_in, ixs_out, layer_types)

    if merge:
        ixs_in, ixs_out, layer_types = merge_same_type_layers(ixs_in, ixs_out, layer_types)

    return ixs_in, ixs_out, layer_types
