import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
import random
import ping_pong_game
import cv2
import numpy as np 
from collections import deque

ACTIONS = 3
GAMMA = 0.99
INITIAL_EPSILON = 1.0
FINAL_EPSILON = 0.05
EXPLORE = 500000 
OBSERVE = 50000 
REPLAY_MEMORY = 500000
BATCH = 100

#create tensorflow graph
def createTensorFlowGraph():

    convolution_layer1 = tf.Variable(tf.zeros([8, 8, 4, 32]))
    bias_convolution_layer1 = tf.Variable(tf.zeros([32]))
    convolution_layer2 = tf.Variable(tf.zeros([4, 4, 32, 64]))
    bias_convolution_layer2 = tf.Variable(tf.zeros([64]))
    convolution_layer3 = tf.Variable(tf.zeros([3, 3, 64, 64]))
    bias_convolution_layer3 = tf.Variable(tf.zeros([64]))
    convolution_layer4 = tf.Variable(tf.zeros([3136, 784]))
    bias_convolution_layer4 = tf.Variable(tf.zeros([784]))
    convolution_layer5 = tf.Variable(tf.zeros([784, ACTIONS]))
    bias_convolution_layer5 = tf.Variable(tf.zeros([ACTIONS]))
    z = tf.compat.v1.placeholder("float", [None, 84, 84, 4])
    convolution1 = tf.nn.relu(tf.nn.conv2d(z, convolution_layer1, strides = [1, 4, 4, 1], padding = "VALID") + bias_convolution_layer1)
    convolution2 = tf.nn.relu(tf.nn.conv2d(convolution1, convolution_layer2, strides = [1, 2, 2, 1], padding = "VALID") + bias_convolution_layer2)
    convolution3 = tf.nn.relu(tf.nn.conv2d(convolution2, convolution_layer3, strides = [1, 1, 1, 1], padding = "VALID") + bias_convolution_layer3)
    convolution3_flat = tf.reshape(convolution3, [-1, 3136])
    convolution4 = tf.nn.relu(tf.matmul(convolution3_flat, convolution_layer4) + bias_convolution_layer4)
    convolution5 = tf.matmul(convolution4, convolution_layer5) + bias_convolution_layer5

    return z, convolution5

#deep q network implementation in which we feed in pixel data to graph session 
def trainNetwork(input, out, sess):

    argmax = tf.compat.v1.placeholder("float", [None, ACTIONS]) 
    gt = tf.compat.v1.placeholder("float", [None]) 
    action = tf.reduce_sum(tf.multiply(out, argmax), reduction_indices = 1)
    cost = tf.reduce_mean(tf.square(action - gt))
    train_step = tf.train.AdamOptimizer(1e-6).minimize(cost)

    game = ping_pong_game.PingPongGame()
    D = deque()
    initial_frame = game.capturePresentWindow()
    initial_frame = cv2.cvtColor(cv2.resize(initial_frame, (84, 84)), cv2.COLOR_BGR2GRAY)
    ret, initial_frame = cv2.threshold(initial_frame, 1, 255, cv2.THRESH_BINARY)
    input_t = np.stack((initial_frame, initial_frame, initial_frame, initial_frame), axis = 2)
    saver = tf.train.Saver()
    sess.run(tf.initialize_all_variables())
    t = 0
    epsilon = INITIAL_EPSILON
    while(1):
        out_t = out.eval(feed_dict = {input : [input_t]})[0]
        argmax_t = np.zeros([ACTIONS])
        if(random.random() <= epsilon):
            maxIndex = random.randrange(ACTIONS)
        else:
            maxIndex = np.argmax(out_t)
        argmax_t[maxIndex] = 1
        if epsilon > FINAL_EPSILON:
            epsilon -= (INITIAL_EPSILON - FINAL_EPSILON) / EXPLORE

        reward_t, initial_frame = game.captureNextWindow(argmax_t)
        initial_frame = cv2.cvtColor(cv2.resize(initial_frame, (84, 84)), cv2.COLOR_BGR2GRAY)
        ret, initial_frame = cv2.threshold(initial_frame, 1, 255, cv2.THRESH_BINARY)
        initial_frame = np.reshape(initial_frame, (84, 84, 1))
        input_t1 = np.append(initial_frame, input_t[:, :, 0:3], axis = 2)
        D.append((input_t, argmax_t, reward_t, input_t))

        if len(D) > REPLAY_MEMORY:
            D.popleft()
        
        if t > OBSERVE:
            small_batch = random.sample(D, BATCH)
            inp_batch = [d[0] for d in small_batch]
            argmax_batch = [d[1] for d in small_batch]
            reward_batch = [d[2] for d in small_batch]
            input_t1_batch = [d[3] for d in small_batch]
            gt_batch = []
            out_batch = out.eval(feed_dict = {input : input_t1_batch})
            for i in range(0, len(small_batch)):
                gt_batch.append(reward_batch[i] + GAMMA * np.max(out_batch[i]))
            train_step.run(feed_dict = {
                           gt : gt_batch,
                           argmax : argmax_batch,
                           input : inp_batch
                           })
        input_t = input_t1
        t = t+1
        if t % 10000 == 0:
            saver.save(sess, './' + 'ping_pong_game' + '-dqn', global_step = t)
        print("TIMESTEP", t, "/ EPSILON", epsilon, "/ ACTION", maxIndex, "/ REWARD", reward_t, "/ Q_MAX %e" % np.max(out_t))


def main():
    sess=tf.compat.v1.InteractiveSession()
    input, out = createTensorFlowGraph()
    trainNetwork(input, out, sess)

if __name__ == "__main__":
    main()
