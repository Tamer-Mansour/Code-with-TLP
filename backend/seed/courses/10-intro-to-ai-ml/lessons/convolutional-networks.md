# Convolutional Neural Networks

Fully connected networks treat every pixel as an independent feature, ignoring the fact that neighbouring pixels share structure. **Convolutional Neural Networks (CNNs)** exploit spatial locality and translational symmetry to learn compact, powerful image representations using far fewer parameters.

## The Convolution Operation

A **filter** (also called a kernel) is a small weight matrix — typically 3×3 or 5×5. It slides across the input image (or feature map) with a stride of 1 or more, computing a dot product at each position:

```
For a 3×3 filter K and a 5×5 input patch X:
output[i][j] = sum over r,c of X[i+r][j+c] * K[r][c]
```

A single filter learns to detect one feature — a horizontal edge, a colour gradient, a corner. Stacking many filters gives the layer the ability to detect many features simultaneously.

### Worked Example

Input (5×5, single channel):
```
1 0 1 0 1
0 1 0 1 0
1 0 1 0 1
0 1 0 1 0
1 0 1 0 1
```

Filter (3×3, edge detector):
```
-1  0  1
-1  0  1
-1  0  1
```

Output at position (0,0): `(-1·1 + 0·0 + 1·1) + (-1·0 + 0·1 + 1·0) + (-1·1 + 0·0 + 1·1)` = `0 + 0 + 0 = 0`.

After sliding the filter across the full image (valid convolution, no padding), the output is 3×3. Padding the input with zeros ("same" padding) keeps the output the same spatial size.

## Key Hyperparameters

| Hyperparameter | Meaning | Typical values |
|---|---|---|
| Filter size (k×k) | Receptive field of one neuron | 3×3, 5×5, 7×7 |
| Number of filters | Depth of output feature map | 32, 64, 128, 256 |
| Stride | Step size when sliding | 1 (default), 2 (downsampling) |
| Padding | Zeros added around input | "valid" (none), "same" (preserve size) |

## Pooling Layers

Pooling reduces spatial dimensions, making the network robust to small translations and reducing memory:

- **Max pooling** (most common): takes the maximum value in each pooling window.
- **Average pooling**: takes the mean. Used in some architectures (e.g., global average pooling before the classifier).

Example — 2×2 max pool on a 4×4 feature map:
```python
input = [[1, 3, 2, 4],
         [5, 6, 7, 8],
         [3, 2, 1, 0],
         [9, 1, 4, 2]]

# 2×2 windows, stride 2 → 2×2 output
output = [[6, 8],
           [9, 4]]
```

## A Typical CNN Architecture

```
Input image (H × W × C)
  └─ Conv → ReLU          (learn low-level features: edges, textures)
  └─ MaxPool              (halve spatial dimensions)
  └─ Conv → ReLU          (learn mid-level features: shapes, patterns)
  └─ MaxPool
  └─ Conv → ReLU          (learn high-level features: parts, objects)
  └─ GlobalAveragePool    (collapse spatial dimensions → feature vector)
  └─ Dense → Softmax      (classify)
```

Famous examples: **LeNet-5** (1998, hand-written digits), **AlexNet** (2012, ImageNet breakthrough), **VGG-16** (2014, very deep 3×3 convolutions), **ResNet-50** (2015, skip connections enabling 50+ layers).

## Why CNNs Work

Three structural properties give CNNs their advantage over dense networks on images:

1. **Local connectivity** — each neuron sees only a small patch, not the full image. This encodes the inductive bias that nearby pixels are more correlated than distant ones.
2. **Weight sharing** — all positions in a feature map share the same filter weights. A 3×3 filter applied to a 224×224 image uses only 9 weights, not 224×224=50,176. This massively reduces the parameter count and forces the filter to learn a generic, reusable feature detector.
3. **Translation equivariance** — if an object shifts in the input, its activation map shifts by the same amount. The network does not need to re-learn an edge detector for every possible position.

## Parameter Count Comparison

Consider classifying 32×32 RGB images into 10 classes:

| Layer type | Parameters |
|---|---|
| Dense (3072 → 512 → 10) | 3072 × 512 + 512 + 512 × 10 + 10 = **1,577,994** |
| CNN (32 filters 3×3, stride 1) | 3 × 3 × 3 × 32 + 32 = **896** for the conv layer |

The CNN's first layer needs roughly 2,000× fewer parameters, yet it captures spatial structure that the dense layer ignores entirely.

## Transfer Learning

Pre-trained CNNs (e.g., ResNet-50 trained on ImageNet's 1.2 M images) learn rich general-purpose feature detectors. You can **fine-tune** them on a small domain-specific dataset by:

1. Replacing the final classification head with a new dense layer for your number of classes.
2. Freezing the earlier convolutional layers (keep ImageNet weights).
3. Training only the new head on your data.

This transfers millions of training examples' worth of knowledge to tasks where you may have only hundreds or thousands of labelled examples.
