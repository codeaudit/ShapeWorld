from math import sqrt
import tensorflow as tf


def model(world, caption, caption_length, agreement, dropout, vocabulary_size, sizes=(5, 3, 3), nums_filters=(16, 32, 64), poolings=('max', 'max', 'avg'), embedding_size=32, lstm_size=1024, hidden_dims=(512,), **kwargs):

    with tf.name_scope(name='cnn'):
        world_embedding = world
        for size, num_filters, pooling in zip(sizes, nums_filters, poolings):
            weights = tf.Variable(initial_value=tf.random_normal(shape=(size, size, world_embedding.get_shape()[3].value, num_filters), stddev=sqrt(2.0 / world_embedding.get_shape()[3].value)))
            world_embedding = tf.nn.conv2d(input=world_embedding, filter=weights, strides=(1, 1, 1, 1), padding='SAME')
            bias = tf.Variable(initial_value=tf.zeros(shape=(num_filters,)))
            world_embedding = tf.nn.bias_add(value=world_embedding, bias=bias)
            world_embedding = tf.nn.relu(features=world_embedding)
            if pooling == 'max':
                world_embedding = tf.nn.max_pool(value=world_embedding, ksize=(1, 2, 2, 1), strides=(1, 2, 2, 1), padding='SAME')
            elif pooling == 'avg':
                world_embedding = tf.nn.avg_pool(value=world_embedding, ksize=(1, 2, 2, 1), strides=(1, 2, 2, 1), padding='SAME')
        size = 1
        for dims in world_embedding.get_shape()[1:]:
            size *= dims.value
        world_embedding = tf.reshape(tensor=world_embedding, shape=(-1, size))

    with tf.name_scope(name='lstm'):
        embeddings = tf.Variable(initial_value=tf.random_normal(shape=(vocabulary_size, embedding_size), stddev=sqrt(embedding_size)))
        embeddings = tf.nn.embedding_lookup(params=embeddings, ids=caption)
        world_embedding = tf.expand_dims(input=world_embedding, axis=1)
        world_embedding = tf.tile(input=world_embedding, multiples=(1, caption.get_shape()[1].value, 1))
        embeddings = tf.concat(values=(embeddings, world_embedding), axis=2)
        lstm = tf.contrib.rnn.LSTMCell(num_units=lstm_size)
        embeddings, state = tf.nn.dynamic_rnn(cell=lstm, inputs=embeddings, sequence_length=tf.squeeze(input=caption_length, axis=1), dtype=tf.float32)
        embedding = embeddings[:, -1, :]

    with tf.name_scope(name='hidden'):
        for dim in hidden_dims:
            weights = tf.Variable(initial_value=tf.random_normal(shape=(embedding.get_shape()[1].value, dim), stddev=sqrt(2.0 / embedding.get_shape()[1].value)))
            embedding = tf.matmul(a=embedding, b=weights)
            bias = tf.Variable(initial_value=tf.zeros(shape=(dim,)))
            embedding = tf.nn.bias_add(value=embedding, bias=bias)
            embedding = tf.nn.relu(features=embedding)
            embedding = tf.nn.dropout(x=embedding, keep_prob=(1.0 - dropout))

    with tf.name_scope(name='agreement'):
        weights = tf.Variable(initial_value=tf.random_normal(shape=(embedding.get_shape()[1].value, 1), stddev=sqrt(2.0 / embedding.get_shape()[1].value)))
        prediction = tf.matmul(a=embedding, b=weights)

    with tf.name_scope(name='optimization'):
        prediction = (tf.tanh(x=prediction) + 1.0) / 2.0
        cross_entropy = -(agreement * tf.log(x=prediction + 1e-10) + (1.0 - agreement) * tf.log(x=1.0 - prediction + 1e-10))
        tf.losses.add_loss(loss=tf.reduce_mean(input_tensor=cross_entropy))

        prediction = tf.cast(x=tf.greater(x=prediction, y=tf.constant(value=0.5)), dtype=tf.float32)
        correct = tf.cast(x=tf.equal(x=prediction, y=agreement), dtype=tf.float32)
        accuracy = tf.reduce_mean(input_tensor=correct)

    return accuracy
