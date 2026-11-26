# Finite Tuza certificates for graphs with a high-degree vertex

Let $G$ be a simple graph on twelve vertices with a universal vertex and minimum degree at least four. Write $\nu(G)$ for its triangle packing number and $\tau(G)$ for its triangle edge-cover number. The checked certificates establish $\tau(G)\leq2\nu(G)$ when $\nu(G)\leq6$. The packing-six manuscript proves the same inequality at every order. [Analytic proof](PACKING-SIX.md)

The thirteen-vertex case uses a vertex of degree exactly eleven, minimum degree at least four, and the additional condition that every edge lies in a triangle. The four certificates give $\tau(G)\leq2\nu(G)$ for $\nu(G)\leq4$ in this class.

Four additional certificates give $\tau(G)\leq2\nu(G)$ when $G$ has thirteen vertices, a universal vertex, minimum degree at least four, and $\nu(G)\leq4$. Their master formulas use the same cone constraints as at order twelve, with twelve noncentral vertices.

Together with Kandasamy's maximum-degree-ten theorem, the certificates imply the following cases of Tuza's conjecture without minimum-degree or triangle-incidence assumptions. [Kandasamy's theorem](https://arxiv.org/abs/2610.15269)

- Every finite simple graph on at most twelve vertices with packing number at most six.
- Every finite simple graph on at most thirteen vertices with packing number at most four.

## Searching the packing-eight domain

The spanning-packing theorem reduces packing eight to orders 12–17 with a vertex of degree at least eleven. For each order, choose an anchor degree from eleven through order minus one. The new encoding lets labels up to that degree be the anchor's neighbors and the other labels be its nonneighbors. The lexicographic maximum now ranges over permutations within each of those two groups. The cut constraints use the actual edge variables, and the averaged bound still uses the universal-vertex upper bound on the number of spokes within a cut. [Spanning-packing theorem](SPANNING-PACKING.md)

The option `--spanning-packing` adds a separate selection variable for each triangle. Exactly eight are selected in the packing-eight run. Selected triangles must be present and can share no edge. Each vertex must lie in at least one selected triangle. Each actual triangle must meet a selected edge, as it would in any maximum packing. The packing and cover refinements still test for nine edge-disjoint triangles and for a cover of at most sixteen edges.

```sh
python synthesis.py --order 17 --anchor-degree 11 --packing 8 --min-degree 5 --reduced --spanning-packing --limit 3000 --export packing8-order17-degree11
```

If the master terminates as unsatisfiable, pass the same order, packing, degree, and encoding options to `replay_synthesis.py` with `--prefix` in place of `--export`. A trial-limit output is a bounded search and proves no slice unsatisfiable.

## Removing the minimum-degree and triangle-incidence assumptions

Both classes in the corollary are closed under taking subgraphs. Choose a counterexample in either class with the fewest vertices and then the fewest edges. Deleting an edge in no triangle leaves $\tau$ and $\nu$ unchanged, so every edge lies in a triangle.

Suppose a vertex $v$ has degree at most three. If it lies in no triangle, delete it. Otherwise, if it lies in one or two triangles, form $H$ by deleting $v$ and the one or two edges opposite $v$ in those triangles. Add those opposite edges to any triangle cover of $H$ to cover $G$. If $v$ lies in three triangles, its neighbors are a triangle $abc$. Form $H$ by deleting $v$ and edge $ab$. Adding $ab$ and $vc$ to a triangle cover of $H$ covers $G$.

In both cases with at least one triangle through $v$, any packing in $H$ can be extended by a triangle through $v$ whose opposite edge was deleted. Thus $\nu(G)\geq\nu(H)+1$ and $\tau(G)\leq\tau(H)+2$. Since $H$ has fewer vertices, this contradicts the choice of $G$. The minimum degree of $G$ is at least four.

Kandasamy's theorem forces maximum degree at least eleven. Any remaining graph of order twelve has a universal vertex and is covered by the first family of certificates. The remaining graphs of order thirteen have maximum degree eleven or twelve. If the maximum degree is eleven, use the certificates for a degree-eleven vertex with one nonneighbor. If it is twelve, use the thirteen-vertex cone certificates.

## Why the encoding covers this class

Fix a label $0$ for the universal vertex. An edge variable records whether an edge is in $G$, and a triangle variable is true exactly when its three edge variables are true. All leaf-graph edges lie in triangles through $0$. A spoke also belongs to a triangle because its other endpoint has at least three neighbors among the other noncentral vertices. Thus the requirement that every edge belongs to a triangle preserves every graph in the stated class.

Fix an integer $k$. A graph with $\tau(G)>2k$ has at least $2k+1$ within-side edges in every bipartition, since these edges meet every triangle. For the lower bound on the number of nonspoke edges, fix $s$ of the eleven noncentral vertices on the side of $0$. Averaging over all such $s$-subsets, the expected number of within-side edges is

$$
s + m\,\frac{\binom{s}{2}+\binom{11-s}{2}}{\binom{11}{2}},
$$

where $m$ is the number of nonspoke edges. This expectation must be at least $2k+1$. The master formula also imposes the within-side bound on eighteen fixed bipartitions.

Among labelings fixing $0$, choose one that maximizes the upper-triangular adjacency vector lexicographically in row order. Interchanging consecutive noncentral labels exchanges two adjacency rows off the positions of those labels. The first changed bit of the upper triangle is the first difference between the compared rows in label order. Consequently the lexicographically maximal labeling satisfies each encoded consecutive row inequality.

## Why the refinements preserve a counterexample

Each packing refinement forbids the simultaneous presence of the edges of a particular packing of $k+1$ edge-disjoint triangles. Each cover refinement requires at least one triangle disjoint from a particular edge set of size at most $2k$. Either requirement holds for every graph with $\nu(G)\leq k$ and $\tau(G)>2k$. The replay checks packing refinements by partitioning their edges into triangles. For cover refinements, it reconstructs an edge set that is disjoint from exactly the triangles in the logged clause. It rebuilds the master CNF from these verified refinements and requires equality with the stored master. A separate SAT solver and DRAT-trim check unsatisfiability.

Certificates for $k=1,2,3,4,5,6$ exclude $\nu(G)\leq k$ and $\tau(G)>2k$ for each successive threshold. Taking $k=\nu(G)$ proves the stated inequality, with the zero case immediate.

For packing six, the replay verified 411,520 packing refinements and 807 cover refinements. It rebuilt the 423,382-clause formula, matched it to the archived CNF, and checked unsatisfiability with CaDiCaL. Glucose generated the proof accepted by DRAT-trim. [Verification record](certificates/tuza-cone12-k6.verified.txt)

## Changes for thirteen vertices

Fix labels $0$ and $12$ for the degree-eleven vertex and its only nonneighbor. Edge $0,12$ is absent. The minimum degree and triangle-incidence clauses operate on the graph itself, so the triangle-incidence hypothesis is part of the theorem.

Let $m$ count edges among the twelve vertices other than $0$. For a uniformly chosen $s$-subset of these twelve vertices on the side of $0$, the mean number of edges lying within the two sides is

$$
\frac{11s}{12} + m\,\frac{\binom{s}{2}+\binom{12-s}{2}}{\binom{12}{2}}.
$$

The encoding uses $s$ in place of $11s/12$. This increases the averaged expression, so a counterexample still forces the encoded lower bound on $m$. The eighteen fixed cuts count actual edges, including the forced absence of edge $0,12$. The lexicographic maximum now ranges over permutations fixing both labels. The same consecutive-row argument applies to the remaining eleven labels, and their rows still include the coordinate for label $12$.

The refinement semantics are unchanged. For each $k=1,2,3,4$, the certificate excludes a graph with $\nu(G)\leq k$ and $\tau(G)>2k$. For a graph with packing number from one to four, use the certificate with $k=\nu(G)$.

The four masters use 187,145 refinements altogether. A fresh referee independently verified every logged witness and its position in the saved master CNF. DRAT-trim accepted every proof. This verifies the stated finite class.

### The packing number is at least three

The first two thresholds can also be ruled out without SAT. Let $F$ be the graph induced by the eleven neighbors of $0$, and let $x$ be its only nonneighbor. The minimum degree of $F$ is at least two. A matching of size three in $F$ gives three edge-disjoint triangles through $0$.

Otherwise a maximum matching of $F$ has size two. If it had size one, the unmatched vertices would form an independent set and each would be adjacent to both endpoints, giving a matching of size two. For a maximum matching of size two, let $U$ be the independent set of seven unmatched vertices. If both endpoints of one matching edge have neighbors in $U$, they must have exactly one shared neighbor there. Distinct neighbors would replace that edge by two and augment the matching. All other vertices of $U$ must then meet both endpoints of the other edge to have degree at least two, which also permits augmentation. If neither endpoint of one edge meets $U$, the other edge likewise permits augmentation. Thus exactly one endpoint of each matching edge meets $U$. Call them $a,c$. Every vertex of $U$ meets both.

Any edge of $F$ outside $\{a,c\}$, together with edges from $a,c$ to distinct unused vertices of $U$, would form a matching of size three. Each of the nine remaining vertices therefore meets both $a$ and $c$, by the minimum degree. The vertex $x$ has a neighbor $p$ among these nine vertices because $d(x)\geq4$. The edge $xp$ lies in a triangle, so $x$ meets $a$ or $c$, say $a$. For distinct $p,q,r$ among the nine vertices, the triangles $xap$, $0aq$, and $0cr$ are edge-disjoint.

## Searching only minimal counterexamples

The optional `--reduced` search uses two more conditions on a counterexample chosen with the fewest edges, breaking ties by order. The ambient class here consists of all graphs below the chosen order and packing bounds. A graph can leave its anchor or degree slice after an edge deletion, so the reduction uses minimality in the ambient class.

Every edge of a minimal counterexample lies in at least two triangles. If an edge lies in no triangle, deleting it preserves both numbers. If it lies in exactly one triangle, delete the three edges of that triangle. The triangle extends any packing of the smaller graph. Adding its other two edges to a cover of the smaller graph meets every triangle lost by the deletion.

The link at $v$ is the graph on its neighbors. Fix a set $W$ of labels other than $v$, a nonempty matching $M$ of opposite edges inside $W$, and a set $Q\subseteq W$ of size at most $|M|$. Suppose each matching edge gives an actual triangle at $v$, and every other triangle at $v$ that uses a spoke to $W$ also uses a spoke to $Q$. Delete the actual spokes to $W$ and the edges of $M$ to form $H$. The $|M|$ triangles extend any packing of $H$. A cover of $H$ extends to one of $G$ by adding $M$ and the actual spokes to $Q$. Thus

$$
\nu(G)\geq\nu(H)+|M|,\qquad
\tau(G)\leq\tau(H)+2|M|.
$$

A minimal counterexample cannot meet those conditions. The corresponding SAT clause allows a matching triangle to disappear or an uncovered triangle touching a scoped spoke to appear. The replay independently reconstructs the exact allowed literals from each stored $(v,W,M,Q)$. The generator obtains a witness from a link component by finding a matching and a vertex cover of the edges left after removing it. Earlier whole-link logs omit $W$, in which case replay takes all nonapex labels. [Link reduction in the literature](https://arxiv.org/html/2611.11128v1)

For a fixed packing threshold $k$, the master imposes $\nu\leq k$ and $\tau>2k$. An unsatisfiable master therefore excludes only minimal counterexamples at actual packing number $k$, or with cover exceeding $2k$ despite smaller packing. The lower packing cases and all possible order and maximum-degree slices must be covered before concluding the whole ambient class satisfies Tuza.

## Replay

Unpack the gzip files in the certificates directory. For each prefix, run the independent refinement replay in ordinary Python with assertions enabled. Then use DRAT-trim on the saved CNF and DRAT files. [DRAT-trim source at the tested revision](https://github.com/marijnheule/drat-trim/tree/2e3b2dc0ecf938addbd779d42877b6ed69d9a985)

    python replay_synthesis.py --order 12 --min-degree 4 --packing 4 --prefix certificates/tuza-cone12-k4
    drat-trim certificates/tuza-cone12-k4.cnf certificates/tuza-cone12-k4.drat
    python replay_synthesis.py --order 12 --min-degree 4 --packing 6 --prefix certificates/tuza-cone12-k6
    drat-trim certificates/tuza-cone12-k6.cnf certificates/tuza-cone12-k6.drat
    python replay_synthesis.py --order 13 --min-degree 4 --packing 4 --missing-one --prefix certificates/tuza-near-cone13-k4
    drat-trim certificates/tuza-near-cone13-k4.cnf certificates/tuza-near-cone13-k4.drat
    python replay_synthesis.py --order 13 --min-degree 4 --packing 4 --prefix certificates/tuza-cone13-k4
    drat-trim certificates/tuza-cone13-k4.cnf certificates/tuza-cone13-k4.drat

On MinGW, compiling DRAT-trim with the flag -Dgetc_unlocked=getc replaces its single-threaded file-reading primitive with the available equivalent. The retained verification summaries record the checker result.
