from gensim import corpora
from nltk.corpus import stopwords
from collections import defaultdict
import re
from nltk.stem.wordnet import WordNetLemmatizer
import wikipedia
import requests
import os
import random
import math
import argparse
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import main_functions


config = main_functions.get_config()
categories = config['topic_modeling']['categories']
uci_folder_name = config['topic_modeling']['uci_folder_name']
corpus_name = config['topic_modeling']['corpus_name']

stop = set(stopwords.words('english'))
lmtzr = WordNetLemmatizer()


class Text:
    def __init__(self):
        pass

    @staticmethod
    def is_word_correct(word):
        if not word.isdigit():
            if word not in stop:
                if len(word) > 2:
                    return True
        return False

    @staticmethod
    def capitalize_first_letter(string):
        if string:
            return string[0].upper() + string[1:]
        return string

    @staticmethod
    def text_cleaning(text_for_clean):
        start = text_for_clean.rfind('http')
        if start != -1:
            end = text_for_clean.rfind('\n')
            if end != -1:
                text_for_clean = text_for_clean[:start] + text_for_clean[end:]
        text = re.sub(r'\([^\)]+\)', '', text_for_clean)
        text = re.sub(r'[^a-zA-Z]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.lstrip()
        text = text.rstrip()
        return text.lower()


class WikiText(Text):
    def __init__(self, list_of_categories, max_files_count_for_saving=45):
        super().__init__()
        self.max_files_count_for_saving = max_files_count_for_saving
        self.list_of_categories = list_of_categories
        self.uci_folder = uci_folder_name

    def get_textfiles_from_wiki(self):
        for category in self.list_of_categories:
            parameters = {'action': 'query', 'list': 'categorymembers',
                          'cmtitle': 'Category:' + category, 'format': 'json',
                          'cmlimit': self.max_files_count_for_saving}
            r = requests.get(
                'https://en.wikipedia.org/w/api.php', params=parameters)
            returned_data = r.json()['query']['categorymembers']
            themes = []
            for article in returned_data:
                if int(article['ns']) == 0:
                    themes.append([article['title'], article['pageid']])
            category_path = os.path.join(self.uci_folder, category)
            if not os.path.exists(category_path):
                os.makedirs('./%s' % category_path)
            for theme, pageid in themes:
                try:
                    page = wikipedia.page(pageid=pageid)
                    with open('./%s/%s.wiki.txt' % (category_path, theme), 'w') as file:
                        file.write(page.content)
                except AttributeError:
                    pass
        return

    def save_test_files(self, files_for_test, category):
        documents_for_test = []
        category_path = os.path.join(self.uci_folder, category)
        for file_name in files_for_test:
            with open('./%s/%s' % (category_path, file_name), 'r') as file:
                for line in file.readlines():
                    documents_for_test.append(line)
        texts_for_test = ' '.join(documents_for_test)
        with open('./%s/%s.test.txt' % (category_path, category), 'w') as file:
            file.write(texts_for_test)
        return

    @staticmethod
    def get_main_article(category):
        article = []
        for word in category.lower().split():
            article.append(lmtzr.lemmatize(word))
        main_article = ' '.join(article)
        return Text.capitalize_first_letter(main_article)

    def save_corpus_from_textfiles(self):
        documents = []
        for category in self.list_of_categories:
            category_path = os.path.join(self.uci_folder, category)
            main_article = '%s.wiki.txt' % self.get_main_article(category)
            files = os.listdir('./%s/' % category_path)
            files.remove(main_article)
            count_of_testfiles = math.floor(len(files) / 3)
            random.shuffle(files)
            testfiles = files[:count_of_testfiles]
            self.save_test_files(testfiles, category)
            trainfiles = files[count_of_testfiles:]
            trainfiles.append(main_article)
            for file_name in trainfiles:
                with open('./%s/%s' % (category_path, file_name), 'r') as file:
                    for line in file.readlines():
                        documents.append(line)
        texts = [[lmtzr.lemmatize(word) for word in re.findall('\w+', document.lower()) if self.is_word_correct(word)]
                 for document in documents]
        frequency = defaultdict(int)
        for text in texts:
            for token in text:
                frequency[token] += 1
        texts = [[token for token in text if frequency[token] > 3]
                 for text in texts]
        dictionary = corpora.Dictionary(texts)
        dictionary.save_as_text('./%s/%s.dict' % (self.uci_folder, corpus_name))
        corpus = [dictionary.doc2bow(text) for text in texts]
        corpora.UciCorpus.save_corpus(
            './%s/%s.txt' % (self.uci_folder, corpus_name), corpus, id2word=dictionary)
        return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--max", help="Максимальное количество "
                        "файлов для сохранения к каждой теме")
    args = parser.parse_args()
    if args.max:
        wiki = WikiText(categories, args.max)
    else:
        wiki = WikiText(categories)
    try:
        wiki.get_textfiles_from_wiki()
        wiki.save_corpus_from_textfiles()
        print('UCI корпус для обучения успешно скачан!\n Для обучения LDA модели -'
              ' используйте команду "python3 lda/trainmodel.py --count COUNT"')
    except FileExistsError:
        print("Корпус уже был скачан!")

