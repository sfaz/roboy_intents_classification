# import rospy
import numpy as np
import os.path
import scipy.spatial.distance as sd
import skipthoughts
from nltk.stem.lancaster import LancasterStemmer
import nltk

neighbors = 1
stemmer = LancasterStemmer()
words = []
classes = []
documents = []
sentences = []
ignore_words = ['?', ',', 'roboy', 'Roboy', '\n', '.']


def read_intents():
    import os
    intents_path = os.getcwd() + "/intents/";
    training_data = []
    for filename in os.listdir(intents_path):
        with open(intents_path + filename) as f:
            for line in f:
                training_data.append({"class": filename, "sentence": line})

    return training_data


def sanitize_sentence(sentence):
    words = [stemmer.stem(w.lower()) for w in sentence if w not in ignore_words]
    sentence_new = "".join(str(x) for x in words)
    return sentence_new


def sanitize_dataset(training_data):
    # loop through each sentence in our training data
    for pattern in training_data:
        pattern['sentence'] = sanitize_sentence(pattern['sentence'])
        # add to our classes list
        if pattern['class'] not in classes:
            classes.append(pattern['class'])
    return classes


def get_nn(encoder, encodings, training_data, sentence):
    encoding = encoder.encode([sentence])
    encoding = encoding[0]
    scores = sd.cdist([encoding], encodings, "cosine")[0]
    sorted_ids = np.argsort(scores)
    print("Sentence : " + sentence)
    print("\nNearest neighbors:")
    for i in range(0, neighbors):
        print(" %d. %s (%.3f) %s" %
              (i + 1, sentences[sorted_ids[i]], scores[sorted_ids[i]], training_data[sorted_ids[i]]["class"]))
    return training_data[sorted_ids[i]]["class"], scores[sorted_ids[i]]


def init(sentence):
    training_data = read_intents()
    sanitize_dataset(training_data)
    for pattern in training_data:
        sentences.append(pattern['sentence'])
    model = skipthoughts.load_model()
    encoder = skipthoughts.Encoder(model)
    encodings = encoder.encode(sentences)
    sentence_sanitized = sanitize_sentence(sentence)
    intent = get_nn(encoder, encodings, training_data, sentence_sanitized)
    print(intent)


def main():
    sentence = "what year were you born"
    init(sentence)


if __name__ == '__main__':
    main()
