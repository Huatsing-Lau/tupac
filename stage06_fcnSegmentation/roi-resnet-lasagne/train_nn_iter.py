import sys
import gzip
import time
import pickle
import numpy as np

import theano
from theano import tensor as T

import lasagne
from lasagne.updates import nesterov_momentum, adam
from lasagne.layers import helper

from utils import load_pickle_data_cv, batch_iterator_valid, batch_iterator_train_crop_flip, load_pickle_data_tupac, load_data_in_chunks

from matplotlib import pyplot

sys.stdout.flush()

variant = sys.argv[1] if len(sys.argv) > 1 else 'normal'
depth = int(sys.argv[2]) if len(sys.argv) > 2 else 18
width = int(sys.argv[3]) if len(sys.argv) > 3 else 1
print 'Using %s ResNet with depth %d and width %d.'%(variant,depth,width)

if variant == 'normal':
    from models import ResNet_FullPreActivation as ResNet
elif variant == 'bottleneck':
    from models import ResNet_BottleNeck_FullPreActivation as ResNet
elif variant == 'wide':
    from models import ResNet_FullPre_Wide as ResNet
else:
    print ('Unsupported model %s' % variant)

# training params
ITERS = 200
BATCHSIZE = 8
LR_SCHEDULE = {
    0: 0.01,
    10: 0.1,
    80: 0.01,
    120: 0.001,
}

"""
Set up all theano functions
"""
print "Setting up theano functions"
X = T.ftensor4('X')
Y = T.ivector('y')

# set up theano functions to generate output by feeding data through network, any test outputs should be deterministic
# load model

print "Creating ResNet Output Layer"
if width > 1:
    output_layer = ResNet(X, n=depth, k=width)
else:
    output_layer = ResNet(X, n=depth)

print "Creating Outputs"
# create outputs
output_train = lasagne.layers.get_output(output_layer)
output_test = lasagne.layers.get_output(output_layer, deterministic=True)

print "Defining the loss"
# set up the loss that we aim to minimize when using cat cross entropy our Y should be ints not one-hot
loss = lasagne.objectives.categorical_crossentropy(output_train, Y)
loss = loss.mean()

print "Defining L2 Regularization"
# if using ResNet use L2 regularization
all_layers = lasagne.layers.get_all_layers(output_layer)
l2_penalty = lasagne.regularization.regularize_layer_params(all_layers, lasagne.regularization.l2) * 0.0001
loss = loss + l2_penalty

print "Setting up Validation Loss Functions"
# set up loss functions for validation dataset
test_loss = lasagne.objectives.categorical_crossentropy(output_test, Y)
test_loss = test_loss.mean()

test_acc = T.mean(T.eq(T.argmax(output_test, axis=1), Y), dtype=theano.config.floatX)

print "Setting up momentum"
# get parameters from network and set up sgd with nesterov momentum to update parameters, l_r is shared var so it can be changed
l_r = theano.shared(np.array(LR_SCHEDULE[0], dtype=theano.config.floatX))
params = lasagne.layers.get_all_params(output_layer, trainable=True)
#updates = nesterov_momentum(loss, params, learning_rate=l_r, momentum=0.9)
updates = adam(loss, params, learning_rate=l_r)

print "Creating training and prediction functions"
# set up training and prediction functions
train_fn = theano.function(inputs=[X,Y], outputs=loss, updates=updates)
valid_fn = theano.function(inputs=[X,Y], outputs=[test_loss, test_acc])
print "Done setting up!"

# loop over training functions for however many iterations, print information while training
train_eval = []
valid_eval = []
valid_acc = []
best_acc = 0.0

CHUNKS = 200 # 200 * 1,000 = 200,000 training images per epoch

try:
    for epoch in range(ITERS):
        for chunk in range(CHUNKS):
            
            print "[INFO] Loading chunk data for chunk " + str(chunk) + " in epoch " + str(epoch)            
            train_X, test_X, train_y, test_y = load_data_in_chunks(chunk) # chunk is from 0 to 19
            print "Data load complete."

            # change learning rate according to schedules
            if epoch in LR_SCHEDULE:
                l_r.set_value(LR_SCHEDULE[epoch])
            # do the training
            start = time.time()

            train_loss = batch_iterator_train_crop_flip(train_X, train_y, BATCHSIZE, train_fn)
            train_eval.append(train_loss)

            valid_loss, acc_v = batch_iterator_valid(test_X, test_y, BATCHSIZE, valid_fn)
            valid_eval.append(valid_loss)
            valid_acc.append(1.0 - acc_v)

            ratio = train_loss / valid_loss
            end = time.time() - start
            # print training details
            print 'chunk:', chunk, '(', epoch, ')', '| TL:', np.round(train_loss,decimals=3), '| VL:', np.round(valid_loss,decimals=3), '| Vacc:', np.round(acc_v,decimals=3), '| Ratio:', np.round(ratio,decimals=2), '| Time:', np.round(end,decimals=1)

            if acc_v > best_acc:
                best_acc = acc_v
                best_params = helper.get_all_param_values(output_layer)

except KeyboardInterrupt:
    pass

print "Final Acc:", best_acc

# save weights
all_params = helper.get_all_param_values(output_layer)
f = gzip.open('data/weights/%s%d_resnet.pklz'%(variant,depth), 'wb')
pickle.dump(best_params, f)
f.close()

# plot loss and accuracy
train_eval = np.array(train_eval)
valid_acc = np.array(valid_acc)
pyplot.plot(train_eval, label='Train loss', color='#707070')
pyplot.ylabel('Categorical Cross Entropy Loss')
pyplot.xlabel('Epoch')
pyplot.legend(loc=2)
#pyplot.ylim([0,1.5])
pyplot.twinx()
pyplot.ylabel('Valid Acc Error (%)')
pyplot.grid()
pyplot.plot(valid_acc, label='Valid classification error (%)', color='#ED5724')
pyplot.legend(loc=1)
pyplot.savefig('plots/%s%d_resnet.png'%(variant,depth))
pyplot.clf()
#pyplot.show()
