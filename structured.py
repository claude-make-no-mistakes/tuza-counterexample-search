"""Search triangle-rich clique arrangements using checkable packing and cover witnesses."""

import argparse
from collections import Counter
from itertools import combinations
import json
from math import ceil
from pathlib import Path
from random import Random

import networkx as nx
from pysat.card import CardEnc, EncType
from pysat.formula import CNF
from pysat.solvers import Glucose4

from search import triangle_numbers


def triangle_incidence(graph):
    edges = sorted(tuple(sorted(edge)) for edge in graph.edges())
    edge_id = {edge: i for i, edge in enumerate(edges)}
    triangles = []
    incident = [[] for _ in edges]
    for u, v in edges:
        for w in sorted(graph[u].keys() & graph[v].keys()):
            if w > v:
                tri = tuple(edge_id[edge] for edge in ((u, v), (u, w), (v, w)))
                for e in tri:
                    incident[e].append(len(triangles))
                triangles.append(tri)
    return edges, triangles, incident


def greedy_witnesses(edges, triangles, incident, rng):
    packing = []
    order = list(range(len(triangles)))
    scores = [sum(len(incident[e]) for e in tri) for tri in triangles]
    for attempt in range(64):
        rng.shuffle(order)
        if attempt % 2 == 0:
            order.sort(key=scores.__getitem__)
        subset = []
        occupied = set()
        for i in order:
            if occupied.isdisjoint(triangles[i]):
                subset.append(i)
                occupied.update(triangles[i])
        if len(subset) > len(packing):
            packing = subset

    cover = list(range(len(edges)))
    order = list(cover)
    for _ in range(12):
        rng.shuffle(order)
        active = set(range(len(triangles)))
        tentative = []
        while active:
            edge = max(order, key=lambda i: sum(t in active for t in incident[i]))
            tentative.append(edge)
            active.difference_update(incident[edge])
        if len(tentative) < len(cover):
            cover = tentative
    return packing, cover


def packing_cnf(incident, triangles, target):
    cnf = CNF()
    for on_edge in incident:
        cnf.extend([-a - 1, -b - 1] for a, b in combinations(on_edge, 2))
    cnf.extend(CardEnc.atleast(lits=list(range(1, len(triangles) + 1)), bound=target,
                              encoding=EncType.seqcounter).clauses)
    return cnf


def cover_cnf(edges, triangles, target):
    cnf = CNF(from_clauses=[[e + 1 for e in tri] for tri in triangles])
    cnf.extend(CardEnc.atmost(lits=list(range(1, len(edges) + 1)), bound=target,
                             encoding=EncType.seqcounter).clauses)
    return cnf


def model(cnf, count):
    with Glucose4(bootstrap_with=cnf.clauses) as solver:
        if solver.solve():
            return [v - 1 for v in solver.get_model() if 0 < v <= count]
    return None


def check_packing(packing, triangles):
    occupied = [e for i in packing for e in triangles[i]]
    assert len(occupied) == len(set(occupied)) == 3 * len(packing)


def check_cover(cover, triangles):
    covered = set(cover)
    assert all(not covered.isdisjoint(tri) for tri in triangles)


