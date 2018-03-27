from gensim import corpora, models
from collections import Counter
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import main_functions
import argparse
from lda.createuci import WikiText

WORD_COUNT_FOR_PRINT = 10

config = main_functions.get_config()
categories = config['topic_modeling']['categories']
uci_folder_name = config['topic_modeling']['uci_folder_name']
ldamodel_name = config['topic_modeling']['ldamodel_name']
corpus_name = config['topic_modeling']['corpus_name']


class LdaModelClass:
    def __init__(self):
        self.name = ldamodel_name
        self.categories = categories
        self.corpus_name = corpus_name
        self.uci_folder_name = uci_folder_name
        self.topics_count = len(self.categories)
        try:
            self.ldamodel = models.ldamodel.LdaModel.load('./%s/%s' % (self.uci_folder_name, self.name))
        except FileNotFoundError:
            self.ldamodel = None
        try:
            self.dictionary = corpora.Dictionary.load_from_text(
                './%s/%s.dict' % (self.uci_folder_name, self.corpus_name))
        except FileNotFoundError:
            print('UCI корпус для обучения не найден!\nЧтобы скачать его'
                  ' используйте комманду "python3 lda/createuci.py --max MAX"')
            exit(0)

    # Импортируем данные в формате UCI Bag of words
    def import_uci(self):
        self.data = corpora.UciCorpus(
            './%s/%s.txt' % (self.uci_folder_name, self.corpus_name),
            './%s/%s.txt.vocab' % (self.uci_folder_name, self.corpus_name))

    def train_model(self, passes_count=10):
        ldamodel = models.ldamodel.LdaModel(
            self.data, id2word=self.dictionary, num_topics=self.topics_count,
            passes=passes_count, alpha='auto', eta='auto')
        ldamodel.save('./%s/%s' % (self.uci_folder_name, self.name))
        print("Модель успешно обучена!")
        self.ldamodel = models.ldamodel.LdaModel.load('./%s/%s' % (self.uci_folder_name, self.name))
        return

    def print_model_topics(self):
        for topic, top_words in self.ldamodel.print_topics(
                num_topics=self.topics_count, num_words=WORD_COUNT_FOR_PRINT):
            print("Topic", self.topic_names[topic], ":", top_words)
        return

    def bayes_get_topic_names(self):
        pass

    def get_topic_names(self):
        wordcount_in_category = {}
        for category in self.categories:
            with open('./%s/%s/%s.wiki.txt' % (self.uci_folder_name, category, WikiText.get_main_article(category)), 'r') as f:
                wordcount = Counter(f.read().split())
                wordcount_in_category[category] = wordcount
        topic_names = []
        for top_words in self.ldamodel.print_topics(
                num_topics=self.topics_count, num_words=10):
            words_from_top = []
            for word in top_words[1].split('+'):
                words_from_top.append(word.split('*')[1].replace(" ", ''))
            topics = []
            for category in self.categories:
                word_count = 0
                for word in words_from_top:
                    word_count += wordcount_in_category[category][word]
                topics.append([category, word_count])
            real_topic = max(topics, key=lambda x: x[1])[0]
            topic_names.append(real_topic)
        self.topic_names = topic_names

    def create_list_with_themes(self, sentence):
        bows = self.dictionary.doc2bow(sentence.lower().split())
        topics = self.ldamodel.get_document_topics(bows)
        topics = [list(topic) for topic in topics]
        for topic in topics:
            topic[0] = self.topic_names[topic[0]]
        return topics

    def test_model(self):
        probabilities = 0.0
        for category in self.categories:
            with open('./%s/%s/%s.test.txt' % (self.uci_folder_name, category, category), 'r') as file:
                list_of_topics = self.create_list_with_themes(file.read())
            for topic_name, probability in list_of_topics:
                if topic_name == category:
                    probabilities += float(probability)
        accuracy = (probabilities / len(self.categories)) * 100
        print("Точность модели  = " + str(accuracy))
        return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", help="Количество проходов при обучении")
    args = parser.parse_args()
    LdaForTrain = LdaModelClass()
    LdaForTrain.import_uci()
    if args.count:
        LdaForTrain.train_model(int(args.count))
    else:
        LdaForTrain.train_model()
    LdaForTrain.get_topic_names()
    #LdaForTrain.bayes_get_topic_names()
    LdaForTrain.print_model_topics()
    LdaForTrain.test_model()
