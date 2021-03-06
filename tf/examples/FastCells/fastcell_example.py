# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT license.

import helpermethods
import tensorflow as tf
import numpy as np
import sys
sys.path.insert(0, '../../')

from edgeml.trainer.fastTrainer import FastTrainer
from edgeml.graph.rnn import FastGRNNCell
from edgeml.graph.rnn import FastRNNCell


def main():
    # Fixing seeds for reproducibility
    tf.set_random_seed(42)
    np.random.seed(42)

    # Hyper Param pre-processing
    args = helpermethods.getArgs()

    dataDir = args.data_dir
    cell = args.cell
    inputDims = args.input_dim
    hiddenDims = args.hidden_dim

    totalEpochs = args.epochs
    learningRate = args.learning_rate
    outFile = args.output_file
    batchSize = args.batch_size
    decayStep = args.decay_step
    decayRate = args.decay_rate

    wRank = args.wRank
    uRank = args.uRank

    sW = args.sW
    sU = args.sU

    update_non_linearity = args.update_nl
    gate_non_linearity = args.gate_nl

    (dataDimension, numClasses,
        Xtrain, Ytrain, Xtest, Ytest) = helpermethods.preProcessData(dataDir)

    assert dataDimension % inputDims == 0, "Infeasible per step input, " + \
        "Timesteps have to be integer"

    X = tf.placeholder(
        "float", [None, int(dataDimension / inputDims), inputDims])
    Y = tf.placeholder("float", [None, numClasses])

    currDir = helpermethods.createTimeStampDir(dataDir, cell)

    helpermethods.dumpCommand(sys.argv, currDir)

    if cell == "FastGRNN":
        FastCell = FastGRNNCell(hiddenDims,
                                gate_non_linearity=gate_non_linearity,
                                update_non_linearity=update_non_linearity,
                                wRank=wRank, uRank=uRank)
    elif cell == "FastRNN":
        FastCell = FastRNNCell(hiddenDims,
                               update_non_linearity=update_non_linearity,
                               wRank=wRank, uRank=uRank)
    else:
        sys.exit('Exiting: No Such Cell as ' + cell)

    FastCellTrainer = FastTrainer(
        FastCell, X, Y, sW=sW, sU=sU,
        learningRate=learningRate, outFile=outFile)

    sess = tf.InteractiveSession()
    sess.run(tf.global_variables_initializer())

    FastCellTrainer.train(batchSize, totalEpochs, sess, Xtrain, Xtest,
                          Ytrain, Ytest, decayStep, decayRate,
                          dataDir, currDir)


if __name__ == '__main__':
    main()
