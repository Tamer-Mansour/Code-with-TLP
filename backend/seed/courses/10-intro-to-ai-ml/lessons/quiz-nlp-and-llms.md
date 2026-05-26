# Quiz: Modern AI — NLP and LLMs

**Q1. What do word embeddings provide that one-hot encodings do not?**
- [ ] A more memory-efficient representation using sparse vectors.
- [x] Dense vectors that place semantically similar words close together, enabling mathematical operations like vector("king") - vector("man") + vector("woman") ≈ vector("queen").
- [ ] The probability that a word appears next in a given sequence.
- [ ] A lookup table mapping words to their integer IDs in the vocabulary.

**Q2. The core innovation of the Transformer's scaled dot-product attention is:**
- [ ] Using recurrent connections to propagate information across sequential time steps.
- [ ] Applying convolution filters that slide across token positions.
- [x] Computing a weighted sum of all token value representations, where weights are determined by the similarity between each query and key — allowing any token to directly attend to any other.
- [ ] Replacing token embeddings with one-hot vectors to reduce the input dimensionality.

**Q3. In the Transformer, why is position information added explicitly via positional encoding?**
- [ ] Because the feed-forward sublayer operates on the entire sequence at once and would otherwise be slow.
- [ ] Because softmax attention requires inputs to be sorted in order of importance.
- [x] Because self-attention treats all positions equivalently (permutation-equivariant), so without positional encoding the model cannot distinguish "dog bites man" from "man bites dog."
- [ ] Because residual connections cause different positions to interfere with each other without explicit ordering.

**Q4. GPT-style models use a causal mask during attention. What does this prevent?**
- [ ] It prevents the model from attending to padding tokens.
- [ ] It prevents the model from attending to tokens in different sentences.
- [x] It prevents each token from attending to future (later) tokens, so the model can only use past context — enabling autoregressive text generation.
- [ ] It prevents the attention weights from becoming larger than 1.0.

**Q5. Chain-of-thought prompting helps LLMs primarily by:**
- [ ] Increasing the model's effective context window length.
- [ ] Reducing hallucinations by retrieving grounding facts from the internet.
- [x] Encouraging the model to allocate tokens to intermediate reasoning steps, which improves accuracy on multi-step arithmetic, logic, and commonsense problems.
- [ ] Caching previous answers to avoid redundant computation.

**Q6. A recidivism prediction model assigns higher false-positive risk scores to one demographic group at similar actual recidivism rates. This illustrates:**
- [ ] Overfitting to the test set due to excessive hyperparameter tuning.
- [ ] Prompt injection exploiting the model's instruction-following behavior.
- [ ] The curse of dimensionality affecting distance-based predictions.
- [x] Algorithmic bias, where historical patterns in training data lead to systematically different error rates across demographic groups.
