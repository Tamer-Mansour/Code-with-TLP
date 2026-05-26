# Embeddings and the Transformer Architecture

The most transformative AI advances of the past decade — BERT, GPT-4, Gemini, Llama — all rest on two ideas: **embeddings** (representations) and the **Transformer** architecture. Understanding these ideas lets you reason clearly about what LLMs can and cannot do.

## From Text to Vectors: The Representation Problem

Neural networks operate on numbers, not words. Before a model can process language, text must be converted to vectors of real numbers. The quality of this representation determines everything that follows.

### One-Hot Encoding: The Naive Baseline

Represent each word as a vector of length V (vocabulary size) with a 1 in the word's position and 0s everywhere else. "cat" might be vector [0, 0, 1, 0, ...] and "dog" [0, 1, 0, 0, ...].

Problems:
- **Sparse and huge**: a vocabulary of 50,000 words means 50,000-dimensional vectors.
- **No similarity structure**: "cat" and "kitten" are perfectly orthogonal (dot product = 0), just like "cat" and "democracy." The representation encodes no semantic information.

### Word Embeddings: Distributed Representations

An **embedding** maps each token to a dense vector of dimension d (typically 100–4000). Semantically similar words end up with similar vectors (high cosine similarity).

**Word2Vec** (Mikolov et al., 2013): trains a shallow neural network to predict surrounding words from a center word (Skip-gram) or a center word from surrounding words (CBOW). The learned vectors capture remarkable structure:

```
vector("king") − vector("man") + vector("woman") ≈ vector("queen")
vector("Paris") − vector("France") + vector("Italy") ≈ vector("Rome")
```

This arithmetic works because words used in analogous contexts end up in analogous vector positions.

### Modern Tokenization: Subword Units

Modern LLMs don't use word-level tokens. They use **subword tokenization** (Byte-Pair Encoding, WordPiece, or SentencePiece):

- "unbreakable" → ["un", "break", "able"] (3 tokens)
- "ChatGPT" → ["Chat", "G", "PT"] (3 tokens, as of some tokenizers)
- "2024" → ["2024"] or ["20", "24"] depending on the tokenizer

This handles rare words, new words, and morphology gracefully without requiring a fixed vocabulary for every word in every language. GPT-4's tokenizer has ~100,000 vocabulary entries but can represent essentially any text.

## The Transformer Architecture

Introduced in "Attention Is All You Need" (Vaswani, Shazeer, Parmar et al., 2017), the Transformer replaced recurrent networks as the architecture of choice for virtually every sequence modeling task.

### Why Not RNNs?

Recurrent neural networks process sequences step by step. To compute the hidden state at position t, you must first compute position t−1. This sequential dependency means:
- **No parallelism**: you cannot compute multiple positions simultaneously.
- **Vanishing gradients across long sequences**: information from position 1 must propagate through hundreds of hidden state transitions to influence position 500.
- **Limited context window** in practice (though LSTMs helped).

Transformers solve all of these by processing **all positions in parallel** using attention.

### The Self-Attention Mechanism

The core innovation: to produce a representation of position i, look at *all* positions simultaneously and weight each by how relevant it is.

For a sentence: "The animal didn't cross the street because **it** was too tired."
- Processing "it": self-attention assigns high weight to "animal" (the referent) and low weight to "street."
- Without attention (pure sequential RNN), this long-range dependency is hard to learn.

**Scaled dot-product attention** (for a single query q, keys K, values V):

```
Attention(q, K, V) = softmax( q · Kᵀ / √d_k ) · V
```

For a full sequence (all positions as queries Q):
```
Attention(Q, K, V) = softmax( Q·Kᵀ / √d_k ) · V
```

Where:
- **Q** (queries): what each position is "looking for."
- **K** (keys): what each position "advertises" about itself.
- **V** (values): the actual content to be retrieved.

The dot product Q·Kᵀ produces an n×n attention matrix where entry (i,j) measures how much position i should attend to position j. Dividing by √d_k prevents the dot products from becoming too large (which would push softmax into its saturated region). Softmax converts scores to a probability distribution (weights summing to 1). Multiplying by V produces a weighted sum of position representations.

### Worked Attention Example

Sentence: "cat sat mat" (3 tokens). Suppose d_k=2 (tiny for illustration).

Queries Q:
```
cat: [1, 0]
sat: [0, 1]
mat: [1, 1]
```

Keys K = same as Q for simplicity:
```
cat: [1, 0]
sat: [0, 1]
mat: [1, 1]
```

