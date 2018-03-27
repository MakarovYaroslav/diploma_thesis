import sys
import os
import urllib.request
import zipfile
import shutil
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import main_functions

config = main_functions.get_config()
negative_train_file = config['tone_analyse']['negative_train_file']
positive_train_file = config['tone_analyse']['positive_train_file']
dataset_folder = config['tone_analyse']['dataset_folder_name']

dataset_url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00331/sentiment%20labelled%20sentences.zip"
os.mkdir('./%s/' % dataset_folder)
urllib.request.urlretrieve(dataset_url, "./%s/dataset.zip" % dataset_folder)

with zipfile.ZipFile("./%s/dataset.zip" % dataset_folder, "r") as zip_ref:
    zip_ref.extractall("./%s/" % dataset_folder)
data_path = './%s/sentiment labelled sentences/' % dataset_folder

os.remove('./%s/dataset.zip' % dataset_folder)
os.remove('%s/readme.txt' % data_path)
os.remove('%s/.DS_Store' % data_path)

with open('./%s/%s' % (dataset_folder, negative_train_file), 'w') as neg_file:
    with open('./%s/%s' % (dataset_folder, positive_train_file), 'w') as pos_file:
        for filename in os.listdir(data_path):
            with open(os.path.join(data_path, filename), 'r') as file:
                for line in file:
                    try:
                        text, attitude = line.split('\t')
                        if attitude == '0\n':
                            neg_file.write(text+'\n')
                        else:
                            pos_file.write(text+'\n')
                    except UnicodeDecodeError:
                        pass
folders = [item for item in os.listdir('./%s/' % dataset_folder)
           if os.path.isdir(os.path.join('./%s/' % dataset_folder, item))]
for folder in folders:
    shutil.rmtree('%s/%s/' % (dataset_folder, folder))
