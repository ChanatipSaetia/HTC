import os
import pickle

import numpy as np
from scipy.sparse import csr_matrix
from torch import FloatTensor

import data.hierarchy as hie
import data.preparation as prep
from data.exception import NotEmbeddingState


class Dataset():

    def __init__(self, data_name, fold_number=1, mode="train", state="first", sequence=False):
        self.data_name = data_name
        self.fold_number = fold_number
        self.mode = mode
        self.data_type = "index"
        self.state = state
        self.sequence = sequence
        self.load_hierarchy()
        self.load_datas()
        # sparse data

    def load_hierarchy(self):
        if not os.path.isfile("data/%s/hierarchy.pickle" % self.data_name):
            hierarchy, parent_of, all_name, name_to_index, level = hie.reindex_hierarchy(
                '%s/hierarchy.txt' % self.data_name)
            hie.save_hierarchy("%s/hierarchy.pickle" % self.data_name, hierarchy,
                               parent_of, all_name, name_to_index, level)
        self.hierarchy, self.parent_of, self.all_name, self.name_to_index, self.level = hie.load_hierarchy(
            "%s/hierarchy.pickle" % self.data_name)

    def load_datas(self):
        if self.state == 'embedding':
            with open('data/%s/doc2vec/data.%s.pickle' % (self.data_name, self.mode), mode='rb') as f:
                self.datas, self.labels = pickle.load(f)
            return
        if not os.path.isfile("data/%s/fold/data_%d.pickle.%s" %
                              (self.data_name, self.fold_number, self.mode)):
            file_name = "%s/data.txt" % (self.data_name)
            datas, labels = prep.import_data(file_name, sequence=self.sequence)
            hierarchy_file_name = "%s/hierarchy.pickle" % self.data_name
            new_labels = prep.map_index_of_label(
                hierarchy_file_name, labels)
            prep.split_data(datas, new_labels, self.data_name)
        self.datas, self.labels = prep.load_data_in_pickle(
            "%s/fold/data_%d.pickle.%s" % (self.data_name, self.fold_number, self.mode))

    def number_of_level(self):
        return len(self.level) - 1

    def number_of_classes(self):
        return len(self.all_name)

    def check_each_number_of_class(self, level):
        return int(self.level[level + 1] - self.level[level])

    def change_to_Doc2Vec(self, doc2vec):
        self.datas = doc2vec.transform(self.datas)

        indice = [j for i in self.labels for j in i]
        indptr = np.cumsum([0] + [len(i) for i in self.labels])
        data_one = np.ones(len(indice))
        self.state = "embedding"
        self.labels = csr_matrix((data_one, indice, indptr),
                                 shape=(len(self.labels), len(self.all_name))).tocsc()
        if not os.path.exists('data/%s/doc2vec/' % self.data_name):
            os.makedirs('data/%s/doc2vec/' % self.data_name)
        with open('data/%s/doc2vec/data.%s.pickle' % (self.data_name, self.mode), mode='wb') as f:
            pickle.dump([self.datas, self.labels], f)

    def generate_batch(self, level, batch_size):
        if self.state != "embedding":
            raise NotEmbeddingState
        number = len(self.datas)
        index = np.arange(0, number, batch_size).tolist()
        index.append(number)
        if level == -1:
            label_level = self.labels.tocsr()
        else:
            label_level = self.labels[:, self.level[level]                                      :self.level[level + 1]].tocsr()
        for i in range(len(index) - 1):
            start, end = [index[i], index[i + 1]]
            batch_datas = FloatTensor(self.datas[start:end])
            batch_labels = FloatTensor(label_level[start:end].toarray())
            yield batch_datas, batch_labels

    def number_of_data_in_each_class(self):
        if self.state != "embedding":
            raise NotEmbeddingState
        return np.sum(self.labels, 0).astype(int).tolist()[0]

    def number_of_data(self):
        return len(self.datas)

    def index_of_level(self, level):
        return self.level[level], self.level[level + 1]

    def size_of_feature(self):
        return self.datas.shape[1]