Attention scores for "mat" (query=[1,1]) vs all keys (divide by √2≈1.41):
```
score(mat→cat) = [1,1]·[1,0] / 1.41 = 1/1.41 ≈ 0.71
score(mat→sat) = [1,1]·[0,1] / 1.41 = 1/1.41 ≈ 0.71
score(mat→mat) = [1,1]·[1,1] / 1.41 = 2/1.41 ≈ 1.41
```

After softmax over [0.71, 0.71, 1.41]:
```
e^0.71 ≈ 2.03,  e^0.71 ≈ 2.03,  e^1.41 ≈ 4.10
sum = 8.16
weights ≈ [0.249, 0.249, 0.502]
```

"mat" attends to itself most (50.2%), and equally to "cat" and "sat" (24.9% each). The output for "mat" is a weighted combination of the values for all three positions.

### Multi-Head Attention

Instead of one attention computation, **multi-head attention** runs H parallel attention heads, each with its own learned Q, K, V projection matrices:

```
MultiHead(Q, K, V) = concat(head₁, ..., headH) · W_O
where headᵢ = Attention(Q·W_Qᵢ, K·W_Kᵢ, V·W_Vᵢ)
```

Different heads learn to attend to different types of relationships simultaneously:
- One head might track subject-verb agreement.
- Another head might track coreference (pronoun → noun).
- Another might capture semantic similarity.

### The Full Transformer Block

A single Transformer layer has two sub-layers, each with a residual connection and layer normalization:

```
x = x + MultiHeadAttention(LayerNorm(x))   # self-attention + residual
x = x + FFN(LayerNorm(x))                  # feed-forward + residual
```

The **Feed-Forward Network** (FFN) applies two linear transformations with a non-linearity (usually GELU):
```
FFN(x) = max(0, x·W₁ + b₁)·W₂ + b₂
```

The FFN dimension is typically 4× the model dimension (e.g., 4096 if the model dimension is 1024). This is where the model stores much of its "factual knowledge" — ablation studies show that factual associations are largely encoded in the FFN weights.

**Residual connections** (`x + sublayer(x)`) allow gradients to flow directly from later layers to earlier layers, enabling very deep networks (GPT-3 has 96 layers).

**Layer normalization** standardizes activations to zero mean and unit variance within each position, stabilizing training.

### Positional Encoding

Attention is **permutation-equivariant** — it treats all positions equally by default. To give the model information about word order, **positional encodings** are added to the token embeddings at the input:

```
PE(pos, 2i)   = sin(pos / 10000^(2i/d))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d))
```

Different dimensions carry position information at different wavelengths, allowing the model to distinguish "dog bites man" from "man bites dog."

Modern LLMs often use **Rotary Position Embedding (RoPE)** or **ALiBi**, which extend better to longer context windows than the original sinusoidal encoding.

### Encoder vs. Decoder

| Variant | Used for | Key design | Examples |
|---|---|---|---|
| Encoder only | Understanding/classification | All positions attend to all | BERT, RoBERTa, DeBERTa |
| Decoder only | Text generation | Each position only attends to earlier positions (causal mask) | GPT-4, Llama, Mistral, Claude |
| Encoder-decoder | Translation, summarization | Encoder processes input; decoder generates output attending to encoder | T5, BART, MarianMT |

GPT-style models use a **causal (autoregressive) mask**: when generating token at position t, the model can only attend to positions 1...t−1. This forces the model to generate text left-to-right and enables training by predicting the next token at every position simultaneously.

## Pre-training and Fine-Tuning

Modern LLMs are trained in two phases:

**Pre-training**: train on hundreds of billions or trillions of tokens of text (books, web, code, papers) by predicting the next token at every position. GPT-3 used 300 billion tokens; GPT-4 reportedly used several trillion. Cost: millions of dollars in compute. This phase builds broad language understanding.

**Fine-tuning / RLHF**: adapt to follow instructions, avoid harmful outputs, and communicate more helpfully. Instruction fine-tuning trains on (instruction, response) pairs. RLHF (Reinforcement Learning from Human Feedback) trains a reward model on human preference data, then uses it as a reward signal to fine-tune the base model using PPO. This is how ChatGPT was created from GPT-3.5.

**Parameter-efficient fine-tuning (LoRA)**: instead of updating all parameters, freeze the pre-trained weights and learn small "delta" matrices. Dramatically reduces the memory and compute cost of fine-tuning.

## Scaling Laws

A key empirical finding: LLM performance improves predictably and smoothly with more parameters, more data, and more compute. The **Chinchilla scaling laws** (Hoffmann et al., 2022) show that the optimal training approach for a given compute budget uses roughly equal tokens and parameters. This guided models like LLaMA to train smaller models on more data rather than huge models on too little data.
