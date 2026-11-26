"""Independently check the reasons behind every Tuza synthesis refinement."""

import argparse
from functools import cache
import json
from pathlib import Path

import networkx as nx
from pysat.formula import CNF
from pysat.solvers import Cadical195, Glucose4

from synthesis import Domain
from structured import triangle_incidence


def partition_into_triangles(order, edges):
    graph = nx.Graph()
    graph.add_nodes_from(range(order))
    graph.add_edges_from(edges)
    actual, triangles, incident = triangle_incidence(graph)
    masks = [sum(1 << i for i in triangle) for triangle in triangles]

    @cache
    def partition(remaining):
        if not remaining:
            return True
        pivot = (remaining & -remaining).bit_length() - 1
        return any(partition(remaining ^ masks[j]) for j in incident[pivot]
                   if remaining & masks[j] == masks[j])

    return partition((1 << len(actual)) - 1)


def recover_cover(domain, clause):
    disjoint = {vs for vs, lit in domain.triangles.items() if lit in clause}
    allowed = set(domain.edges) - {e for vs in disjoint for e in domain.triples[vs]}
    required = set(domain.triangles) - disjoint
    choices = {vs: sorted(allowed.intersection(domain.triples[vs])) for vs in required}
    covered_by = {e: {vs for vs in required if e in domain.triples[vs]} for e in allowed}

    def find(remaining, budget):
        if not remaining:
            return set()
        if not budget:
            return None
        victim = min(remaining, key=lambda vs: len(choices[vs]))
        for edge in choices[victim]:
            tail = find(remaining - covered_by[edge], budget - 1)
            if tail is not None:
                return {edge} | tail
        return None

    return find(required, 2 * domain.k)


def check_refinements(domain, path, append=True):
    inverse = {lit: edge for edge, lit in domain.edges.items()}
    edge_lits = set(inverse)
    triangle_lits = set(domain.triangles.values())
    counts = {"packing": 0, "cover": 0}
    with path.open(encoding="ascii") as log:
        for line in log:
            event = json.loads(line)
            reason, clause = event["reason"], event["clause"]
            assert len(clause) == len(set(clause))
            if reason == "packing":
                assert len(clause) == 3 * (domain.k + 1) and {-x for x in clause} <= edge_lits
                assert partition_into_triangles(domain.order, [inverse[-x] for x in clause]), event
            elif reason == "cover":
                assert set(clause) <= triangle_lits
                witness = recover_cover(domain, set(clause))
                assert witness is not None and domain.cover_rejection(witness) == clause, event
            else:
                raise ValueError(f"Unknown refinement: {reason}")
            counts[reason] += 1
            if append:
                domain.cnf.append(clause)
    return counts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--order", type=int, required=True)
    parser.add_argument("--packing", type=int, required=True)
    parser.add_argument("--min-degree", type=int, required=True)
    parser.add_argument("--missing-one", action="store_true")
    parser.add_argument("--prefix", type=Path, required=True)
    parser.add_argument("--drat", action="store_true")
    args = parser.parse_args()
    domain = Domain(args.order, args.packing, args.min_degree, args.missing_one)
    counts = check_refinements(domain, args.prefix.with_suffix('.refinements.jsonl'))
    recorded = CNF(from_file=str(args.prefix.with_suffix('.cnf')))
    assert domain.cnf.clauses == recorded.clauses
    with Cadical195(bootstrap_with=recorded.clauses) as checker:
        assert not checker.solve()
    if args.drat:
        with Glucose4(bootstrap_with=recorded.clauses, with_proof=True) as producer:
            assert not producer.solve()
            proof = producer.get_proof()
        args.prefix.with_suffix('.drat').write_text('\n'.join(proof) + '\n', encoding='ascii')
    print(json.dumps({"refinements_checked": counts, "cadical_master_unsat": True, "drat_exported": args.drat}))
