############################################################################
# Copyright ESIEE Paris (2018)                                             #
#                                                                          #
# Contributor(s) : Benjamin Perret                                         #
#                                                                          #
# Distributed under the terms of the CECILL-B License.                     #
#                                                                          #
# The full license is in the file LICENSE, distributed with this software. #
############################################################################

import unittest
import numpy as np
import higra as hg


class TestWatershedHierarchy(unittest.TestCase):

    def test_watershed_hierarchy_by_attribute(self):
        g = hg.get_4_adjacency_graph((1, 19))
        edge_weights = np.asarray((0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 2, 0, 0))
        # watershed hierarchy by area...
        t, altitudes = hg.watershed_hierarchy_by_attribute(edge_weights, lambda tree, _: hg.attribute_area(tree), g)

        ref_parents = np.asarray((
            19, 19, 20, 20, 20, 21, 21, 21, 21, 21, 21, 22, 22, 22, 22, 22, 23, 23, 23, 24, 24, 25,
            26, 26, 25, 27, 27, 27), dtype=np.int64)
        ref_tree = hg.Tree(ref_parents)
        ref_altitudes = np.asarray((0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 3, 3, 5))

        self.assertTrue(hg.test_tree_isomorphism(t, ref_tree))
        self.assertTrue(np.allclose(altitudes, ref_altitudes))

    def test_watershed_hierarchy_by_minima_ordering(self):
        g = hg.get_4_adjacency_graph((1, 7))
        edge_weights = np.asarray((1, 4, 1, 0, 10, 8))
        # same as dynamics
        minima_ranking = np.asarray((2, 2, 0, 3, 3, 1, 1), dtype=np.uint64)
        minima_altitudes = np.asarray((0, 2, 3, 10), dtype=np.float64)

        t, altitudes = hg.watershed_hierarchy_by_minima_ordering(edge_weights, minima_ranking, minima_altitudes, g)

        ref_parents = np.asarray((7, 7, 8, 8, 8, 9, 9, 11, 10, 10, 11, 11))
        ref_tree = hg.Tree(ref_parents)
        ref_altitudes = np.asarray((0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 3))

        self.assertTrue(hg.test_tree_isomorphism(t, ref_tree))
        self.assertTrue(np.allclose(altitudes, ref_altitudes))


if __name__ == '__main__':
    unittest.main()
