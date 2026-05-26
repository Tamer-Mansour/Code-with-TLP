# Neurons, Layers, and Activation Functions

A neural network is a system of simple computing units — artificial neurons — wired together in layers. Each neuron does almost nothing on its own; the power comes from composing thousands of them and learning the right weights.

## The Artificial Neuron

Inspired loosely by biological neurons (though the analogy should not be taken too literally), an artificial neuron:

1. Receives a vector of inputs x₁, x₂, ..., xₙ.
2. Computes a **weighted sum**: z = w₀ + w₁x₁ + w₂x₂ + ... + wₙxₙ.
3. Applies a non-linear **activation function**: output = f(z).

Step 2 alone is just a linear function — you could stack a thousand linear functions on top of each other and the whole network would still be equivalent to a single linear function. The activation function in step 3 is what makes deep networks powerful.

### Worked Example: One Neuron

Inputs: x₁=2, x₂=3. Weights: w₀=−1 (bias), w₁=0.5, w₂=0.4. Activation: ReLU.

```
z = −1 + 0.5·2 + 0.4·3 = −1 + 1.0 + 1.2 = 1.2
output = ReLU(1.2) = max(0, 1.2) = 1.2
```

If we change x₂=0:
```
z = −1 + 1.0 + 0 = 0.0
output = ReLU(0.0) = 0.0
```

If x₁=0.5, x₂=0:
```
z = −1 + 0.25 + 0 = −0.75
output = ReLU(−0.75) = 0.0
```

ReLU maps all negative pre-activations to exactly 0 ("dead neuron" region) and passes positive values through unchanged.

## Common Activation Functions

### Sigmoid

```
σ(z) = 1 / (1 + e^(-z))
```

- Output range: (0, 1). Interpretable as a probability.
- σ(0) = 0.5, σ(2) ≈ 0.88, σ(−2) ≈ 0.12.
- **Vanishing gradient problem**: for |z| > 4, the derivative σ'(z) = σ(z)·(1−σ(z)) < 0.02. Gradients effectively vanish, making very deep networks untrainable with sigmoid hidden layers.
- **Still used**: output layer for binary classification.

### Tanh

```
tanh(z) = (e^z − e^(−z)) / (e^z + e^(−z))
```

- Output range: (−1, 1). Zero-centered (unlike sigmoid's (0,1)).
- Derivative: tanh'(z) = 1 − tanh²(z). Also suffers from vanishing gradients for large |z|.
- Historically used in hidden layers of RNNs; mostly replaced by ReLU in feedforward networks.

### ReLU (Rectified Linear Unit)

```
ReLU(z) = max(0, z)
```

- Output range: [0, ∞).
- Derivative: 1 for z > 0, 0 for z < 0 (undefined at z=0, set to 0 by convention).
- **No vanishing gradient for positive activations** — gradient is always 1, so it flows freely backward.
- **Dying ReLU problem**: if a neuron's pre-activation is always negative, its gradient is always 0 and it never updates. The neuron "dies."
- **Dominant choice** for hidden layers in feedforward and convolutional networks.

### Leaky ReLU

```
LeakyReLU(z) = max(0.01·z, z)
```

For z < 0: output is 0.01·z (small negative slope) instead of 0. Prevents dying neurons by ensuring a non-zero gradient everywhere.

### Softmax (for output layer)

```
softmax(zᵢ) = e^(zᵢ) / Σⱼ e^(zⱼ)
```

Converts a vector of raw scores (logits) into a probability distribution — all outputs sum to 1. Used in the output layer for multi-class classification (k mutually exclusive classes).

Example: logits [2.0, 1.0, 0.5]:
```
e^2.0 = 7.389
e^1.0 = 2.718
e^0.5 = 1.649
sum   = 11.756
softmax = [7.389/11.756, 2.718/11.756, 1.649/11.756]
        ≈ [0.629, 0.231, 0.140]
```
The model assigns 62.9% probability to class 0.

## Layer Types

### Input Layer

Holds the raw features. No learnable parameters. Just passes data to the first hidden layer.

### Dense (Fully Connected) Hidden Layers

Every neuron in layer ℓ is connected to every neuron in layer ℓ−1. For a layer with h neurons receiving input of dimension d, this requires **h·d + h** parameters (weights + biases).

Example: input_dim=784 (28×28 image), first hidden layer has 64 neurons:
Parameters = 784·64 + 64 = 50,176 + 64 = **50,240**

### Output Layer

Activation depends on task:
- **Binary classification**: 1 sigmoid neuron → probability in (0,1).
- **Multi-class classification**: k softmax neurons → probability distribution.
- **Regression**: 1 linear neuron (no activation) → any real value.

## Network Depth and Capacity

**Shallow vs. deep networks**:

The **Universal Approximation Theorem** states that a network with a single hidden layer and enough neurons can approximate any continuous function to arbitrary precision. So why go deep?

- Deep networks are **more parameter-efficient**: a deep network of depth L with O(d) neurons per layer can represent functions that require O(d^L) neurons in a single-layer network. Exponentially more expressive for the same number of parameters.
- Deep networks learn **hierarchical representations**: early layers learn simple features (edges, textures); later layers combine them into complex patterns (faces, objects). This inductive bias aligns with how many real-world phenomena are structured.
- Empirically, depth outperforms width on almost every benchmark task.

### Parameter Count Example

Network: [input: 784] → [hidden1: 128] → [hidden2: 64] → [output: 10]

| Layer | Computation | Parameters |
|---|---|---|
| hidden1 | 784→128 | 784·128 + 128 = 100,480 |
| hidden2 | 128→64 | 128·64 + 64 = 8,256 |
| output | 64→10 | 64·10 + 10 = 650 |
| **Total** | | **109,386** |

This relatively small network has 109K learnable parameters — quite manageable. GPT-4 has approximately 1.8 trillion parameters.

## Specialized Architectures

While dense networks are the foundation, specialized architectures exploit structure in specific data types:

| Architecture | Abbreviation | Key idea | Dominant use |
|---|---|---|---|
| Convolutional Neural Net | CNN | Shared filters slide across spatial positions | Images, video, audio |
| Recurrent Neural Net | RNN/LSTM/GRU | Hidden state carries information across time steps | Sequences (now largely replaced) |
| Transformer | — | Self-attention over all positions in parallel | Language, vision, any sequence |
| Graph Neural Net | GNN | Message passing between graph nodes | Molecules, social networks, knowledge graphs |
| Diffusion Model | — | Learn to reverse a noise process | Image generation (Stable Diffusion, DALL-E) |

Understanding dense networks (this lesson) and the Transformer (Module 7) covers the foundations needed to understand all modern AI systems.
