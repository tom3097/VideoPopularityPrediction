import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import caffe
import operator

caffe.set_device(0)
caffe.set_mode_gpu()

net = caffe.Net('/home/tbochens/FineTuning/Facebook/deploy_8.prototxt',
                '/home/tbochens/FineTuning/Facebook/facebook_8_iter_50000.caffemodel',
                caffe.TEST)

# load input and configure preprocessing
transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
transformer.set_mean('data', np.load('/home/tbochens/FineTuning/imagenet_mean.npy').mean(1).mean(1))
transformer.set_transpose('data', (2,0,1))
transformer.set_channel_swap('data', (2,1,0))
transformer.set_raw_scale('data', 255.0)

net.blobs['data'].reshape(50,3,227,227)

thumb_path = "/home/tbochens/Thumbnails/Facebook2/"

total_images = 0
no_thumb = 0
names = []
results = []

with open("/home/tbochens/FineTuning/Facebook/val_8.txt") as f:
    idx = 0
    data = f.read().splitlines()
    for single_line in data:
        thumb_name = single_line.split()[0]
        try:
            im = caffe.io.load_image(thumb_path + thumb_name)
        except Exception as e:
            no_thumb += 1
            print("Cant find %s" % thumb_name)
            print("Idx = %s" % idx)
            continue
        names.append(thumb_name)
        net.blobs['data'].data[idx] = transformer.preprocess('data', im)
        idx += 1
        if idx == 50:
            total_images += 50
            out = net.forward()
            for x in xrange(50):
                results.append( (names[x], out['fc8_8'][x]) )
            net.blobs['data'].data[...] = transformer.preprocess('data', im)
            idx = 0
            names = []
            print("Total images analyzed: %s" % total_images)
    if idx != 0:
        out = net.forward()
        total_images += len(names)
        for x in xrange(len(names)):
            results.append( (names[x], out['fc8_8'][x]) )
        print("Total images analyzed: %s" % total_images)

best_thumb = sorted(results, key=lambda x:x[1][7], reverse=True)
with open("best_thumb_8.txt", 'w') as best_file:
    for position in best_thumb[:25]:
        best_file.write("Filename: %s, Score: %s\n" % (position[0], position[1][7]))
worst_thumb = sorted(results, key=lambda x:x[1][0], reverse=True)
with open("worst_thumb_8.txt", 'w') as worst_file:
    for position in worst_thumb[:25]:
        worst_file.write("Filename: %s, Score: %s\n" % (position[0], position[1][0]))

