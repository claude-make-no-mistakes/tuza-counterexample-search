# Tuza's conjecture counterexample search

Tuza's conjecture asks whether the minimum number of edges meeting every triangle is at most twice the maximum number of edge-disjoint triangles. We searched structured graphs and used independently checked SAT certificates for restricted cases. The full conjecture remains open. [Conjecture and general bound](https://arxiv.org/abs/2609.13831)

- Exact checks cover 11,117 connected graphs on eight vertices and 25,245 labeled one-vertex extensions of equality cases. [Graph catalogue](https://users.cecs.anu.edu.au/~bdm/data/graphs.html)
- Explicit packings and covers certify the bound on 500 sampled graphs of orders 12–22 with high triangle overlap.
- Independent certificate checks establish the conjecture on 12-vertex graphs with a universal vertex, minimum degree at least four, and packing number at most five. [Statement and certificate replay](CERTIFICATE.md)
- The 13-vertex certificates cover minimum degree at least four, a vertex of degree exactly eleven, every edge in a triangle, and packing number at most four. [Statement and certificate replay](CERTIFICATE.md#changes-for-thirteen-vertices)
- Three further certificates cover 13-vertex graphs with a universal vertex, minimum degree at least four, and packing number at most three.

Combining these certificates with Kandasamy's theorem and an elementary reduction proves the inequality for all finite simple graphs on at most twelve vertices with packing number at most five, and on at most thirteen vertices with packing number at most three. At thirteen vertices the bound rises to four when the maximum degree is at most eleven. [Proof of the corollaries](CERTIFICATE.md#removing-the-minimum-degree-and-triangle-incidence-assumptions)

```sh
python search.py mckay-connected8.g6
python extend_equality.py mckay-connected8.g6
python structured.py --count 100
```

Use Python 3.10, NetworkX 3.3, and `python-sat==1.9.dev25`. The eight-vertex graph data are from Brendan McKay's catalogue, CC BY 4.0. [Licence and source](https://users.cecs.anu.edu.au/~bdm/data/graphs.html)