def decide(graph, rng):
    edges, triangles, incident = triangle_incidence(graph)
    pack, cover = greedy_witnesses(edges, triangles, incident, rng)
    check_packing(pack, triangles)
    check_cover(cover, triangles)
    if len(cover) <= 2 * len(pack):
        return "greedy-certificates", pack, cover, None

    hi = min(len(triangles), len(edges) // 3, ceil(len(cover) / 2))
    while len(pack) < hi:
        target = (len(pack) + hi + 1) // 2
        attempt = model(packing_cnf(incident, triangles, target), len(triangles))
        if attempt is None:
            hi = target - 1
        else:
            check_packing(attempt, triangles)
            assert len(attempt) >= target
            pack = attempt
    if len(cover) <= 2 * len(pack):
        return "sat-packing-certificate", pack, cover, None

    attempt = model(cover_cnf(edges, triangles, 2 * len(pack)), len(edges))
    if attempt is not None:
        check_cover(attempt, triangles)
        assert len(attempt) <= 2 * len(pack)
        return "sat-cover-certificate", pack, attempt, None

    assert len(pack) < len(triangles)
    return "candidate-awaiting-proof-check", pack, cover, (
        packing_cnf(incident, triangles, len(pack) + 1), cover_cnf(edges, triangles, 2 * len(pack)))


def export_proofs(formulas, prefix):
    for role, formula in zip(("packing", "cover"), formulas, strict=True):
        output = prefix.parent / f"{prefix.name}-{role}"
        with Glucose4(bootstrap_with=formula.clauses, with_proof=True) as solver:
            assert not solver.solve(), f"Proof-producing solve disagrees for {role}"
            formula.to_file(str(output.with_suffix(".cnf")))
            output.with_suffix(".drat").write_text("\n".join(solver.get_proof()) + "\n", encoding="ascii")


def candidates(seed, inputs_per_order):
    rng = Random(seed)
    for n in (12, 13, 15, 18, 22):
        seen = set()
        for _ in range(inputs_per_order * 500):
            graph = nx.Graph()
            graph.add_nodes_from(range(n))
            per_vertex = [0] * n
            desired = rng.randrange(n, 2 * n + 1)
            for _ in range(desired):
                weights = [1 / (1 + amount) for amount in per_vertex]
                group = set()
                size = rng.choice((4, 5, 5, 6))
                while len(group) < size:
                    group.add(rng.choices(range(n), weights=weights, k=1)[0])
                graph.add_edges_from(combinations(sorted(group), 2))
                for u in group:
                    per_vertex[u] += 1
            # Decrease the density around the target range while retaining heavily shared triangle edges.
            probability = rng.uniform(0.24, 0.6)
            graph.remove_edges_from(edge for edge in list(graph.edges()) if rng.random() < probability)
            if not nx.is_connected(graph) or max(d for _, d in graph.degree()) <= 10:
                continue
            _, _, incident = triangle_incidence(graph)
            if max(map(len, incident), default=0) < 5:
                continue
            token = nx.to_graph6_bytes(graph, header=False).decode().strip()
            if token not in seen:
                seen.add(token)
                yield token, graph
                if len(seen) == inputs_per_order:
                    break
        if len(seen) != inputs_per_order:
            raise RuntimeError(f"Generated {len(seen)} of {inputs_per_order} requested inputs at order {n}")


def validate():
    rng = Random(871)
    for graph in nx.graph_atlas_g():
        if len(graph) > 5:
            break
        outcome, pack, cover, formulas = decide(graph, rng)
        expected_pack, expected_cover = triangle_numbers(graph)
        assert formulas is None and len(cover) <= 2 * len(pack)
        assert len(pack) <= expected_pack and len(cover) >= expected_cover
    graph = nx.complete_graph(4)
    edges, triangles, incident = triangle_incidence(graph)
    assert model(packing_cnf(incident, triangles, 1), len(triangles)) is not None
    assert model(packing_cnf(incident, triangles, 2), len(triangles)) is None
    assert model(cover_cnf(edges, triangles, 1), len(edges)) is None
    assert model(cover_cnf(edges, triangles, 2), len(edges)) is not None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=70, help="Inputs per graph order")
    parser.add_argument("--seed", type=int, default=20261126)
    parser.add_argument("--proof-prefix", type=Path, default=Path("tuza-candidate"))
    args = parser.parse_args()
    if args.count < 1:
        parser.error("Count must be positive")
    validate()
    rng = Random(args.seed + 1)
    totals = Counter()
    for token, graph in candidates(args.seed, args.count):
        status, packing, cover, formulas = decide(graph, rng)
        totals[status] += 1
        record = {"graph6": token, "order": len(graph), "packing_size": len(packing),
                  "cover_size": len(cover), "status": status}
        if formulas is not None:
            export_proofs(formulas, args.proof_prefix)
            record["proof_prefix"] = str(args.proof_prefix)
            print(json.dumps(record), flush=True)
            break
        print(json.dumps(record), flush=True)
    print(json.dumps({"seed": args.seed, "outcomes": dict(totals)}), flush=True)
