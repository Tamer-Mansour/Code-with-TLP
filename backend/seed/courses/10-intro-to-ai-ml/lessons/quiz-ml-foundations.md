# Quiz: Machine Learning Foundations

**Q1. Which learning paradigm uses labeled training data to map inputs to outputs?**
- [x] Supervised learning
- [ ] Unsupervised learning
- [ ] Reinforcement learning
- [ ] Self-supervised learning

**Q2. A model achieves 99% accuracy on training data but only 62% on the test set. This is most likely:**
- [ ] Underfitting — the model is too simple to capture patterns in the data.
- [x] Overfitting — the model has memorized the training data and does not generalize.
- [ ] A data preprocessing bug causing train and test to be on different scales.
- [ ] Normal behavior for classification problems with class imbalance.

**Q3. According to the bias-variance tradeoff, a very complex model typically has:**
- [ ] High bias and high variance.
- [ ] High bias and low variance.
- [x] Low bias and high variance.
- [ ] Low bias and low variance.

**Q4. Why must the test set never be used during model development and hyperparameter tuning?**
- [ ] Test sets are too small to provide useful signal for debugging.
- [ ] Training on the test set would be computationally wasteful.
- [x] Using test performance to make decisions leaks information and makes the final estimate biased and over-optimistic.
- [ ] The test set must be reserved for deployment in production systems.

**Q5. In k-fold cross-validation, what happens to the held-out test set?**
- [ ] It is included in one of the k folds and used for validation in that round.
- [ ] It is used to compute the final training loss after all k rounds.
- [x] It is held out completely from all k folds and used only for the final performance estimate.
- [ ] It is rotated across all folds exactly like the validation set.

**Q6. Which remedy is usually most effective against overfitting when it is feasible?**
- [ ] Increasing model complexity to capture more patterns.
- [ ] Training for more epochs until the training loss is near zero.
- [x] Collecting more training data, which reduces variance without increasing bias.
- [ ] Removing the validation set so all data can be used for training.
