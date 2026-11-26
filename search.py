"""Exact triangle packing and edge transversal search on graph6 inputs."""

import argparse
from functools import cache
from itertools import combinations
import json
from pathlib import Path

import networkx as nx


def set_bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def triangle_numbers(graph):
    edges = {edge: i for i, edge in enumerate(sorted(tuple(sorted(e)) for e in graph.edges()))}
    triangles = []
    edge_covers = [0] * len(edges)
    for u, v in edges:
        for w in graph[u].keys() & graph[v].keys():
            if w <= v:
                continue
            triple = (edges[u, v], edges[u, w], edges[v, w])
            for e in triple:
                edge_covers[e] |= 1 << len(triangles)
            triangles.append(triple)
    conflicts = [edge_covers[i] | edge_covers[j] | edge_covers[k] for i, j, k in triangles]

    def components(remaining):
        while remaining:
            component = 0
            frontier = remaining & -remaining
            while frontier:
                bit = frontier & -frontier
                component |= bit
                frontier = ((frontier ^ bit) | conflicts[bit.bit_length() - 1]) & remaining & ~component
            yield component
            remaining ^= component

    @cache
    def packing(remaining):
        if not remaining:
            return 0
        components_now = list(components(remaining))
        if len(components_now) > 1:
            return sum(packing(c) for c in components_now)
        # A packing either uses no triangle on this edge, or uses exactly one.
        pivot = max((cover & remaining for cover in edge_covers), key=int.bit_count)
        if pivot == remaining:
            return 1
        return max(packing(remaining & ~pivot),
                   max(1 + packing(remaining & ~conflicts[i]) for i in set_bits(pivot)))

    @cache
    def cover(remaining):
        if not remaining:
            return 0
        components_now = list(components(remaining))
        if len(components_now) > 1:
            return sum(cover(c) for c in components_now)
        choices = [edge_covers[e] & remaining for e in range(len(edges))]
        if remaining in choices:
            return 1
        # Covering any one triangle requires at least one of its three edges.
        pivot = max(set_bits(remaining),
                    key=lambda i: sum(choices[e].bit_count() for e in triangles[i]))
        options = sorted({choices[e] for e in triangles[pivot]}, key=int.bit_count, reverse=True)
        maximal_options = [option for i, option in enumerate(options)
                           if all(option & other != option for other in options[:i])]
        return 1 + min(cover(remaining & ~option) for option in maximal_options)

    remaining = (1 << len(triangles)) - 1
    result = packing(remaining), cover(remaining)
    packing.cache_clear()
    cover.cache_clear()
    return result


def brute_numbers(graph):
    """Independent exhaustive baseline via edge masks."""
    edges = tuple(tuple(sorted(edge)) for edge in sorted(graph.edges()))
    triangles = tuple(frozenset(combinations(vs, 2)) for vs in combinations(sorted(graph), 3)
                      if all(graph.has_edge(*edge) for edge in combinations(vs, 2)))
    packing = 0
    for size in range(1, min(len(edges) // 3, len(triangles)) + 1):
        if any(len(frozenset.union(*tri)) == 3 * size for tri in combinations(triangles, size)):
            packing = size
    for size in range(len(edges) + 1):
        if any(all(set(candidate) & tri for tri in triangles) for candidate in combinations(edges, size)):
            return packing, size
    raise AssertionError("Selecting all edges always hits every triangle")


def validate():
    # The four triangles of K4 intersect pairwise in edges, and two opposite edges cover them.
    assert triangle_numbers(nx.complete_graph(4)) == (1, 2)
    for graph in nx.graph_atlas_g():
        if len(graph) <= 5:
            assert triangle_numbers(graph) == brute_numbers(graph)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("corpus", nargs="?", type=Path)
    args = parser.parse_args()
    validate()
    corpus = nx.graph_atlas_g() if args.corpus is None else nx.read_graph6(args.corpus)
    counts = {}
    equality = {}
    for graph in corpus:
        n = len(graph)
        counts[n] = counts.get(n, 0) + 1
        packing, cover = triangle_numbers(graph)
        if cover > 2 * packing:
            print(json.dumps({"graph6": nx.to_graph6_bytes(graph, header=False).decode().strip(),
                              "packing": packing, "cover": cover}), flush=True)
            return
        if cover == 2 * packing and packing:
            equality[n] = equality.get(n, 0) + 1
    print(json.dumps({"checked_by_order": counts, "nontrivial_equality_by_order": equality, "witness": None}))


if __name__ == "__main__":
    main()
