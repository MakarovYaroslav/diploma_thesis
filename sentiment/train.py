import nltk
import math
import random
import pickle
import os
from nltk.tokenize import word_tokenize
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import main_functions

config = main_functions.get_config()
algos_folder = config['tone_analyse']['folder_for_algos']
negative_train_file = config['tone_analyse']['negative_train_file']
positive_train_file = config['tone_analyse']['positive_train_file']
dataset_folder = config['tone_analyse']['dataset_folder_name']

try:
    from sentiment.sentiment_mod import MainClassifier
except FileNotFoundError:
    os.mkdir(algos_folder)
    from sentiment.sentiment_mod import MainClassifier


def find_features(document):
    words = word_tokenize(document)
    features = {}
    for w in word_features:
        features[w] = (w in words)
    return features


# функция сохранения в файл
def save_to_file(filepath, open_mode, data):
    save_file = open(filepath, open_mode)
    pickle.dump(data, save_file)
    save_file.close()
    return


# функция обработки высказываний из файла
def statement_processing(file, tone, word_types):
    for p in file.split('\n'):
        documents.append((p, tone))
        words = word_tokenize(p)
        pos = nltk.pos_tag(words)
        for w in pos:
            if w[1][0] in word_types:
                all_words.append(w[0].lower())
    return


short_pos = open('./%s/%s' % (dataset_folder, positive_train_file), "r").read()
short_neg = open('./%s/%s' % (dataset_folder, negative_train_file), "r").read()


all_words = []
documents = []


#  J-прилагательное, R-наречие и V-глагол
allowed_word_types = ["J", "R", "V"]
# обрабатываем позитивные высказывания
statement_processing(short_pos, "pos", allowed_word_types)
# обрабатываем негативные высказывания
statement_processing(short_neg, "neg", allowed_word_types)


save_to_file('./%s/dociments.pickle' % algos_folder, "wb", documents)


all_words = nltk.FreqDist(all_words)


word_features_count = math.floor(len(all_words) / 2)
word_features = list(all_words.keys())[:word_features_count]

save_to_file('./%s/word_features5k.pickle' % algos_folder, "wb", word_features)


featuresets = [(find_features(rev), category) for (rev, category) in documents]
print(len(featuresets))

random.shuffle(featuresets)

test_count = math.floor(len(featuresets) / 3)
testing_set = featuresets[:test_count]
training_set = featuresets[test_count:]


MainClassifier.learn_all(training_set, testing_set)
