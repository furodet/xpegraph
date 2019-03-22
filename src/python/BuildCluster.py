"""
Partitions a graph in smaller graphs

Input to this program are:
  * The initial graph file, which must be an mtx file
    * First node index must be 1
    * Edges are not weighted
  * The number of partitions to create
  * An output file containing clustering result

Output is a cluster description, in a proprietary text format:
  * Each line is either a comment (starting with //)
  * Or the description of a edge, in the form:
    * (P.N):(P':N') where (P:N) is the source node (P=partition number, N=node identifier) and
      (P':N') is the target node
"""

from sys import argv
from time import time

from scipy.io import mmread
from sklearn.cluster import SpectralClustering


class ProgramConfiguration:
    """User arguments

    Verifies that the program is supplied enough arguments and provides one function for
    each argument type.
    """

    def __init__(self, args):
        if len(args) != 4:
            print("Usage: %s <mtx file> <number of partitions> <output file>" % args[0])
            exit(1)
        self.args = args

    def input_file(self):
        return self.args[1]

    def output_file(self):
        return self.args[3]

    def nr_partitions(self):
        return int(self.args[2])


class Cluster:
    """Invokes spectral clustering on a graph to create a given number of partitions
    """

    def __init__(self, graph, nr_partitions):
        self.graph = graph
        self.sc = SpectralClustering(nr_partitions, affinity="precomputed", n_init=100)

    def create(self):
        self.sc.fit(self.graph)
        return self.sc.labels_


class ClusterPrinter:
    """
    Unwraps a cluster to produce sub-graphs.
    For example (5.8):(7.10) means "node number 8 in sub-graph 5 is connected to node number 10 in sub-graph 10)
    """

    def __init__(self, cluster, graph):
        self.cluster = cluster
        self.graph = graph

    def write_into(self, out):
        for node_id in range(len(self.cluster)):
            # Assume nodes are indexed from 1 to N
            source_node_index = node_id + 1
            source_sg_index = self.cluster[node_id]
            out.write("// node #%d : cluster[%d]=%d\n" % (source_node_index, node_id, source_sg_index))
            row = self.graph.getrow(node_id)
            for each_col_index in row.indices:
                target_node_index = each_col_index + 1
                target_sg_index = self.cluster[each_col_index]
                out.write(
                    "(%d.%d):(%d.%d)\n" % (source_sg_index, source_node_index, target_sg_index, target_node_index))


# ================================================================================
class Main:
    def __init__(self, program_configuration):
        self.input_file = program_configuration.input_file()
        self.nr_partitions = program_configuration.nr_partitions()
        self.output_file = program_configuration.output_file()

    def execute(self):
        g = self.__load_file(self.input_file)
        c = self.__partition(g, self.nr_partitions)
        self.__write_result(self.output_file, g, c, self.input_file, self.nr_partitions)

    @classmethod
    def __load_file(cls, input_file):
        print("loading file %s" % input_file)
        start_time = time()
        graph = mmread(input_file)
        print("file loaded in %d seconds" % (time() - start_time))
        return graph

    @classmethod
    def __partition(cls, graph, nr_partitions):
        print("partitioning")
        start_time = time()
        cluster = Cluster(graph, nr_partitions).create()
        print("partitioning complete in %d seconds" % (time() - start_time))
        return cluster

    @classmethod
    def __write_result(cls, output_file, graph, cluster, input_file, nr_partitions):
        with open(output_file, "wt") as f:
            f.write("// source: %s\n" % input_file)
            f.write("// nr partitions: %s\n" % nr_partitions)
            f.write("// cluster: %s\n" % str(cluster))
            ClusterPrinter(cluster, graph).write_into(f)
            f.write("\n")
            print("cluster written into %s" % output_file)


# ================================================================================
configuration = ProgramConfiguration(argv)
Main(configuration).execute()
