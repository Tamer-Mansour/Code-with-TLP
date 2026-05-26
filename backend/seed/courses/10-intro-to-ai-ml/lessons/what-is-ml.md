# What Is Machine Learning?

Traditional programming is explicit: a human writes rules, the computer applies them. Machine Learning flips this: the computer **infers rules from examples**. This shift in paradigm is responsible for most of the AI progress since the 1990s.

## The Classic Definition

> A computer program is said to learn from experience E with respect to some class of tasks T and performance measure P, if its performance at tasks in T, as measured by P, improves with experience E.
> — Tom Mitchell, *Machine Learning*, 1997

For a spam filter:
- **T** = classify emails as spam or not spam.
- **E** = a dataset of labeled emails (spam / not spam).
- **P** = classification accuracy on new, unseen emails.

This definition is deceptively simple but captures the essential idea: learning is measured by *improvement* on a *task* by *doing more of something*.

## Why ML Works: The Core Intuition

Suppose you want to recognize handwritten digits. Writing explicit rules is nearly impossible: the digit "3" can look like two bumps, a right-pointing horn, a squiggly line — the variation is infinite. But show a ML model 60,000 labeled examples (this is the MNIST dataset) and it learns to extract the right features automatically, reaching >99% accuracy on new digits.

ML succeeds when:
- There are **too many rules** to hand-code (spam, faces, speech, protein folding).
- The rules **change over time** (financial fraud patterns evolve as fraudsters adapt).
- Humans can recognize patterns but **cannot articulate** the rules (handwriting, tone of voice, aesthetic quality).

ML fails when:
- Data is scarce or too noisy to detect the underlying pattern.
- The desired output cannot be measured or labeled cheaply.
- The problem has a simple, stable rule — use a lookup table or formula instead.

## Three Learning Paradigms

### Supervised Learning

The training data comes with **labels** — the correct answers. The algorithm learns a mapping from inputs `x` to outputs `y`.

```
Input (features)         Label (target)
Email text features  →   spam (1) / not spam (0)
House: size, location →  price ($350,000)
Medical image        →   tumor present (1) / absent (0)
```

**Classification** predicts a *discrete* category. **Regression** predicts a *continuous* value.

The algorithm minimizes the difference between its predictions `ŷ` and the true labels `y` over the training set, using a **loss function**. Common choices: mean squared error for regression, cross-entropy for classification.

### Unsupervised Learning

No labels. The algorithm discovers **structure** in the data entirely on its own.

```
Input: customer purchase histories (no labels)
Goal:  find k groups of customers with similar buying behavior
```

Common tasks:
- **Clustering**: group similar examples (k-Means, DBSCAN, hierarchical clustering).
- **Dimensionality reduction**: compress high-dimensional data (PCA, t-SNE, autoencoders).
- **Anomaly detection**: find examples that don't fit any cluster (fraud, faults).
- **Generative modeling**: learn to generate new samples from the data distribution (GANs, VAEs, diffusion models).

Unsupervised learning is valuable because labeled data is expensive (requires human annotation), while unlabeled data is abundant (the whole internet).

### Reinforcement Learning

An **agent** interacts with an environment, takes **actions**, observes **state transitions**, and receives **reward** signals. It learns a **policy** — a mapping from states to actions — that maximizes cumulative reward.

```
Agent (game-playing AI)
State:   board position at time t
Action:  move a piece
Reward:  +1 for winning, -1 for losing, 0 for all intermediate moves
Goal:    maximize total reward over the game
```

RL is behind AlphaGo, robotics locomotion, recommendation systems, and automated trading. The key challenge is the **credit assignment problem**: which of the many actions taken during a game caused the eventual win or loss?

### Comparison Table

| Paradigm | Data needed | Core question | Example |
|---|---|---|---|
| Supervised | Labeled (x, y) pairs | What is the output for this input? | Image classifier, spam filter |
| Unsupervised | Unlabeled inputs x | What hidden structure exists? | Customer segmentation, embeddings |
| Reinforcement | Reward signals | What sequence of actions maximizes reward? | AlphaGo, robot control |

## The ML Workflow in Detail

A realistic supervised learning project follows these steps:

**1. Define the problem clearly.** What is the input? What is the output? What does success mean? Many ML projects fail because the business goal is never precisely defined.

**2. Collect and label data.** Raw observations from sensors, logs, surveys, or web scraping. Labeling is often the most expensive step — it requires human judgment.

**3. Explore and clean (EDA).** Summarize distributions, plot histograms, identify missing values, find outliers. A single corrupted feature can destroy model performance if not caught here.

**4. Feature engineering.** Represent raw data as numeric vectors that the algorithm can process. Convert text to bag-of-words or embeddings. Normalize numeric features. Encode categorical variables. Often the highest-leverage step in the project.

**5. Split into train / validation / test.** Before any modeling. Typical ratio: 70% train, 15% validation, 15% test. The test set is a sealed envelope — never opened until final evaluation.

**6. Train a model.** Fit the algorithm to the training data. This adjusts model parameters to minimize the loss function.

**7. Evaluate on validation set.** Measure performance with appropriate metrics (accuracy, F1, RMSE). Compare multiple model architectures and hyperparameters.

**8. Tune hyperparameters.** Hyperparameters (learning rate, tree depth, regularization strength) are *not* learned from data — they are set by the developer and tuned via the validation set. Common technique: grid search or random search.

**9. Final evaluation on test set.** One evaluation, at the very end. This gives an honest estimate of how the model will perform on new data in production.

**10. Deploy and monitor.** Push the model to production. Monitor for **distribution shift** — the real world may gradually differ from training data, causing performance degradation over time.

## Representation: The Hidden Key

A critical insight often missing from introductory treatments: **the representation of inputs matters as much as the algorithm**. 

A raw 28×28 grayscale image is 784 numbers. A linear model over these 784 pixels performs poorly on digit recognition (~92% accuracy). A deep convolutional network over the same pixels achieves >99% — not because it's a fundamentally different kind of learner, but because its architecture automatically *learns better representations* (edges → curves → digit parts → digits) from the data.

Feature engineering is the manual version of what deep learning does automatically. Both are transformations of raw input into a representation that makes the learning problem easier to solve.
