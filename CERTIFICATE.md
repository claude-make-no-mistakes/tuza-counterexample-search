# A finite Tuza certificate for cones on twelve vertices

Let $G$ be a simple graph on twelve vertices with a universal vertex and minimum degree at least four. Write $\nu(G)$ for its triangle packing number and $\tau(G)$ for its triangle edge-cover number. The checked certificates establish $\tau(G)\leq2\nu(G)$ when $\nu(G)\leq5$.

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

## Replay

Unpack the gzip files in the certificates directory. For each prefix, run the independent refinement replay in ordinary Python with assertions enabled. Then use DRAT-trim on the saved CNF and DRAT files. [DRAT-trim source at the tested revision](https://github.com/marijnheule/drat-trim/tree/2e3b2dc0ecf938addbd779d42877b6ed69d9a985)

    python replay_synthesis.py --order 12 --min-degree 4 --packing 4 --prefix certificates/tuza-cone12-k4
    drat-trim certificates/tuza-cone12-k4.cnf certificates/tuza-cone12-k4.drat

On MinGW, compiling DRAT-trim with the flag -Dgetc_unlocked=getc replaces its single-threaded file-reading primitive with the available equivalent. The retained verification summaries record the checker result.
