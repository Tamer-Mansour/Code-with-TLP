# Gradient Descent and Backpropagation

Training a neural network means finding the parameter values (weights and biases) that minimize the loss function. **Gradient descent** is the optimization algorithm; **backpropagation** is the efficient method to compute the required gradients. Together they are the engine behind all modern deep learning.

## The Loss Function

The loss function measures how wrong the network's predictions are on the training data. It takes the network's output and the true label and returns a single number.

- **MSE** (mean squared error): `L = (1/n)·Σ(ŷ − y)²` — for regression.
- **Binary cross-entropy**: `L = −(1/n)·Σ[y·log(ŷ) + (1−y)·log(1−ŷ)]` — for binary classification.
- **Categorical cross-entropy**: `L = −(1/n)·Σᵢ Σⱼ yᵢⱼ·log(ŷᵢⱼ)` — for multi-class.

The goal of training is to find weights `w` that minimize L(w) over the training set.

## Gradient Descent: The Core Idea

The **gradient** ∂L/∂w tells us: "if I increase weight `w` by a tiny amount, how much does the loss increase?" If the gradient is positive, increasing w makes the loss worse — so we should *decrease* w. If negative, we should *increase* w.

**Gradient descent** moves each weight in the direction that reduces the loss:

```
w ← w − α · ∂L/∂w
```

Where `α` (alpha) is the **learning rate** — a hyperparameter that controls how large each step is.

### Intuition: Rolling Down a Hill

Imagine the loss surface as a hilly landscape. The weights are your position, and the loss is your altitude. Gradient descent always steps in the direction of steepest downhill — toward a valley (local minimum). The learning rate controls how big each step is.

### Worked Example: One Gradient Descent Step

Model: `ŷ = w·x + b` (linear regression, 1 input).
Loss for one example: `L = (ŷ − y)²`
Training point: x=2, y=6. Current weights: w=1, b=0. Learning rate α=0.1.

**Forward pass**:
```
ŷ = 1·2 + 0 = 2
L = (2 − 6)² = 16
```

**Gradients** (using chain rule):
```
∂L/∂ŷ = 2(ŷ − y) = 2(2 − 6) = −8
∂ŷ/∂w = x = 2
∂ŷ/∂b = 1

∂L/∂w = ∂L/∂ŷ · ∂ŷ/∂w = −8 · 2 = −16
∂L/∂b = ∂L/∂ŷ · ∂ŷ/∂b = −8 · 1 = −8
```

**Weight updates**:
```
w_new = 1 − 0.1·(−16) = 1 + 1.6 = 2.6
b_new = 0 − 0.1·(−8)  = 0 + 0.8 = 0.8
```

**Check**: ŷ_new = 2.6·2 + 0.8 = 6.0 = y exactly. With α=0.1 and this particular example, we converged in one step! (This rarely happens in practice — real training data has noise and many examples.)

## Learning Rate Trade-offs

| Learning rate | Effect |
|---|---|
| Too large (α=10) | Overshoots the minimum; loss oscillates or diverges |
| Too small (α=0.00001) | Converges extremely slowly; may get stuck |
| Just right | Smooth, consistent decrease in loss |

**Learning rate scheduling**: start with a larger α (explore quickly) and decay it as training progresses (converge precisely). Common schedules: exponential decay, cosine annealing, warmup + decay.

**Adaptive optimizers** (Adam, RMSprop, AdaGrad) adjust the effective learning rate *per parameter* based on the history of gradients. Adam is the most widely used:
```
m_t = β₁·m_{t-1} + (1-β₁)·g_t     (momentum: running avg of gradient)
v_t = β₂·v_{t-1} + (1-β₂)·g_t²    (running avg of squared gradient)
w ← w − α · m_t / (√v_t + ε)
```
Adam adapts: parameters that have had large gradients in the past get smaller updates, preventing instability.

## Gradient Descent Variants

| Variant | Batch size | Updates per epoch | Notes |
|---|---|---|---|
| Batch gradient descent | All n examples | 1 | Stable gradients; impractical for large n |
| Stochastic GD (SGD) | 1 example | n | Very noisy; can escape local minima; slow |
| Mini-batch GD | m examples (32–512) | n/m | Best of both; GPU-efficient; **standard in practice** |

**Mini-batch gradient descent** is universal in modern deep learning:
- GPUs process many examples in parallel with no overhead — a batch of 64 runs almost as fast as a batch of 1.
- Noisy gradients (from using a subset) act as implicit regularization, sometimes helping generalization.
- Updates are frequent enough to make progress quickly.

## Backpropagation

Computing ∂L/∂w for every weight in a deep network by hand would be impractical for millions of parameters. **Backpropagation** applies the **chain rule of calculus** systematically, computing gradients layer by layer from output back to input. It is efficient because it reuses intermediate computations.

### The Chain Rule

If L depends on ŷ, which depends on z, which depends on w:
```
∂L/∂w = (∂L/∂ŷ) · (∂ŷ/∂z) · (∂z/∂w)
```

In a neural network, the loss depends on the output layer, which depends on the last hidden layer, ..., which depends on the first layer, which depends on the weights. Backprop computes each factor once and multiplies them together.

### Forward Pass vs. Backward Pass

**Forward pass**: feed the input through the network layer by layer, computing each layer's output. Store intermediate activations (they are needed for the gradient computation).

**Backward pass**: starting from ∂L/∂output = 1, propagate gradients backward through each layer:
1. Compute the gradient of L w.r.t. each layer's output (using the chain rule and the stored activations).
2. Compute the gradient of L w.r.t. each layer's parameters (weights and biases).
3. Update parameters using gradient descent.

Modern deep learning frameworks (PyTorch, TensorFlow) build a **computation graph** during the forward pass and automatically apply backprop. This is called **automatic differentiation** (autograd).

## The Vanishing Gradient Problem

With many layers and sigmoid/tanh activations, gradients can become **exponentially small** as they propagate backward. The gradient at layer ℓ involves a product of derivatives from layers ℓ+1, ℓ+2, ..., L. If each derivative is < 1 (as it is for sigmoid in the saturated region), the product shrinks exponentially.

**Example**: 10 layers, each contributing a factor of 0.1 to the gradient. The gradient at layer 1 is 0.1^9 = 10^{-9}. Weights in early layers barely update — they don't learn.

**Solutions**:
- **ReLU activations**: gradient = 1 for positive activations, doesn't shrink.
- **Batch normalization**: normalizes layer inputs to zero mean and unit variance, keeping activations in the non-saturating region.
- **Residual connections (ResNet)**: add skip connections that allow gradients to flow directly from later layers to earlier layers, bypassing the chain of multiplications.
- **Careful weight initialization**: He initialization (for ReLU), Xavier/Glorot initialization (for sigmoid/tanh) scales initial weights to prevent activations from exploding or vanishing at initialization.

## The Exploding Gradient Problem

The opposite: gradients grow exponentially, causing weight updates to become enormous and training to diverge. Common in RNNs processing long sequences.

**Solution**: **gradient clipping** — if the gradient norm exceeds a threshold (e.g., 1.0), scale it down: g ← g · (1.0 / ||g||). This prevents runaway updates without eliminating the gradient signal.

## Putting It All Together

The training loop for one epoch:

```
for each mini-batch (X, Y):
    # Forward pass
    output = network(X)
    loss = loss_function(output, Y)
    
    # Backward pass
    gradients = backprop(loss)
    
    # Update weights
    for each parameter w:
        w ← w − α · gradient_of_w
```

Repeating this over many epochs on a large dataset, with a well-chosen architecture and learning rate, is how modern neural networks are trained.
