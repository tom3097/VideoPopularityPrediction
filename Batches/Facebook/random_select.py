import random

TRAIN_SAMPLE_NUMBER = 100000
VAL_SAMPLE_NUMBER = int(0.25*TRAIN_SAMPLE_NUMBER)

train_txt = 'train_2.txt'
val_txt = 'val_2.txt'

selected_train_txt = 'selected_train_2.txt'
selected_val_txt = 'selected_val_2.txt'

train_popularity = {}
val_popularity = {}

with open(train_txt, 'r') as tr_file:
    for line in tr_file:
        data = line.split()
        if data[1] in train_popularity:
            train_popularity[data[1]].append(line)
        else:
            train_popularity[data[1]] = [line]

for key in train_popularity.keys():
    random.shuffle(train_popularity[key])

with open(val_txt, 'r') as va_file:
    for line in va_file:
        data = line.split()
        if data[1] in val_popularity:
            val_popularity[data[1]].append(line)
        else:
            val_popularity[data[1]] = [line]

for key in val_popularity.keys():
    random.shuffle(val_popularity[key])


TRAIN_PER_POPULARITY = int(TRAIN_SAMPLE_NUMBER / len(train_popularity.keys()))
VAL_PER_POPULARITY = int(VAL_SAMPLE_NUMBER / len(val_popularity.keys()))
selected_train_popularity = []
selected_val_popularity = []

for key in train_popularity.keys():
    for element in train_popularity[key][:TRAIN_PER_POPULARITY]:
        selected_train_popularity.append(element)
random.shuffle(selected_train_popularity)

for key in val_popularity.keys():
    for element in val_popularity[key][:VAL_PER_POPULARITY]:
        selected_val_popularity.append(element)
random.shuffle(selected_val_popularity)

with open(selected_train_txt, 'w') as st_file:
    for element in selected_train_popularity:
        st_file.write('%s' % element)

with open(selected_val_txt, 'w') as sv_file:
    for element in selected_val_popularity:
        sv_file.write('%s' % element)


