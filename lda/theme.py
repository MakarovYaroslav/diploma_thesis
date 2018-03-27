import lda.trainmodel as trainmodel
import argparse

LdaForTopicModeling = trainmodel.LdaModelClass()
LdaForTopicModeling.get_topic_names()


def get_post_topics(post):
    list_of_topics = LdaForTopicModeling.create_list_with_themes(post)
    return list_of_topics


def replace_posts_with_topics(posts):
    topics_with_tone = []
    for post in posts:
        topics_with_tone.append([get_post_topics(post), posts[post]])
    return topics_with_tone


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("text", help="Текст для тематического анализа")
    args = parser.parse_args()
    topics = get_post_topics(args.text)
    print("Текст для анализа: %s" % args.text)
    for topic, probability in topics:
        prob = probability * 100
        print('Принадлежит к теме "' + topic +
              '" с вероятностью ' + str(prob) + '%')
