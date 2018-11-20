############################################################################
# Copyright ESIEE Paris (2018)                                             #
#                                                                          #
# Contributor(s) : Benjamin Perret                                         #
#                                                                          #
# Distributed under the terms of the CECILL-B License.                     #
#                                                                          #
# The full license is in the file LICENSE, distributed with this software. #
############################################################################

import higra as hg


@hg.argument_helper(hg.CptVertexLabeledGraph)
def make_region_adjacency_graph_from_labelisation(vertex_labels, graph):
    """
    Create a region adjacency graph (rag) of a vertex labelled graph.
    Each maximal connected set of vertices having the same label is a region.
    Each region is represented by a vertex in the rag.
    There is an edge between two regions of labels l1 and l2 in the rag iff there exists an edge linking 2
    vertices of labels l1 and l2 int he original graph.

    The returned rag is equipped with three attributes:

    * vertex_map: an array of size graph.num_vertices() which indicates for each vertex v of the graph
    the index of the vertex of the rag that represents the region containing v;
    * edge_map: an array of size graph.num_edges() which indicates for each edge e of the graph
    the index of the edge of the rag that links the two regions containing the extremities of e. If no such edge exists
    (if both extremities of e are in the same region), the value -1 is used.
    * original_graph: the graph from which this rag has been computed

    :param graph:
    :param vertex_labels:
    :return:
    """
    vertex_labels = hg.linearize_vertex_weights(vertex_labels, graph)

    rag, vertex_map, edge_map = hg._make_region_adjacency_graph_from_labelisation(graph, vertex_labels)

    hg.CptRegionAdjacencyGraph.link(rag, graph, vertex_map, edge_map)

    return rag


@hg.argument_helper(hg.CptGraphCut)
def make_region_adjacency_graph_from_graph_cut(edge_weights, graph):
    """
    Create a region adjacency graph (rag) from a graph cut.
    Two vertices v1, v2 are in the same region if there exists a v1v2-path composed of edges weighted 0.
    Each region is represented by a vertex in the rag.
    There is an edge between two regions of labels l1 and l2 in the rag iff there exists an edge linking 2
    vertices of labels l1 and l2 int he original graph.

    The returned rag is equipped with three attributes:

    * vertex_map: an array of size graph.num_vertices() which indicates for each vertex v of the graph
    the index of the vertex of the rag that represents the region containing v;
    * edge_map: an array of size graph.num_edges() which indicates for each edge e of the graph
    the index of the edge of the rag that links the two regions containing the extremities of e. If no such edge exists
    (if both extremities of e are in the same region), the value -1 is used.
    * original_graph: the graph from which this rag has been computed

    :param graph:
    :param edge_weights:
    :return:
    """
    rag, vertex_map, edge_map = hg._make_region_adjacency_graph_from_graph_cut(graph, edge_weights)

    hg.CptRegionAdjacencyGraph.link(rag, graph, vertex_map, edge_map)

    return rag


@hg.argument_helper(hg.CptVertexWeightedGraph)
def rag_back_project_vertex_weights(vertex_weights, graph):
    """
    Projects rag vertex weights onto original graph vertices.
    The result is an array weighting the vertices of the original graph of the rag such that:
    for any vertex v of the original graph, its weight is equal to the weight of the vertex of the rag that represents
    the region that contains v.

    For any vertex index i,
    result[i] = rag_vertex_weight[rag_vertex_map[i]]

    :param graph:
    :param vertex_weights:
    :return:
    """

    rag = hg.CptRegionAdjacencyGraph.construct(graph)

    new_weights = hg._rag_back_project_weights(rag["vertex_map"], vertex_weights)

    new_weights = hg.delinearize_vertex_weights(new_weights, rag["pre_graph"])
    hg.CptVertexWeightedGraph.link(new_weights, rag["pre_graph"])

    return new_weights


@hg.argument_helper(hg.CptEdgeWeightedGraph)
def rag_back_project_edge_weights(edge_weights, graph):
    """
    Projects rag edge weights onto original graph edges.
    The result is an array weighting the edges of the original graph of the rag such that:
    for any edge e of the original graph, its weight is equal to the weight of the edge of the rag that represents
    that links the two regions containing the extremities of e. If no such edge exists (if the extremities of e are
    in the same region), its value is 0.

    For any edge index ei,
    result[ei] = rag_edge_weight[rag_edge_map[ei]] if rag_edge_map[ei] != -1 and 0 otherwise

    :param graph:
    :param edge_weights:
    :return:
    """

    rag = hg.CptRegionAdjacencyGraph.construct(graph)

    new_weights = hg._rag_back_project_weights(rag["edge_map"], edge_weights)

    hg.CptEdgeWeightedGraph.link(new_weights, rag["pre_graph"])

    return new_weights


@hg.argument_helper(hg.CptRegionAdjacencyGraph)
def rag_accumulate_on_vertices(rag, accumulator, vertex_weights):
    """
    Computes rag vertex weights by accumulating values from the vertex weights of the original graph.

    For any vertex index i of the rag,
    result[i] = accumulate({vertex_weights[j] | rag_vertex_map[j] == i})

    :param rag:
    :param vertex_weights:
    :param accumulator:
    :return:
    """

    detail = hg.CptRegionAdjacencyGraph.construct(rag)
    vertex_weights = hg.linearize_vertex_weights(vertex_weights, detail["pre_graph"])

    new_weights = hg._rag_accumulate(detail["vertex_map"], vertex_weights, accumulator)

    hg.CptVertexWeightedGraph.link(new_weights, rag)

    return new_weights


@hg.argument_helper(hg.CptRegionAdjacencyGraph)
def rag_accumulate_on_edges(rag, accumulator, edge_weights):
    """
    Computes rag edge weights by accumulating values from the edge weights of the original graph.

    For any edge index i of the rag,
    result[i] = accumulate({vertex_weights[j] | rag_vertex_map[j] == i})

    :param rag:
    :param edge_weights:
    :param accumulator:
    :return:
    """

    detail = hg.CptRegionAdjacencyGraph.construct(rag)

    new_weights = hg._rag_accumulate(detail["edge_map"], edge_weights, accumulator)

    hg.CptEdgeWeightedGraph.link(new_weights, rag)

    return new_weights