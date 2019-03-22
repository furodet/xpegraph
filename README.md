# xpegraph
Experiments around graph partitioning using scikit-learn
========================================================

This project is a collection of scripts and methods to study clustering of big graphs.

Python scripts can be found in src/python. They use scikit-learn:
```
  pip install scikit-learn
```

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
  * DotGraph.py: translates an mtx file to a dot script, which can be plotted with neato
