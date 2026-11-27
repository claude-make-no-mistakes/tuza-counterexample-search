# Tuza's Conjecture Counterexample Search

Tuza's conjecture asks whether the minimum number of edges meeting every triangle of a finite simple graph $G$, denoted $\tau(G)$, is at most twice the maximum number of edge-disjoint triangles, denoted $\nu(G)$. This repository combines analytic proofs for small triangle packing numbers, structural order bounds for minimal counterexamples, exhaustive small-order checks, and independently verified SAT/DRAT certificates for restricted graph classes. The full conjecture remains open. ([Conjecture and general bound](https://arxiv.org/abs/2609.13831))

## Analytic results

- **$\nu(G) \le 7$ (all orders):** Every finite simple graph with triangle packing number at most seven satisfies $\tau(G) \le 2\nu(G)$. The proof uses Kandasamy's maximum-degree-ten theorem, Puleo's local reductions, and matching theory. [Paper (PDF)](packing-seven.pdf) · [Markdown](PACKING-SEVEN.md) · [LaTeX](packing-seven.tex)
- **$\nu(G) \le 6$ and $\nu(G) \le 5$ (all orders):** Companion proofs establishing $\tau(G) \le 2\nu(G)$ for $\nu(G) \le 6$ (used in the $\nu \le 7$ proof) and a shorter self-contained argument for $\nu(G) \le 5$. [Packing-six PDF](packing-six.pdf) ([Markdown](PACKING-SIX.md), [LaTeX](packing-six.tex)) · [Packing-five PDF](packing-five.pdf) ([Markdown](PACKING-FIVE.md), [LaTeX](packing-five.tex))
- **Spanning packings and order bounds ($\nu(G) \le 9$):** Every minimal counterexample with $\nu(G) \le 9$ has a spanning maximum triangle packing whose union is connected, implying $|V(G)| \le 2\nu(G) + 1$. This restricts the first unresolved case $\nu(G) = 8$ to orders $12$–$17$ and $\nu(G) = 9$ to order at most $19$. [Paper (PDF)](spanning-packing.pdf) · [Markdown](SPANNING-PACKING.md) · [LaTeX](spanning-packing.tex) · [Exact link log](small-links.jsonl)

## Computational verification and certificates

- **Small-order exact checks:** Exhaustive verification covers all $11{,}117$ connected graphs on eight vertices (`order8.jsonl`) and all $25{,}245$ labeled connected one-vertex extensions of the $99$ nontrivial equality graphs (`equality-extensions.jsonl`). Eight-vertex graph data are from Brendan McKay's catalogue (CC BY 4.0). ([Graph catalogue](https://users.cecs.anu.edu.au/~bdm/data/graphs.html))
- **Structured search:** Explicit packing and cover witnesses certify $\tau(G) \le 2\nu(G)$ on $500$ sampled triangle-dense graphs of orders $12$–$22$ (`structured.jsonl`).
- **SAT/DRAT certificates:** Independently replayed master formulas and DRAT-trim proofs establish $\tau(G) \le 2\nu(G)$ for:
  - all $12$-vertex graphs with a universal vertex, minimum degree at least $4$, and $\nu(G) \le 6$ (`tuza-cone12-k1` through `k6`);
  - all $13$-vertex graphs with a vertex of degree $11$, minimum degree at least $4$, every edge in a triangle, and $\nu(G) \le 4$ (`tuza-near-cone13-k1` through `k4`);
  - all $13$-vertex graphs with a universal vertex, minimum degree at least $4$, and $\nu(G) \le 4$ (`tuza-cone13-k1` through `k4`).

  See [CERTIFICATE.md](CERTIFICATE.md) for the exact statements, encoding soundness proofs, scoped link reductions, packing-eight pilot runs, and full replay instructions.

## Reproduction

Tested with Python 3.10+ (including Python 3.12), NetworkX 3.3+, and `python-sat==1.9.dev25`.

```sh
python3 search.py mckay-connected8.g6
python3 extend_equality.py mckay-connected8.g6
python3 structured.py --count 100
python3 check_small_links.py
```

For certificate replay and DRAT-trim verification, see [CERTIFICATE.md#replay](CERTIFICATE.md#replay).
