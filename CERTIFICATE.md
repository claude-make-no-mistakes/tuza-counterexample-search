# Finite Tuza certificates for graphs with a high-degree vertex

Let $G$ be a simple graph on twelve vertices with a universal vertex and minimum degree at least four. Write $\nu(G)$ for its triangle packing number and $\tau(G)$ for its triangle edge-cover number. The checked certificates establish $\tau(G)\leq2\nu(G)$ when $\nu(G)\leq5$.

The thirteen-vertex case uses a vertex of degree exactly eleven, minimum degree at least four, and the additional condition that every edge lies in a triangle. The four certificates give $\tau(G)\leq2\nu(G)$ for $\nu(G)\leq4$ in this class.

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

Certificates for $k=1,2,3,4,5$ therefore exclude $\nu(G)\leq k$ and $\tau(G)>2k$ for each successive threshold. Taking $k=\nu(G)$ proves the stated inequality, with the zero case immediate.

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

## Replay

Unpack the gzip files in the certificates directory. For each prefix, run the independent refinement replay in ordinary Python with assertions enabled. Then use DRAT-trim on the saved CNF and DRAT files. [DRAT-trim source at the tested revision](https://github.com/marijnheule/drat-trim/tree/2e3b2dc0ecf938addbd779d42877b6ed69d9a985)

    python replay_synthesis.py --order 12 --min-degree 4 --packing 4 --prefix certificates/tuza-cone12-k4
    drat-trim certificates/tuza-cone12-k4.cnf certificates/tuza-cone12-k4.drat
    python replay_synthesis.py --order 13 --min-degree 4 --packing 4 --missing-one --prefix certificates/tuza-near-cone13-k4
    drat-trim certificates/tuza-near-cone13-k4.cnf certificates/tuza-near-cone13-k4.drat

On MinGW, compiling DRAT-trim with the flag -Dgetc_unlocked=getc replaces its single-threaded file-reading primitive with the available equivalent. The retained verification summaries record the checker result.
