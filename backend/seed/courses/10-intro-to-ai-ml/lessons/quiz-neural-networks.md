# Quiz: Neural Networks & Deep Learning

**Q1. Why do neural networks use non-linear activation functions?**
- [ ] To make the network faster to train by reducing the number of computations.
- [x] Without non-linearity, any composition of linear layers is still a single linear transformation, and the network cannot represent non-linear functions.
- [ ] To prevent the loss function from producing negative values during training.
- [ ] Because linear activations cannot handle floating-point inputs correctly.

**Q2. ReLU is preferred over sigmoid in hidden layers primarily because:**
- [ ] It outputs values between 0 and 1, which matches probability interpretations.
- [ ] It is symmetric around zero, which speeds up gradient descent.
- [x] Its gradient is 1 for positive inputs, preventing the vanishing gradient problem that plagues sigmoid's near-zero gradients in the saturated region.
- [ ] It requires fewer parameters than sigmoid because it has no exponential computation.

**Q3. In mini-batch gradient descent, what is the "batch size"?**
- [ ] The total number of training examples in the dataset.
- [x] The number of training examples processed together before performing one weight update.
- [ ] The number of hidden layers in the network.
- [ ] The number of training epochs completed so far.

**Q4. Backpropagation computes gradients efficiently by:**
- [ ] Running the network forward many times with different random weights.
- [ ] Randomly sampling gradients using Monte Carlo estimates.
- [x] Applying the chain rule layer by layer from the output back to the input, reusing intermediate activations stored during the forward pass.
- [ ] Numerically estimating gradients with finite differences for each weight individually.

**Q5. The vanishing gradient problem occurs when:**
- [x] Gradients become exponentially small as they propagate backward through many layers, causing early layers to receive nearly zero gradient signal and learn extremely slowly.
- [ ] The learning rate is set too large, causing weight updates to oscillate around the minimum.
- [ ] The network has too few parameters relative to the training set size.
- [ ] Batch normalization removes all variance from layer activations.

**Q6. Residual connections (skip connections), as used in ResNet, primarily help by:**
- [ ] Reducing the number of parameters in the network significantly.
- [ ] Preventing overfitting by adding regularization at each layer.
- [x] Allowing gradients to flow directly from later layers to earlier layers, bypassing intermediate layers and alleviating the vanishing gradient problem in very deep networks.
- [ ] Automatically selecting the best subset of features from the input.
