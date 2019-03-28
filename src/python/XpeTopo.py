"""
Experiments around a well-known graph with peculiar topology.

This file does not intend to be full part of the project at the end. Need to construct generic framework around
the experiments done here.

Input to the program is the mtx file representing the graph to explore.
"""

from sys import argv
from time import time
from typing import List, Dict


class ProgramConfiguration:
    """User arguments

    Verifies that the program is supplied enough arguments and provides one function for
    each argument type.
    """

    def __init__(self, args: List[str]):
        if len(args) != 2:
            print("Usage: %s <mtx file>" % args[0])
            exit(1)
        self.args = args

    def input_file(self) -> str:
        return self.args[1]


class Graph:
    """
    Use an internal representation of the graph, suitable for the exploration requirements.
    Representation is node centric:
      * Record vertices with their edges
      * Each edge is recorded in both direction
    Keep all this in a map of lists:
      * Given the node n
      * map(n) = list of nodes connected to n
    """

    def __init__(self):
        self.map: Dict[int, List[int]] = {}

    def from_mtx_file(self, file_name: str):
        # Count the current "effective" line (i.e. non empty and not a comment). After the first line is read
        # we get edge descriptions
        line_count = 0
        print("loading %s" % file_name)
        start_time = time()
        with open(file_name, "rt") as f:
            each_line = f.readline()
            while each_line:
                if not each_line.startswith("%"):
                    line_count += 1
                    if line_count >= 2:
                        nodes = each_line.split(" ")
                        source = int(nodes[0])
                        destination = int(nodes[1])
                        self.register(source, destination)
                each_line = f.readline()
        print("file loaded in %d seconds" % (time() - start_time))
        return self

    def register(self, x: int, y: int):
        self.__add_or_update(x, y)
        self.__add_or_update(y, x)

    def __add_or_update(self, x: int, y: int):
        existing = self.map.get(x)
        if existing:
            existing.append(y)
        else:
            self.map.update({x: [y]})


class TreePartition:
    """
    A "tree partition" is a collection of sparse nodes joined by a common dense node (called root)
    It can be considered as a partition belonging to the peripheral area of the graph.
    It consists of a map containing the node and the leaves reachable from that dense node
    """

    def __init__(self, tree_id: int, root: int):
        self.root = root
        self.tree_id = tree_id
        self.graph: Graph = Graph()

    def add_nodes_from_root_in_graph(self, tree_ids: Dict[int, List[int]], reference_graph: Graph):
        print("creating tree partition starting from root node %d" % self.root)
        self.__add_nodes_from_sibling_in_graph(self.root, tree_ids, reference_graph)
        return self

    def __add_nodes_from_sibling_in_graph(self, node: int, tree_ids, reference_graph: Graph):
        # Given the tree id, rebuild all the nodes that can be joined in that
        # tree. => n -> t, for each sibling s, if s is in t then add.
        siblings = reference_graph.map.get(node)
        for each_sibling in siblings:
            sibling_tree_ids = tree_ids.get(each_sibling)
            if sibling_tree_ids and sibling_tree_ids.__contains__(self.tree_id):
                self.graph.register(node, each_sibling)
                self.__add_nodes_from_sibling_in_graph(each_sibling, tree_ids, reference_graph)


class Classifier:
    """
    Applies the experimental classification criteria to produce the exploration
    results of a graph.
    """

    def __init__(self, graph: Graph):
        self.graph = graph

    def search_nodes_with_weight(self, weight: int) -> List[int]:
        result = []
        for each_key in self.graph.map:
            connected_nodes = self.graph.map.get(each_key)
            if len(connected_nodes) == weight:
                result.append(each_key)
        return result

    def build_trees(self):
        leaves = self.search_nodes_with_weight(1)
        trees: List[TreePartition] = []
        # Parse each path starting from a leaf. Each encountered node is recorded in a local
        # map (chain map) with the list of starting leaves. A good candidate for having
        # a forest is a node in the map with large list of leaves.
        chain_map: Dict[int, List[int]] = {}
        for each_leaf in leaves:
            # Record this leaf in the chain map and start from its sibling.
            # We may have a case like this:
            #  X ------ A ---...---
            #  Y ------ A ---...---
            # In this case, if X is visited first, A belongs to chain 'X'.
            # Revisit from Y, so that A and all the nodes in chain 'X' will also be part
            # of chain 'Y'.
            existing = chain_map.get(each_leaf)
            if existing:
                existing.append(each_leaf)
            else:
                chain_map.update({each_leaf: [each_leaf]})
            first_sibling = self.graph.map.get(each_leaf)[0]
            self.__build_chain(first_sibling, 4, chain_map, each_leaf)
        for each_node in chain_map:
            chains = chain_map.get(each_node)
            if len(chains) > 10:
                for each_chain_id in chains:
                    # Verify that each_chain_id is not already built
                    todo
                    trees.append(
                        TreePartition(each_node, each_chain_id).add_nodes_from_root_in_graph(chain_map, self.graph))
        return trees

    def __build_chain(self, node: int, chain_length, cm: Dict[int, List[int]], chain_id: int):
        if chain_length == 0:
            return
        siblings = self.graph.map.get(node)
        if len(siblings) == 1:
            # Reached a leaf ending another chain... Forget about it, it will
            # be handled by another iteration of build_tree (see the big comment above).
            return
        else:
            # This node belongs to the registered chain...
            existing = cm.get(node)
            if existing:
                existing.append(chain_id)
            else:
                cm.update({node: [chain_id]})
        # If the node density is not too high, then let's continue the chain with the
        # siblings
        if len(siblings) <= 2:
            for each_sibling in siblings:
                self.__build_chain(each_sibling, chain_length - 1, cm, chain_id)


# ================================================================================

def __main(configuration: ProgramConfiguration):
    graph = Graph().from_mtx_file(configuration.input_file())
    classifier = Classifier(graph)
    trees = classifier.build_trees()
    print("created %d trees" % len(trees))


# ================================================================================
__main(ProgramConfiguration(argv))
