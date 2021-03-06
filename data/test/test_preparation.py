import unittest

import numpy as np

import data.exception as ex
import data.preparation as preparation


class PreparationUnitTest(unittest.TestCase):

    def test_import_each_row(self):
        test_string = []
        result_data = []
        result_label = []
        # single feature
        test_string.append("5:[2]")
        result_data.append(['2'])
        result_label.append(['5'])
        # multi feature
        test_string.append("5:[2,4]")
        result_data.append(['2', '4'])
        result_label.append(['5'])
        # multi label
        test_string.append("5,2:[2]")
        result_data.append(['2'])
        result_label.append(['2', '5'])
        # multi feature and label
        test_string.append("5,2:[2,4]")
        result_data.append(['2', '4'])
        result_label.append(['2', '5'])
        for input_string, output_data, output_label in zip(test_string, result_data, result_label):
            data, label = preparation.import_each_row(input_string)
            self.assertEqual(data, output_data)
            self.assertEqual(label, output_label)
        # no feature
        with self.assertRaises(ex.NoFeatureInRow):
            preparation.import_each_row("5:[]")
        # no label
        with self.assertRaises(ex.NoLabelInRow):
            preparation.import_each_row(":[2]")

    def test_import_each_row_bag_of_word(self):
        test_string = []
        result_data = []
        result_label = []
        # single feature
        test_string.append("5 2:2")
        result_data.append(['2', '2'])
        result_label.append(['5'])
        # multi feature
        test_string.append("5 2:1 4:1")
        result_data.append(['2', '4'])
        result_label.append(['5'])
        # multi label
        test_string.append("5, 2 2:1")
        result_data.append(['2'])
        result_label.append(['2', '5'])
        # multi feature and label
        test_string.append("5, 2 2:1 4:1")
        result_data.append(['2', '4'])
        result_label.append(['2', '5'])
        for input_string, output_data, output_label in zip(test_string, result_data, result_label):
            data, label = preparation.import_each_row_bag_of_word(input_string)
            self.assertEqual(data, output_data)
            self.assertEqual(label, output_label)
        # no feature
        with self.assertRaises(ex.NoFeatureInRow):
            preparation.import_each_row_bag_of_word("5")
        with self.assertRaises(ex.NoFeatureInRow):
            preparation.import_each_row_bag_of_word("5, 3")
        # no label
        with self.assertRaises(ex.NoLabelInRow):
            preparation.import_each_row_bag_of_word("2:1")
        with self.assertRaises(ex.NoLabelInRow):
            preparation.import_each_row_bag_of_word("2:1 4:1")

    def test_import_data_seq(self):
        file_name = "test/data.txt"
        real_data = [['1'], ['2', '3'], ['1', '6'], ['4', '1'], ['5', '2']]
        real_label = [['3'], ['4', '8'], ['5', '6'], ['1', '2'], ['7']]
        datas, labels = preparation.import_data_sequence(file_name)
        self.assertEqual(datas, real_data)
        self.assertEqual(labels, real_label)

    def test_import_data_bag(self):
        file_name = "test/test_data_bag_of_word.txt"
        real_data = [['8', '18', '18'], ['2', '33', '33']]
        real_label = [['32', '545'], ['11']]
        datas, labels = preparation.import_data_bag_of_word(file_name)
        self.assertEqual(datas, real_data)
        self.assertEqual(labels, real_label)

    def test_import_data(self):
        file_name = "test/data.txt"
        real_data = [['1'], ['2', '3'], ['1', '6'], ['4', '1'], ['5', '2']]
        real_label = [['3'], ['4', '8'], ['5', '6'], ['1', '2'], ['7']]
        datas, labels = preparation.import_data(file_name)
        self.assertEqual(datas, real_data)
        self.assertEqual(labels, real_label)

        file_name = "test/test_data_bag_of_word.txt"
        real_data = [['8', '18', '18'], ['2', '33', '33']]
        real_label = [['32', '545'], ['11']]
        datas, labels = preparation.import_data(
            file_name, sequence=False)
        self.assertEqual(datas, real_data)
        self.assertEqual(labels, real_label)

    def test_load_save_pickle(self):
        file_name = "test/test_data_bag_of_word.txt"
        datas, labels = preparation.import_data(
            file_name, sequence=False)
        preparation.save_data_in_pickle(
            "test/pickle/test.pickle", datas, labels)
        real_data, real_label = preparation.load_data_in_pickle(
            "test/pickle/test.pickle")
        self.assertEqual(datas, real_data)
        self.assertEqual(labels, real_label)

    def test_map_index(self):
        file_name = "test/data.txt"
        _, labels = preparation.import_data(file_name)
        hierarchy_file_name = "test/hierarchy.pickle"
        new_labels = preparation.map_index_of_label(
            hierarchy_file_name, labels)
        real_new_labels = [
            set([0, 2]),
            set(range(8)),
            set(range(6)),
            set([0, 1]),
            set(range(7))
        ]
        self.assertListEqual(real_new_labels, new_labels)

    def test_split_data(self):
        file_name = "test/data.txt"
        datas, labels = preparation.import_data(file_name)
        hierarchy_file_name = "test/hierarchy.pickle"
        new_labels = preparation.map_index_of_label(
            hierarchy_file_name, labels)
        data_name = "test"
        preparation.split_fold_data(datas, new_labels, data_name)
        for i in range(5):
            name = "test/fold/data_%d.pickle.%s" % (i + 1, "train")
            train, train_label = preparation.load_data_in_pickle(name)
            name = "test/fold/data_%d.pickle.%s" % (i + 1, "validate")
            validate, validate_label = preparation.load_data_in_pickle(name)
            name = "test/fold/data_%d.pickle.%s" % (i + 1, "test")
            test, test_label = preparation.load_data_in_pickle(name)
            fold_datas = np.concatenate([train, validate, test])
            fold_labels = np.concatenate(
                [train_label, validate_label, test_label])
            self.assertListEqual(sorted(fold_datas.tolist()), sorted(datas))
            a = sorted(map(list, fold_labels.tolist()))
            b = sorted(map(list, new_labels))
            self.assertListEqual(a, b)

    def test_create_map_data_index(self):
        labels = [[1, 2], [1, 4], [3, 5], [1], [1], [1]]
        real_map = {1: [0, 1, 3, 4, 5],
                    2: [0],
                    3: [2],
                    4: [1],
                    5: [2]}
        map_index = preparation.create_map_data_index(labels)
        self.assertDictEqual(real_map, map_index)

    def test_create_train_validate_index(self):
        labels = [[1, 2], [1, 4], [3, 5], [1], [1], [1]]
        real_cutoff = [0, 2, 3, 4, 5, 6, 7]
        real_train = {0, 1, 3, 4}
        real_validate = {5}
        hierarchy_file_name = "test/hierarchy.pickle"
        train, validate, cutoff = preparation.create_train_validate_index(
            labels, hierarchy_file_name)
        self.assertSetEqual(real_train, train)
        self.assertSetEqual(real_validate, validate)
        self.assertListEqual(real_cutoff, cutoff)

        real_train = {0, 1, 3, 4}
        real_validate = {0, 1, 2, 5}
        real_cutoff = [0, 6, 7]
        train, validate, cutoff = preparation.create_train_validate_index(
            labels, hierarchy_file_name, least_data=1)
        self.assertSetEqual(real_train, train)
        self.assertSetEqual(real_validate, validate)
        self.assertListEqual(real_cutoff, cutoff)

    def test_remap_data(self):
        data = [[1], [2], [3], [4], [5]]
        labels = [set([1]), set([2]), set([3]), set([4]), set([1, 3])]
        remap = {1: 0, 2: 1}
        data, labels = preparation.remap_data(data, labels, remap)
        real_datas = [[1], [2], [5]]
        real_labels = [set([0]), set([1]), set([0])]
        self.assertListEqual(real_datas, data.tolist())
        self.assertListEqual(real_labels, labels.tolist())
