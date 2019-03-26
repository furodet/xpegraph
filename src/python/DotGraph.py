"""
Converts a graph file (mtx) to dot, in order to visualize the graph with neato.

Input to this program are:
  * The initial graph file, which must be an mtx file
    * First node index must be 1
    * Edges are not weighted
  * An output file containing resulting dot script

"""

from sys import argv
from time import time

from scipy.io import mmread


class ProgramConfiguration:
    def __init__(self, args):
        if len(args) != 3:
            print("Usage: DotGraph.py <mtx file> <dot file>")
            exit(1)
        self.args = args

    def input_file(self):
        return self.args[1]

    def output_file(self):
        return self.args[2]


# ================================================================================
configuration = ProgramConfiguration(argv)
print("loading file %s" % configuration.input_file())
start_time = time()
graph = mmread(configuration.input_file()).tocoo()
print("file loaded in %d seconds" % (time() - start_time))

with open(configuration.output_file(), "wt") as f:
    f.write("strict graph {\n  overlap = false;\n  splines = true;\n  node[shape=record, height=.1, fontsize=8];\n")
    for each_row_index in range(graph.shape[0]):
        row = graph.getrow(each_row_index)
        for each_col_index in row.indices:
            row_id = each_row_index + 1
            col_id = each_col_index + 1
            f.write("    %d -- %d [color=\"blue\"]\n" % (each_row_index + 1, each_col_index + 1))
    f.write("  }\n\n")

print("TO PLOT THIS GRAPH: neato -T<format> -o... < %s" % configuration.output_file())
