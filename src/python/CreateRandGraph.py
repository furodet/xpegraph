"""
Generates a random graph in mtx format.

Inputs to this program are:
  * The number of nodes in the generated graph
  * The graph density, expressed as a density of edges per node
  * The output mtx file
"""
import random
from datetime import datetime
from sys import argv
from typing import List


class ProgramConfiguration:
    """User arguments

    Verifies that the program is supplied enough arguments and provides one function for
    each argument type.
    """

    def __init__(self, args: List[str]):
        if len(args) != 4:
            print("Usage: %s <nr nodes> <edge density> <output file>" % args[0])
            exit(1)
        self.args = args

    def nr_nodes(self) -> int:
        return int(self.args[1])

    def density(self) -> int:
        return int(self.args[2])

    def output_file(self) -> str:
        return self.args[3]


class Edge:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y


class RandomGraph:
    def __init__(self, nr_nodes: int, density: int):
        self.nr_nodes = nr_nodes
        self.nr_edges = 0
        self.density = density
        self.edges = []

    def generate(self, seed: int):
        """
        Generates a random graph.

        :param seed: a random seed
        :return: self
        """
        random.seed(seed)
        for each_node in range(1, self.nr_nodes):
            '''
            Each node has a potential chance to be connected to this node:
              * Given that nr_nodes are present
              * And given that each node has an average of density 'D' neighbors
              * Then this node has D chances out of nr_nodes chances to be a neighbor
            
            The problem is that this method may generate orphan nodes. So we implement
            an additional post-processing mechanism to have at least one connection for
            the orphans.
            '''
            nr_neighbors = 0
            for each_other_node in range(each_node + 1, self.nr_nodes):
                pick = random.randint(1, self.nr_nodes)
                if pick < self.density:
                    self.__record_edge(each_node, each_other_node)
                    nr_neighbors += 1
            if nr_neighbors == 0:
                a_neighbor = random.randint(1, self.nr_nodes)
                self.__record_edge(each_node, a_neighbor)
        return self

    def __record_edge(self, x: int, y: int):
        self.nr_edges += 1
        self.edges.append((x, y))


class MtxFile:
    def __init__(self, output_file: str, random_graph: RandomGraph):
        self.output_file = output_file
        self.random_graph = random_graph

    def create(self):
        with open(self.output_file, "wt") as f:
            f.write("%%MatrixMarket matrix coordinate pattern symmetric\n")
            f.write("%d %d %d\n" % (self.random_graph.nr_nodes, self.random_graph.nr_nodes, self.random_graph.nr_edges))
            for each_edge in self.random_graph.edges:
                f.write("%d %d\n" % (each_edge[0], each_edge[1]))


# ================================================================================
configuration = ProgramConfiguration(argv)
now_epoch = int(datetime.now().strftime('%s'))
g = RandomGraph(configuration.nr_nodes(), configuration.density()).generate(now_epoch)
print("generated graph: %d nodes %d edges" % (g.nr_nodes, g.nr_edges))
MtxFile(configuration.output_file(), g).create()
print("graph saved into %s" % configuration.output_file())
