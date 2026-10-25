"""
Construct CP graph structure

Nodes are bit strings of length 0 through dpth n:
- "": root
- "0": left child of root
- "1": right child of root
- ....
- "000"..."111" : leaves when depth=3

graph includes:
- complete binary tree, with edges directed from children rowards their parents
- additional CP edges from left siblings to leaves along path to root
"""

from collections import defaultdict, deque
from itertools import product
from heapq import heappop, heappush


def generate_graph(depth):
    # include error handling

    # create nodes from root to leaves
    nodes = {""}
    for level in range(1, depth + 1):
        nodes.update(
            "".join(bits) for bits in product("01", repeat=level)
        )

    edges = set()

    # add edges from children to parents
    for node in nodes:
        if node:  # skip root
            parent = node[:-1]
            edges.add((node, parent))


    # add additional edges from each left child to every leaf in its parent's right subtree in root path
    # - every prefix p with len(p) <n 
    # - connect root of its left subtree p+"0" to every leaf in its right subtree p+"1"
    for prefix_length in range(depth):
        # generate every possible internal-node prefix of this length
        for bits in product("01", repeat=prefix_length):
            prefix = "".join(bits)

            # roots of left and right subtrees
            left_subtree_root = prefix + "0"
            right_subtree_root = prefix + "1"

            # find all leaves in the right subtree
            remaining = depth - len(right_subtree_root)

            # generate all leaves in the right subtree
            for suffix in product("01", repeat=remaining):
                leaf = right_subtree_root + "".join(suffix)

                # add directed CP edge
                edges.add((left_subtree_root, leaf))

    
    # construct graph representation
    graph = {
        'nodes': nodes,
        'edges': edges,
        'depth': depth,
        'N': len(nodes)
    }

    # validate graph structure -> graph should be acyclic
    topological_order(graph)

    return graph


def get_predecessors(graph, node):
    # return incoming neighbors of node, in deterministic order
    # these are the labels that must be available before computing this node's label
    if node not in graph['nodes']:
        raise ValueError(f"Node {node} not in graph.")

    # select all sources of edges whose target is the requested node
    # sorting makes output deterministic
    return sorted(
        source for source, target in graph['edges'] if target == node
    )


def topological_order(graph):
    """
    return deterministic topological ordering:
    every source of an edge appears before its target
    Kahn' algorithm applied:
    1. calculate indegree (= number of incoming edges for each node) of every node (indegree 0 means lowest level = leaves)
    2. place all zero-indegree nodes in priority queue (leaves are prioritized)
    3. repeatedly remove smallest available node
    4. decrease indegree of its successors (outgoing neighbors)
    5. add successors whose indegree becomes zero

    """
    nodes=graph['nodes']
    edges=graph['edges']

    indegree={node: 0 for node in nodes}
    successors = defaultdict(list)

    # build indegree and successor information
    for source, target in edges:
        indegree[target] += 1
        successors[source].append(target)

    # priority queue of nodes with no incoming edges
    ready = []

    for node in nodes:
        if indegree[node] == 0:
            heappush(ready, (len(node), node))

    order = []

    # process nodes in topological order
    while ready:

        # remove highest-priorit available node
        _, node = heappop(ready)
        order.append(node)

        # decrease indegree of each successor
        for target in sorted(successors[node]):
            indegree[target] -= 1
            if indegree[target] == 0:
                heappush(ready, (len(target), target))

    # if some nodes remain unprocessed, a directed cycle exists != acyclic
    if len(order) != len(nodes):
        raise ValueError("Graph has at least one cycle; topological order not possible.")

    return order
    

def get_root(graph):
    return ""  # root is always the empty string

def get_leaves(graph):
    n=graph['depth']
    return sorted(node for node in graph['nodes'] if len(node) == n)

def get_leftmost(graph):
    n = graph['depth']
    return '0' * n  # leftmost leaf is all zeros

def print_graph(graph):
    print(f"Graph with depth {graph['depth']}, {graph['N']} nodes, and {len(graph['edges'])} edges:")

    print("\nNodes:")
    for level in range(graph['depth'] + 1):
        nodes_at_level = sorted((node for node in graph['nodes'] if len(node) == level),
                                key=lambda node: node,)
        print (f"Level {level}: {nodes_at_level}")

    print("\nEdges (source -> target):")
    for source, target in sorted(
        graph['edges'], 
        key=lambda edge: (len(edge[0]), edge[0], len(edge[1]), edge[1]),):
        print(f"  {source!r} -> {target!r}")

    print("\nPredecessors:")
    for node in sorted(graph['nodes'], key=lambda node: (len(node), node),):
        preds = get_predecessors(graph, node)
        print(f"  {node!r}: {preds}")


if __name__ == "__main__":
    depth = 4
    graph = generate_graph(depth)
    print_graph(graph)

    print("\nTopological Order:")
    print(topological_order(graph))
