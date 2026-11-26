"""Check the remaining eight- and nine-edge links of minimum degree two."""

from itertools import combinations
import json


def reduction(edge_masks, covers_by_size):
    for size, covers in enumerate(covers_by_size, 1):
        for matching in combinations(edge_masks, size):
            used = 0
            for edge in matching:
                used |= edge
            if used.bit_count() != 2 * size:
                continue
            remaining = set(edge_masks) - set(matching)
            for cover in covers:
                if all(edge & cover for edge in remaining):
                    return matching, cover
    return None


def check(order, size):
    edges = tuple(combinations(range(order), 2))
    covers = [tuple(sum(1 << v for v in cover) for cover in combinations(range(order), size))
              for size in range(1, order // 2 + 1)]
    total = checked = 0
    for graph in combinations(edges, size):
        total += 1
        degrees = [0] * order
        for u, v in graph:
            degrees[u] += 1
            degrees[v] += 1
        if min(degrees) < 2:
            continue
        masks = tuple((1 << u) | (1 << v) for u, v in graph)
        witness = reduction(masks, covers)
        if witness is None:
            raise AssertionError(f"No matching and cover for {graph}")
        matching, cover = witness
        assert sum(matching).bit_count() == 2 * len(matching)
        assert cover.bit_count() <= len(matching)
        assert all(edge in matching or edge & cover for edge in masks)
        checked += 1
    return {"order": order, "edges": size, "labeled_graphs": total, "minimum_degree_two": checked,
            "reductions_verified": checked}


if __name__ == "__main__":
    for order, size in ((7, 8), (7, 9), (8, 9)):
        print(json.dumps(check(order, size)), flush=True)
