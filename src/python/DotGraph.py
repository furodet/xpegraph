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
from typing import List

from scipy.io import mmread
from scipy.sparse import coo_matrix


class ProgramConfiguration:
    def __init__(self, args: List[str]):
        if len(args) != 3:
            print("Usage: DotGraph.py <mtx file> <dot file>")
            exit(1)
        self.args = args

    def input_file(self) -> str:
        return self.args[1]

    def output_file(self) -> str:
        return self.args[2]


class DotGenerator:
    def __init__(self, coo: coo_matrix, out: str):
        self.coo = coo
        self.out = out

    def create_file(self):
        with open(self.out, "wt") as f:
            f.write(
                "strict graph {\n  overlap = false;\n  splines = true;\n  node[shape=record, height=.1, fontsize=8];\n")
            for each_row_index in range(graph.shape[0]):
                row = graph.getrow(each_row_index)
                for each_col_index in row.indices:
                    row_id = each_row_index + 1
                    col_id = each_col_index + 1
                    f.write("    %d -- %d [color=\"blue\"]\n" % (row_id, col_id))
            f.write("  }\n\n")


# ================================================================================
configuration = ProgramConfiguration(argv)
print("loading file %s" % configuration.input_file())
start_time = time()
graph = mmread(configuration.input_file())
DotGenerator(graph.tocoo(), configuration.output_file()).create_file()
print("file loaded in %d seconds" % (time() - start_time))

print("TO PLOT THIS GRAPH: neato -T<format> -o... < %s" % configuration.output_file())
