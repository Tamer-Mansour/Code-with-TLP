# Quiz: Supervised Learning

**Q1. Logistic regression outputs a value between 0 and 1 because it applies which function to its linear combination of features?**
- [ ] ReLU — outputs max(0, z)
- [x] Sigmoid — outputs 1/(1+e^(-z)), mapping any real number to (0,1)
- [ ] Softmax — distributes probability across multiple classes
- [ ] Tanh — maps to (-1, 1) and is zero-centered

**Q2. In k-nearest neighbors classification, increasing k from 1 to a large value generally:**
- [ ] Increases both bias and variance.
- [ ] Decreases both bias and variance.
- [ ] Increases bias but has no effect on variance.
- [x] Increases bias (smoother boundary) and decreases variance (less sensitivity to individual points).

**Q3. A hospital screening tool for a rare disease should prioritize which metric, and why?**
- [ ] Accuracy — because we want the overall correct rate to be as high as possible.
- [ ] Precision — because false alarms waste medical resources.
- [x] Recall — because missing a sick patient (false negative) is much more costly than a false alarm.
- [ ] F1 — because we always need a balanced metric regardless of context.

**Q4. Which criterion does a decision tree use to choose the best feature split at each node?**
- [ ] The feature with the largest number of distinct values.
- [ ] The feature whose mean is closest to the overall dataset mean.
- [x] The feature and threshold that maximally reduce impurity (e.g., maximize information gain or minimize Gini impurity).
- [ ] The feature with the smallest variance in the training data.

**Q5. What is the F1 score when precision = 0.6 and recall = 1.0?**
- [ ] 0.80 — the arithmetic mean of 0.6 and 1.0
- [x] 0.75 — the harmonic mean: 2·(0.6·1.0)/(0.6+1.0) = 1.2/1.6 = 0.75
- [ ] 0.60 — the minimum of precision and recall
- [ ] 0.70 — the weighted average with equal weights

**Q6. What does L1 (Lasso) regularization do that L2 (Ridge) regularization does not?**
- [ ] It penalizes large weights more severely than L2 does.
- [ ] It prevents overfitting by adding noise to the training data.
- [x] It drives some weights to exactly zero, performing automatic feature selection.
- [ ] It adapts the learning rate separately for each weight.
