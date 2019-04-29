import tensorflow as tf
from tensorflow.contrib import rnn

def rnn_layer(inputs, seq_len, num_hidden, num_layers, rnn_type, keep_prob):
    if rnn_type == 'lstm':
        cells = [tf.contrib.rnn.LSTMCell(num_hidden, state_is_tuple=True) for n in range(num_layers)]
        stack = tf.contrib.rnn.MultiRNNCell(cells)
        outputs, state = tf.nn.dynamic_rnn(stack, inputs, seq_len, dtype=tf.float32)
        #state = state[-1][1]
    elif rnn_type == 'gru':
        cells = [tf.contrib.rnn.GRUCell(num_hidden) for n in range(num_layers)]
        stack = tf.contrib.rnn.MultiRNNCell(cells)
        outputs, state = tf.nn.dynamic_rnn(stack, inputs, seq_len, dtype=tf.float32)
    elif rnn_type == 'bi_lstm':
        fw_cells = cells = [tf.contrib.rnn.LSTMCell(num_hidden, state_is_tuple=True) for n in range(num_layers)]
        bw_cells = cells = [tf.contrib.rnn.LSTMCell(num_hidden, state_is_tuple=True) for n in range(num_layers)]
        stack_fw = tf.contrib.rnn.MultiRNNCell(fw_cells)
        stack_bw = tf.contrib.rnn.MultiRNNCell(bw_cells)
        (fw_outputs,bw_outputs), (fw_state,bw_state) = tf.nn.bidirectional_dynamic_rnn(stack_fw,stack_bw,inputs, seq_len, dtype=tf.float32)
        outputs = tf.concat((fw_outputs, bw_outputs), 2)
        state = tf.concat((fw_state, bw_state), 2)
        #state = state[-1][1]
    elif rnn_type == 'bi_gru':
        fw_cells = [tf.contrib.rnn.GRUCell(num_hidden) for n in range(num_layers)]
        bw_cells = [tf.contrib.rnn.GRUCell(num_hidden) for n in range(num_layers)]
        stack_fw = tf.contrib.rnn.MultiRNNCell(fw_cells)
        stack_bw = tf.contrib.rnn.MultiRNNCell(bw_cells)
        (fw_outputs,bw_outputs), (fw_state,bw_state) = tf.nn.bidirectional_dynamic_rnn(stack_fw,stack_bw,inputs, seq_len, dtype=tf.float32)
        outputs = tf.concat((fw_outputs, bw_outputs), 2)
        state = tf.concat((fw_state, bw_state), 2)
    else:
        raise ValueError("unknown rnn type")
    return outputs,state

def get_initializer(type = 'random_uniform', **kwargs):
    '''
    params:
    constant: value
    zeros:
    ones:
    random_normal: mean stddev
    truncated_normal: mean stddev
    random_uniform: minval, maxval
    xavier:
    variance_scaling:
    '''
    #default value
    value = kwargs['value'] if 'value' in kwargs else 0.0
    minval = kwargs['minval'] if 'minval' in kwargs else -1
    maxval = kwargs['maxval'] if 'maxval' in kwargs else 1
    mean = kwargs['mean'] if 'mean' in kwargs else 0.0
    stddev = kwargs['stddev'] if 'stddev' in kwargs else 1.0


    if type == 'constant':
        return tf.constant_initializer(value = value, dtype = tf.float32)
    elif type == 'zeros':
        return tf.zeros_initializer()
    elif type == 'ones':
        return tf.ones_initializer()
    elif type == 'random_normal':
        return tf.random_normal_initializer(mean=0.0, stddev=1.0, seed=None, dtype=tf.float32)
    elif type == 'truncated_normal':
        return tf.truncated_normal_initializer(mean=0.0, stddev=1.0, seed=None, dtype=tf.float32)
    elif type == 'random_uniform':
        return tf.random_uniform_initializer(minval = minval,
                                             maxval = maxval, 
                                             seed=None, 
                                             dtype=tf.float32)
    elif type == 'xavier':
        return tf.contrib.layers.xavier_initializer(uniform=True, seed=None, dtype=tf.float32)
    elif type =='variance_scaling':
        return tf.variance_scaling_initializer(scale=1.0,mode="fan_in",
                                                        distribution="uniform",seed=None,dtype=tf.float32)
    else:
        raise ValueError('unknown type of initializer!')

def conv(inputs, output_units, bias=True, activation=None, dropout=None,
                                 scope='conv-layer', reuse=False):
    with tf.variable_scope(scope, reuse=reuse):
        W = tf.get_variable(
            name='weights',
            initializer=get_initializer(type = 'variance_scaling'),
            shape=[shape(inputs, -1), output_units]
        )
        z = tf.einsum('ijk,kl->ijl', inputs, W)
        if bias:
            b = tf.get_variable(
                name='biases',
                initializer=get_initializer(type = 'zeros'),
                shape=[output_units]
            )
            z = z + b
        z = activation(z) if activation else z
        z = tf.nn.dropout(z, dropout) if dropout else z
    return z

