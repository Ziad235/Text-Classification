import re
import sys
import math
import copy
from decimal import Decimal

filename = sys.argv[1]
stopWordsFile = "stopwords.txt"
numTraining = int(sys.argv[2])
epsilon = 0.1

def Categories_count(givenSet):

    categories = {}
    for i in givenSet:
        if i[1] not in categories:
            categories[i[1]] = 1
        else:
            categories[i[1]] = categories[i[1]] + 1

    Text_Corpus_Words = copy.deepcopy(categories)
    for i in Text_Corpus_Words:
        Text_Corpus_Words[i] = {}

    for biography in givenSet:
        for word in biography[2]:
            if word not in Text_Corpus_Words[biography[1]]:
                Text_Corpus_Words[biography[1]][word] = 1
            else:
                Text_Corpus_Words[biography[1]
                                  ][word] = Text_Corpus_Words[biography[1]][word] + 1
    return categories, Text_Corpus_Words


def Frequency_category(categories, Training_Set):
    freq = copy.deepcopy(categories)
    for i in freq:
        freq[i] = categories[i]/len(Training_Set)
    return freq


def Frequency_word(Text_Corpus_Words, categories):
    freq = copy.deepcopy(Text_Corpus_Words)
    allWords = {}
    for i in Text_Corpus_Words:
        for word in Text_Corpus_Words[i]:
            allWords[word] = 0
    for cat in freq:
        for word in Text_Corpus_Words[cat]:
            freq[cat][word] = Text_Corpus_Words[cat][word]/categories[cat]
        for word in allWords:
            if word not in freq[cat]:
                freq[cat][word] = 0
    return freq


def LapCorrectionWord(Frequency_word, epsilon):
    for i in Frequency_word:
        for word in Frequency_word[i]:
            Frequency_word[i][word] = (
                Frequency_word[i][word]+epsilon)/(1+2*epsilon)
    return Frequency_word


def LapCorrectionCategory(Frequency_category, epsilon):
    for i in Frequency_category:
        Frequency_category[i] = (
            Frequency_category[i]+epsilon)/(1+len(Frequency_category)*epsilon)
    return Frequency_category


def negLogWord(Frequency_word):
    for i in Frequency_word:
        for word in Frequency_word[i]:
            Frequency_word[i][word] = math.log(Frequency_word[i][word], 2)*(-1)
    return Frequency_word


def negLogCat(Frequency_category):
    for i in Frequency_category:
        Frequency_category[i] = math.log(Frequency_category[i], 2)*(-1)
    return Frequency_category


def trainingFunc(Training_Set, StopWords, epsilon):
    catFreqv, wordFreqv = {}, {}

    for i in range(len(Training_Set)):
        wordList = Training_Set[i][2].split()
        newWordList = {}
        for j in wordList:
            j = j.rstrip(',. ')
            if j not in StopWords and len(j) > 2:
                newWordList[j] = 1
        Training_Set[i][2] = newWordList

    categories, Text_Corpus_Words = Categories_count(Training_Set)
    catFreqv = Frequency_category(categories, Training_Set)
    catFreqv = LapCorrectionCategory(catFreqv, epsilon)
    catFreqv = negLogCat(catFreqv)
    wordFreqv = Frequency_word(Text_Corpus_Words, categories)
    wordFreqv = LapCorrectionWord(wordFreqv, epsilon)
    wordFreqv = negLogWord(wordFreqv)
    return catFreqv, wordFreqv


def testingFunc(tesSet, Frequency_category, Frequency_word):

    Predictions = {}

    probAll = {}

    for bio in Testing_Set:
        cats = {}
        for cat in Frequency_category:
            cats[cat] = Frequency_category[cat]
            for word in bio[2]:
                cats[cat] = cats[cat] + Frequency_word[cat][word]

        minKey = min(cats, key=cats.get)
        minVal = cats[min(cats, key=cats.get)]

        Predictions[bio[0]] = [minKey, minVal]

        x = {}
        s = 0
        for i in cats:
            if cats[i]-minVal < 7:
                x[i] = 2**(minVal-cats[i])
            else:
                x[i] = 0
            s += x[i]

        Probabilities = {}
        for i in cats:
            Probabilities[i] = round(x[i]/s, 2)

        probAll[bio[0]] = Probabilities

    return Predictions, probAll


Training_Set = []
Testing_Set = []

biography = []

file = open(filename, 'r')
text = file.read()

# Replace any sequence of two or more line breaks with a single line break
text = re.sub(r"\n{2,}", "\n\n", text)

# create an output file called "output.txt" and write the text to it
output = open("output.txt", "w")
output.write(text)
output.close()

file = open("output.txt", 'r')
while len(Training_Set) < numTraining:
    line = file.readline().rstrip('\n ')
    if (line != ''):
        biography.append(line.lower())
    else:
        Training_Set.append(biography)
        biography = []

biography = []
for i in file:
    line = i.rstrip('\n ')
    if (line != ''):
        biography.append(line.lower())
    elif len(biography) != 0:
        Testing_Set.append(biography)
        biography = []
Testing_Set.append(biography)
file.close()

stopWordsList = []
file = open(stopWordsFile, 'r')
for i in file:
    if (i != '\n'):
        line = i.rstrip('\n')
        line = line.split(' ')
        stopWordsList += line
file.close()

StopWords = {}
for i in stopWordsList:
    StopWords[i] = 1

Frequency_category, Frequency_word = trainingFunc(
    Training_Set, StopWords, epsilon)

for i in range(len(Testing_Set)):
    wordList = Testing_Set[i][2].split()
    newWordList = {}
    for j in wordList:
        j = j.rstrip(',. ')
        if j not in StopWords and len(j) > 2:
            for k in Frequency_word:
                if j in Frequency_word[k]:
                    newWordList[j] = -1
    Testing_Set[i][2] = newWordList


Predictions, Probabilities = testingFunc(
    Testing_Set, Frequency_category, Frequency_word)

correct = 0
for bio in Testing_Set:
    str1 = bio[0].title() + ".   " + " Prediction: " + \
        Predictions[bio[0]][0].title() + "."
    if (Predictions[bio[0]][0] == bio[1]):
        correct += 1
        str1 = str1 + "   Right.\n"
    else:
        str1 = str1 + "   Wrong.\n"

    for category in Probabilities[bio[0]]:
        str1 += category.title() + ": " + \
            str(Probabilities[bio[0]][category]) + "   "

    print(str1, '\n')
print("Overall accuracy:", correct, "out of", len(
    Testing_Set), "=", round(correct/len(Testing_Set), 2))

