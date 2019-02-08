import random
import numpy as np
import pandas as pd
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.layers import Embedding
from keras.layers import Input, Dense, Embedding, merge, Dropout
from keras.models import Model, Sequential
from sklearn.model_selection import train_test_split
import keras
from keras.layers import Dense, Embedding, LSTM, SpatialDropout1D

texts = []
with open('data/cleaned_pos.txt') as file:
    for line in file:
        line = line.strip()
        texts.append(line)
        
with open('data/cleaned_neg.txt') as file:
    for line in file:
        line = line.strip()
        texts.append(line)

print('Found %s texts.' % len(texts))

MAX_NB_WORDS = 10000
MAX_SEQ_LEN = 15

tokenizer = Tokenizer(num_words=MAX_NB_WORDS)
tokenizer.fit_on_texts(texts)

word_index = tokenizer.word_index
print("Found %s unique tokens" % len(word_index))

pos_ex = list(open('data/cleaned_pos.txt', "r").readlines())
pos_ex = [s.strip() for s in pos_ex]
random.shuffle(pos_ex)

neg_ex = list(open('data/cleaned_neg.txt', "r").readlines())
neg_ex = [s.strip() for s in neg_ex]
random.shuffle(neg_ex)

x_text = pos_ex + neg_ex
x_text = [s.split(" ") for s in x_text]

pos_labels = [[0, 1] for _ in pos_ex]
neg_labels = [[1, 0] for _ in neg_ex]

y = np.concatenate([pos_labels, neg_labels], 0)

embeddings_index = {}
f = open('data/glove.6B.100d.txt')
for line in f:
    values = line.split()
    word = values[0]
    coefs = np.asarray(values[1:], dtype='float32')
    embeddings_index[word] = coefs
f.close()

print("Found %s word vectors"%len(embeddings_index))

embedding_matrix = np.zeros((len(word_index)+1, 100))
for word, i in word_index.items():
    embedding_vector = embeddings_index.get(word)
    if embedding_vector is not None:
        embedding_matrix[i] = embedding_vector

embedding_layer = Embedding(len(word_index)+1, 100, 
                            weights=[embedding_matrix],
                           input_length=MAX_SEQ_LEN,
                           trainable=False)


sequences = tokenizer.texts_to_sequences(x_text)
data = pad_sequences(sequences, maxlen=MAX_SEQ_LEN)
print(len(data))

X_train, X_test, y_train, y_test = train_test_split( data, y, test_size=0.2, random_state=42)

inputs = Input(shape=(MAX_SEQ_LEN, ), dtype='int32')
embedded_sequences = embedding_layer(inputs)

embedding_dim = 100

optimizer = keras.optimizers.Adam(lr=0.0002, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=0.0, amsgrad=False)

model = Sequential()
model.add(Embedding(len(word_index)+1, 100, weights=[embedding_matrix], input_length=MAX_SEQ_LEN, trainable=False))
# model.add(SpatialDropout1D(0.2))
model.add(LSTM(196, return_sequences=True, dropout=0.2))
model.add(LSTM(128))
model.add(Dense(2, activation='softmax'))
model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])
print(model.summary())

model.fit(X_train, y_train, validation_split=0.1, epochs=30, batch_size=45, verbose=1)

pos_cnt, neg_cnt, pos_correct, neg_correct = 0, 0, 0, 0
for x in range(len(X_test)):
    
    result = model.predict(X_test[x].reshape(1,X_test.shape[1]),batch_size=1,verbose = 2)[0]
#     print result, y_test[x]
    if np.argmax(result) == np.argmax(y_test[x]):
        if np.argmax(y_test[x]) == 0:
            neg_correct += 1
        else:
            pos_correct += 1
       
    if np.argmax(y_test[x]) == 0:
        neg_cnt += 1
    else:
        pos_cnt += 1
        
print(pos_cnt, neg_cnt, pos_correct, neg_correct)

print("pos_acc", pos_correct*1.0/pos_cnt*100, "%")
print("neg_acc", neg_correct*1.0/neg_cnt*100, "%")
