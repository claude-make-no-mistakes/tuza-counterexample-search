"""Search for a Tuza counterexample by adding valid packing and cover constraints."""

import argparse
from collections import Counter
from itertools import combinations
import json
from math import comb
from pathlib import Path
from random import Random

import networkx as nx
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Glucose4

from link_reduction import forbid_link_reduction, reducible_link
from structured import check_cover, check_packing, cover_cnf, export_proofs, model, packing_cnf, triangle_incidence


def require_at_least(cnf, variables, bound, pool):
    if bound > len(variables):
        cnf.append([])
    elif bound > 0:
        cnf.extend(CardEnc.atleast(variables, bound, vpool=pool, encoding=EncType.seqcounter).clauses)


def lex_order(cnf, left, right, pool):
    """Require left >= right in lexicographic order, with 1 larger than 0."""
    prefix = pool.id()
    cnf.append([prefix])
    for a, b in zip(left, right, strict=True):
        cnf.append([-prefix, a, -b])
        following = pool.id()
        cnf.append([-prefix, -a, -b, following])
        cnf.append([-prefix, a, b, following])
        prefix = following


def cone_edge_lower_bound(order, k):
    """Use each uniform size of the side that contains the universal vertex."""
    leaves = order - 1
    pairs = comb(leaves, 2)
    allowed = []
    for inside in range(leaves + 1):
        same_side = comb(inside, 2) + comb(leaves - inside, 2)
        # The average number of edges within the two parts is inside + same_side*m/pairs.
        demanded = (2 * k + 1 - inside) * pairs
        if demanded > 0:
            allowed.append(pairs + 1 if not same_side else (demanded + same_side - 1) // same_side)
    return max(allowed, default=0)


class Domain:
    def __init__(self, order, k, min_degree, missing_one=False, reduced=False):
        self.order = order
        self.k = k
        self.reduced = reduced
        pool = IDPool()
        self.edges = {edge: pool.id(edge) for edge in combinations(range(order), 2)}
        self.triangles = {vs: pool.id(vs) for vs in combinations(range(order), 3)}
        self.triples = {vs: tuple(combinations(vs, 2)) for vs in self.triangles}
        self.edge_triples = {edge: [] for edge in self.edges}
        cnf = CNF()
        for vs, t in self.triangles.items():
            variables = [self.edges[edge] for edge in self.triples[vs]]
            cnf.append([t, *(-e for e in variables)])
            cnf.extend([-t, e] for e in variables)
            for edge in self.triples[vs]:
                self.edge_triples[edge].append(t)

        for (u, v), e in self.edges.items():
            if u == 0:
                cnf.append([-e if missing_one and v == order - 1 else e])
            cnf.append([-e, *self.edge_triples[u, v]])
            if reduced:
                triangles = self.edge_triples[u, v]
                cnf.extend([-e, *triangles[:i], *triangles[i+1:]] for i in range(len(triangles)))
        for vertex in range(1, order):
            require_at_least(cnf, [e for edge, e in self.edges.items() if vertex in edge], min_degree, pool)
        leaf_edges = [e for (u, _), e in self.edges.items() if u != 0]
        require_at_least(cnf, leaf_edges, cone_edge_lower_bound(order, k), pool)

        # A lexicographically maximal labeling fixing vertex 0 has these row comparisons.
        end = order - int(missing_one)
        for a, b in zip(range(1, end - 1), range(2, end), strict=True):
            others = [v for v in range(1, order) if v != a and v != b]
            left = [self.edges[tuple(sorted((a, v)))] for v in others]
            right = [self.edges[tuple(sorted((b, v)))] for v in others]
            lex_order(cnf, left, right, pool)

        rng = Random(587)
        for _ in range(18):
            inside = set(rng.sample(range(1, order), (order - 1) // 2)) | {0}
            inside_edges = [e for (u, v), e in self.edges.items() if (u in inside) == (v in inside)]
            require_at_least(cnf, inside_edges, 2 * k + 1, pool)
        self.cnf = cnf

    def graph(self, assignment):
        positive = {v for v in assignment if v > 0}
        graph = nx.Graph()
        graph.add_nodes_from(range(self.order))
        graph.add_edges_from(edge for edge, lit in self.edges.items() if lit in positive)
        return graph

    def packing_rejection(self, packing_edges):
        assert len(packing_edges) == 3 * (self.k + 1) and len(set(packing_edges)) == len(packing_edges)
        return sorted(-self.edges[e] for e in packing_edges)

    def cover_rejection(self, covered):
        assert len(covered) <= 2 * self.k
        return [t for vs, t in self.triangles.items() if covered.isdisjoint(self.triples[vs])]


def greedy_pack(triangles, incident, target):
    used = set()
    found = []
    scores = [sum(len(incident[e]) for e in tri) for tri in triangles]
    for i in sorted(range(len(triangles)), key=scores.__getitem__):
        if used.isdisjoint(triangles[i]):
            used.update(triangles[i])
            found.append(i)
            if len(found) >= target:
                return found
    return None


def refine(domain, graph):
    k = domain.k
    edges, triangles, incident = triangle_incidence(graph)
    if len(triangles) >= k + 1:
        pack = greedy_pack(triangles, incident, k + 1)
        if pack is None:
            pack = model(packing_cnf(incident, triangles, k + 1), len(triangles))
        if pack is not None:
            pack = pack[:k + 1]
            check_packing(pack, triangles)
            forbidden = [edges[e] for i in pack for e in triangles[i]]
            return "packing", domain.packing_rejection(forbidden)

    cover = model(cover_cnf(edges, triangles, 2 * k), len(edges))
    if cover is not None:
        check_cover(cover, triangles)
        return "cover", domain.cover_rejection({edges[i] for i in cover})
    if len(triangles) < k + 1:
        raise RuntimeError("The cover model rejected a graph with too few triangles")
    return "candidate", (packing_cnf(incident, triangles, k + 1), cover_cnf(edges, triangles, 2 * k))


def scan(domain, limit, output, export=None, earlier=()):
    counts = Counter()
    kinds = set()
    initial = len(domain.cnf.clauses)
    for event in earlier:
        clause = event["clause"]
        domain.cnf.append(clause)
        kinds.add(tuple(clause))
        counts[event["reason"]] += 1
    with Glucose4(bootstrap_with=domain.cnf.clauses) as solver:
        for trial in range(1, limit + 1):
            if not solver.solve():
                if export is not None:
                    domain.cnf.to_file(str(export.with_suffix('.cnf')))
                return {"status": "master-unsat", "initial_clauses": initial, "rejections": dict(counts)}
            graph = domain.graph(solver.get_model())
            witness = reducible_link(graph) if domain.reduced else None
            if witness is None:
                rejection, clause = refine(domain, graph)
            else:
                rejection, clause = "link", forbid_link_reduction(domain, witness)
            if rejection == "candidate":
                if export is not None:
                    export_proofs(clause, export)
                return {"status": "candidate-awaiting-proof-check", "bound": domain.k,
                        "graph6": nx.to_graph6_bytes(graph, header=False).decode().strip(), "rejections": dict(counts)}
            key = tuple(clause)
            assert key not in kinds, "A duplicate refinement failed to exclude its own witness"
            kinds.add(key)
            domain.cnf.append(clause)
            solver.add_clause(clause)
            counts[rejection] += 1
            if output is not None:
                event = {"reason": rejection, "clause": clause}
                if witness is not None:
                    event["witness"] = witness
                output.write(json.dumps(event) + "\n")
            if trial % 2500 == 0 and export is not None:
                print(json.dumps({"trials": sum(counts.values()), "rejections": dict(counts)}), flush=True)
    return {"status": "trial-limit", "initial_clauses": initial, "rejections": dict(counts)}


def validate():
    # At order four the cone K4 is tight with nu=1 and tau=2. At order five K5 is tight at 2 and 4.
    assert scan(Domain(4, 1, 0), 100, None)["status"] == "master-unsat"
    assert scan(Domain(5, 2, 0), 100, None)["status"] == "master-unsat"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--order", type=int, required=True)
    parser.add_argument("--packing", type=int, required=True)
    parser.add_argument("--min-degree", type=int, default=4)
    parser.add_argument("--missing-one", action="store_true", help="Use an anchor adjacent to all but one vertex")
    parser.add_argument("--reduced", action="store_true", help="Search only for an edge-minimal counterexample")
    parser.add_argument("--limit", type=int, default=50000)
    parser.add_argument("--export", type=Path, required=True)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if not 4 <= args.order <= 20 or not 1 <= args.packing or not 0 <= args.min_degree < args.order or args.limit < 1:
        parser.error("Invalid graph order, packing bound, degree, or trial limit")
    validate()
    domain = Domain(args.order, args.packing, args.min_degree, args.missing_one, args.reduced)
    log = args.export.with_suffix('.refinements.jsonl')
    earlier = ()
    if args.resume:
        from replay_synthesis import check_refinements

        check_refinements(domain, log, append=False)
        earlier = [json.loads(line) for line in log.read_text(encoding='ascii').splitlines()]
    with log.open('a' if args.resume else 'w', encoding='ascii') as output:
        result = scan(domain, args.limit, output, args.export, earlier)
    print(json.dumps({"order": args.order, "packing_bound": args.packing,
                      "min_degree": args.min_degree, "anchor_degree": args.order - 1 - args.missing_one,
                      "reduced": args.reduced, **result}), flush=True)
