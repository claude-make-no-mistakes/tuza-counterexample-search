"""Find a matching and a small cover of the remaining link edges."""

from functools import lru_cache
from itertools import combinations

import networkx as nx


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


@lru_cache(maxsize=8192)
def matching_and_cover(adjacency):
    """Return a matching M and vertex set Q covering the link minus M."""
    order = len(adjacency)
    vertices = (1 << order) - 1

    @lru_cache(maxsize=None)
    def maximum_matching(available):
        if not available:
            return ()
        u = (available & -available).bit_length() - 1
        remainder = available ^ (1 << u)
        best = maximum_matching(remainder)
        for v in bits(adjacency[u] & remainder):
            trial = ((u, v), *maximum_matching(remainder ^ (1 << v)))
            if len(trial) > len(best):
                best = trial
                if 2 * len(best) == available.bit_count() or 2 * len(best) + 1 == available.bit_count():
                    break
        return best

    # Every edge avoiding Q must itself belong to M, so these edges are forced.
    matching_bound = len(maximum_matching(vertices))
    for size in range(matching_bound + 1):
        for cover in combinations(range(order), size):
            outside = vertices ^ sum(1 << v for v in cover)
            forced = []
            for u in bits(outside):
                neighbors = adjacency[u] & outside
                if neighbors.bit_count() >= 2:
                    break
                if neighbors:
                    v = neighbors.bit_length() - 1
                    if u < v:
                        forced.append((u, v))
            else:
                free = vertices ^ sum(1 << v for edge in forced for v in edge)
                matching = (*forced, *maximum_matching(free))
                if matching and len(matching) >= size:
                    return matching, cover
    return None


def reducible_link(graph):
    """Return the first reduction supported on one component of a link."""
    # Small links are cheaper and often have shorter reductions.
    for apex, _ in sorted(graph.degree(), key=lambda item: (item[1], item[0])):
        link = graph.subgraph(graph[apex])
        for component in sorted(nx.connected_components(link), key=lambda c: (len(c), min(c))):
            vertices = sorted(component)
            positions = {vertex: i for i, vertex in enumerate(vertices)}
            adjacency = tuple(sum(1 << positions[v] for v in link[u] if v in positions) for u in vertices)
            result = matching_and_cover(adjacency)
            if result is not None:
                matching, cover = result
                return {"apex": apex, "scope": vertices,
                        "matching": [(vertices[u], vertices[v]) for u, v in matching],
                        "cover": [vertices[v] for v in cover]}
    return None


def forbid_link_reduction(domain, witness):
    apex = witness["apex"]
    matching = {tuple(sorted(edge)) for edge in witness["matching"]}
    cover = set(witness["cover"])
    scope = set(witness["scope"])
    clause = []
    for triangle, literal in domain.triangles.items():
        if apex not in triangle:
            continue
        opposite = tuple(v for v in triangle if v != apex)
        if opposite in matching:
            clause.append(-literal)
        elif not scope.isdisjoint(opposite) and cover.isdisjoint(opposite):
            clause.append(literal)
    return clause
