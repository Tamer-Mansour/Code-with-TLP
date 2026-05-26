# Evaluation Metrics for Supervised Learning

Choosing the right metric is as important as choosing the right model. Accuracy sounds intuitive but often misleads. This lesson introduces the confusion matrix, all major metrics derived from it, and regression metrics — with worked numeric examples throughout.

## The Confusion Matrix

For a binary classifier (positive=1, negative=0), every prediction falls into one of four cells:

|  | Predicted Positive | Predicted Negative |
|---|---|---|
| **Actual Positive** | True Positive (TP) | False Negative (FN) |
| **Actual Negative** | False Positive (FP) | True Negative (TN) |

- **TP (True Positive)**: correctly predicted positive. Test says "sick", patient is sick.
- **TN (True Negative)**: correctly predicted negative. Test says "healthy", patient is healthy.
- **FP (False Positive)**: predicted positive, actually negative. *Type I error* — false alarm.
- **FN (False Negative)**: predicted negative, actually positive. *Type II error* — miss.

The relative cost of FP vs. FN determines which metrics matter most for a given problem.

## Core Metrics: Full Worked Example

A disease detector on **100 patients** (10 actually sick, 90 healthy):

| Predicted \ Actual | Sick | Healthy |
|---|---|---|
| Positive (flagged) | **TP = 8** | **FP = 5** |
| Negative (cleared) | **FN = 2** | **TN = 85** |

Total: 8 + 5 + 2 + 85 = 100 ✓

### Accuracy

```
Accuracy = (TP + TN) / Total = (8 + 85) / 100 = 93/100 = 0.93
```

93% — sounds excellent! But this hides serious problems (2 sick patients were missed).

**Problem with accuracy on imbalanced data**: if 99% of emails are not spam, a model that *always* predicts "not spam" achieves 99% accuracy while catching *zero* spam. Accuracy is dangerously misleading here.

### Precision

```
Precision = TP / (TP + FP) = 8 / (8 + 5) = 8/13 ≈ 0.615
```

"Of all the patients I flagged as sick, 61.5% actually were sick." Low precision means many false alarms.

### Recall (Sensitivity, True Positive Rate)

```
Recall = TP / (TP + FN) = 8 / (8 + 2) = 8/10 = 0.80
```

"Of all actually sick patients, I caught 80%." Low recall means many missed cases.

### F1 Score

The harmonic mean of precision and recall:
```
F1 = 2 · (Precision · Recall) / (Precision + Recall)
   = 2 · (0.615 · 0.80) / (0.615 + 0.80)
   = 2 · 0.492 / 1.415
   ≈ 0.696
```

The F1 score is 0.696 — significantly lower than the misleading 93% accuracy. F1 penalizes any model that achieves high precision by ignoring positives, or high recall by flagging everything.

**Why harmonic mean?** The harmonic mean is always ≤ arithmetic mean. It only gives a high value when *both* precision and recall are high. If either is near 0, F1 is near 0.

### Specificity (True Negative Rate)

```
Specificity = TN / (TN + FP) = 85 / (85 + 5) = 85/90 ≈ 0.944
```

"Of all actually healthy patients, 94.4% were correctly cleared." Also called **Recall for the negative class**.

### Summary Table for the Example

| Metric | Formula | Value |
|---|---|---|
| Accuracy | (TP+TN)/Total | 0.93 |
| Precision | TP/(TP+FP) | 0.615 |
| Recall | TP/(TP+FN) | 0.80 |
| F1 | 2·P·R/(P+R) | 0.696 |
| Specificity | TN/(TN+FP) | 0.944 |

## Precision-Recall Tradeoff

Most classifiers output a **probability score**, and you choose a **threshold** to convert it to a class label.

**Lowering the threshold** (e.g., 0.5 → 0.3): flag more patients as sick.
- Recall increases: catch more true sick patients.
- Precision decreases: more false alarms (healthy patients flagged).

**Raising the threshold** (e.g., 0.5 → 0.7): only flag when very confident.
- Precision increases: fewer false alarms.
- Recall decreases: miss more sick patients.

This tradeoff is unavoidable. The right operating point depends on the **cost of errors**:
- Medical diagnosis: low threshold, high recall. Missing cancer is catastrophic; a false alarm leads to a follow-up test.
- Spam filter: higher threshold, high precision. False positives (important email in spam folder) annoy users.

**ROC Curve** (Receiver Operating Characteristic): plots True Positive Rate (Recall) vs. False Positive Rate (FP/(FP+TN)) as the threshold varies. The **AUC** (Area Under the ROC Curve) summarizes overall discriminability — AUC=1.0 is perfect, AUC=0.5 is random guessing.

## Multi-Class Metrics

For k > 2 classes, build a k×k confusion matrix. Then compute metrics either:

- **Macro-average**: compute metric per class, average equally. Treats rare classes equally to frequent ones.
- **Micro-average**: sum all TP/FP/FN across classes, then compute once. Dominated by frequent classes.
- **Weighted average**: weight per-class metrics by class frequency.

## Regression Metrics

For regression tasks (continuous output):

| Metric | Formula | Notes |
|---|---|---|
| MAE | (1/n)·Σ\|y−ŷ\| | Robust to outliers; same units as target |
| MSE | (1/n)·Σ(y−ŷ)² | Penalizes large errors heavily; sensitive to outliers |
| RMSE | √MSE | Same units as target; most common |
| R² | 1 − SS_res/SS_tot | 1.0 = perfect; 0 = predicts mean; can be negative |

**Worked example**: True values [3, 5, 2], predictions [2.5, 5.5, 2.0].
```
Errors: [0.5, 0.5, 0.0]
MAE  = (0.5 + 0.5 + 0.0) / 3 = 0.333
MSE  = (0.25 + 0.25 + 0.0) / 3 = 0.167
RMSE = √0.167 ≈ 0.408
```
Mean of true values = (3+5+2)/3 = 3.333.
SS_res = 0.25+0.25+0.0 = 0.5
SS_tot = (3−3.33)²+(5−3.33)²+(2−3.33)² = 0.111+2.789+1.769 = 4.667
R² = 1 − 0.5/4.667 = 1 − 0.107 = **0.893**

## Choosing the Right Metric

| Situation | Recommended metric |
|---|---|
| Balanced binary classes | Accuracy or F1 |
| Imbalanced classes | F1 (classification), PR-AUC |
| Medical diagnosis | Recall (catching all true positives critical) |
| Spam filter | Precision (user experience matters) |
| Ranking/retrieval | AUC-ROC, NDCG |
| Continuous prediction | RMSE (if large errors are bad), MAE (if robust) |
| Explained variance needed | R² |

**Never choose metrics after seeing results.** Decide which metrics matter based on the *problem requirements* before training any model. Metric shopping is a form of overfitting.
