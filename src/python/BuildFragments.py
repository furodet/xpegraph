"""
Reads a cluster file (produced by BuildCluster) to produce sub-graphes and a "meta-graph" that interconnects
them.

Inputs to this program are:
  * The initial cluster description
  * A "base name" for the output files. Given that the base name is 'foo', for example, the outputs are:
    * foo_XXX.txt: sub-graph files (XXX is the partition number)
    * foo_meta.txt: a description of the interconnecting graph

TODO: sub-graphs should be mtx files... But we need to compute the matrix sizes and then inject them at the beginning
TODO: in each sub-graph, define a way to map "external connections"... These are sorts of "virtual nodes"
"""

from sys import argv

# Expect the cluster builder to provide the number of partitions in a comment looking like this:
NR_PARTITIONS_ID = "// nr partitions: "


class ProgramConfiguration:
    """User arguments

    Verifies that the program is supplied enough arguments and provides one function for
    each argument type.
    """

    def __init__(self, args):
        if len(args) != 3:
            print("Usage: %s <cluster file> <output base name>" % args[0])
            exit(1)
        self.args = args

    def input_file(self):
        return self.args[1]

    def output_radix(self):
        return self.args[2]


class Node:
    def __init__(self, partition, index):
        self.partition = partition
        self.index = index

    def __str__(self):
        return "%s.%s" % (self.partition, self.index)


class Edge:
    def __init__(self, node1, node2):
        self.x = node1
        self.y = node2

    def __str__(self):
        return "(%s):(%s)" % (self.x, self.y)


class EdgeReader:
    """
    Creates an edge from a textual description of the cluster file ("(P.N):(P'.N')")
    """

    def __init__(self, line):
        self.line = line

    def translate(self):
        items = self.line.replace("(", "").replace(")", "").split(":")
        if len(items) == 2:
            (node1, node2) = map(lambda s: s.split("."), items)
            return Edge(Node(node1[0], node1[1]), Node(node2[0], node2[1]))


class Partition:
    """
    Maintains the information of 1 sub-graph
    """

    def __init__(self, base_name, index):
        self.index = index
        self.nr_edges = 0
        file_name = "%s_%s.txt" % (base_name, index)
        print "creating file %s" % file_name
        self.file = open(file_name, "wt")

    def add_edge(self, edge):
        self.file.write("%s\n" % edge)

    def close(self):
        self.file.write("\n")
        self.file.close()


class MetaGraph:
    """
    A "virtual" graph representing the interconnects between nodes.
    """

    def __init__(self, output_radix):
        file_name = "%s_meta.txt" % output_radix
        print("creating file %s" % file_name)
        self.file = open(file_name, "wt")
        # Virtual node counter: whenever adding a new inter-connect from P:X to Q:Y, create one
        # edge from virtual node P to virtual node "PXQY" and one from this new virtual node to
        # virtual node Q. Need a counter to assign arbitrary indexes to "PXQY"
        self.vnode_counter = 0

    def set_nr_partitions(self, nr_partitions):
        self.vnode_counter = nr_partitions + 1

    def record(self, x, y):
        # Graph is non-oriented. No need to record edges in the two directions. The arbitrary rule then
        # is to record the interconnect iff the target partition is greater than the source one.
        px = int(x.partition)
        py = int(y.partition)
        if px < py:
            self.file.write("%% %s:%s" % (x, y))
            self.file.write("%d %d\n" % (px, self.vnode_counter))
            self.file.write("%d %d\n" % (self.vnode_counter, py))
            self.vnode_counter += 1

    def close(self):
        self.file.write("\n")
        self.file.close()


class PartitionMap:
    """
    Mapping of all the sub-graphs, indexed by partition index, along with the file that records "crossing edges".
    """

    def __init__(self, output_radix):
        self.file_map = {}
        self.output_radix = output_radix
        self.meta = MetaGraph(output_radix)

    def get_or_create(self, key):
        """
        Searches for the partition with the given key. If not found, creates a new sub-graph.

        :param key: the partition index
        :return: The existing or new partition
        """
        if key not in self.file_map:
            self.file_map[key] = Partition(self.output_radix, key)
        return self.file_map[key]

    def close_all(self):
        """
        Closes all the partition files mapped by this.
        """
        for each_partition in self.file_map.items():
            each_partition[1].close()
        self.meta.close()


class EdgeProcessor:
    """
    Performs the actual work of this program. Gets edges one by one and writes out the fragmentation information.
    """

    def __init__(self, output_radix):
        self.partition_map = PartitionMap(output_radix)

    def set_nr_partitions(self, nr_partitions):
        self.partition_map.meta.set_nr_partitions(nr_partitions)

    def handle_edge(self, edge):
        partition = self.partition_map.get_or_create(edge.x.partition)
        partition.add_edge(edge)
        if edge.x.partition != edge.y.partition:
            self.partition_map.meta.record(edge.x, edge.y)

    def close_all(self):
        """
        Closes all the partition files created during the process
        """
        self.partition_map.close_all()


# ================================================================================
configuration = ProgramConfiguration(argv)
processor = EdgeProcessor(configuration.output_radix())
with open(configuration.input_file(), "rt") as cluster:
    each_line = cluster.readline().strip()
    while each_line:
        if each_line.startswith(NR_PARTITIONS_ID):
            processor.set_nr_partitions(int(each_line.replace(NR_PARTITIONS_ID, "")))
        elif not each_line.startswith("//"):
            e = EdgeReader(each_line).translate()
            if e is not None:
                processor.handle_edge(e)
        each_line = cluster.readline()
processor.close_all()
