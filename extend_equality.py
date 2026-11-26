"""Search all connected one-vertex extensions of Tuza equality graphs in a corpus."""

import argparse
from collections import Counter
import json
from pathlib import Path

import networkx as nx

from search import set_bits, triangle_numbers, validate


def scan(corpus):
    seen = set()
    tallies = Counter()
    parents = 0
    for graph in nx.read_graph6(corpus):
        packing, cover = triangle_numbers(graph)
        if not packing or cover != 2 * packing:
            continue
        parents += 1
        added = len(graph)
        graph.add_node(added)
        for neighborhood in range(1, 1 << added):
            edges = [(u, added) for u in set_bits(neighborhood)]
            graph.add_edges_from(edges)
            graph6 = nx.to_graph6_bytes(graph, header=False).decode("ascii").strip()
            if graph6 not in seen:
                seen.add(graph6)
                packing, cover = triangle_numbers(graph)
                tallies[2 * packing - cover] += 1
                if cover > 2 * packing:
                    return {"graph6": graph6, "packing": packing, "cover": cover}
            graph.remove_edges_from(edges)
    return {"equality_parents": parents, "labeled_extensions": len(seen),
            "counts_by_slack": dict(sorted(tallies.items())), "witness": None}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("corpus", type=Path)
    args = parser.parse_args()
    validate()
    print(json.dumps(scan(args.corpus)))
