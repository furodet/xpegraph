# xpegraph
Experiments around graph partitioning using scikit-learn
========================================================

This project is a collection of scripts and methods to study clustering of big graphs.

Python scripts can be found in src/python. They use scikit-learn:
```
  pip install scikit-learn
```

Python scripts require type-checking features, available since **Python 3.6**. Project does
not work with older versions of Python.

Project structure
-----------------

  * src/python: the scripts
  * resources: a bunch of small graphs to make preliminary experiments

The scripts
-----------

  * BuildCluster.py: gets an mtx file and creates the corresponding partitions
    * Output is a "partition file" in proprietary format:
      * Comments = "// ..."
      * Nodes = (P.N):(P':N') where P is a partition number and N a node identifier
    * The input graph must be:
      * Non-oriented
      * No weighted edges
      * Node identifier must be (1,2...)
  * BuildFragments.py: reads a cluster to produce mtx files describing the different partitions:
      * Sub-graphes implementing each fragment
      * A "meta-graph" that inter-connects the fragments via "virtual nodes"
  * DotGraph.py: translates an mtx file to a dot script, which can be plotted with neato
  * CreateRandGraph.py: creates a random graph, for tests

Example
-------
Reference: Zachary's Karate club (http://konect.cc/networks/ucidata-zachary/)

```
  python BuildCluster.py ../../resources/zachary.mtx 4 ../../clusters/zachary.txt
```

Produces the output cluster file `../../clusters/zachary.txt`:
```
  // source: /home/david/work/xpegraph/resources/zachary.mtx
  // nr partitions: 4
  // cluster: [0 0 0 0 3 3 3 0 2 2 3 0 0 0 2 2 3 0 2 0 2 0 2 1 1 1 2 1 0 2 2 1 2 2]
  // node #1 : cluster[0]=0
  (0.1):(1.32)
  (0.1):(0.22)
  (0.1):(0.20)
...
```

The four first lines are comments, next ones describe connections from node 1, in partition number 0:
  * (0.1):(1:32): node 1 is connected to node 32 in partition 1
  * (0.1):(0:22): node 1 is connected to node 22 in the same partition
  * (0.1):(0.20): node 1 is connected to node 20 in the same partition

```
  python BuildFragments.py ../../clusters/zachary.txt ../../clusters/zachary_cluster
```

Creates 4 files (one per partition, called zachary_cluster_#N) representing the sub-graphes and a file,
called zachary_cluster_meta.mtx, representing the "meta-graph".


