# Narrow AI, General AI, and Intelligent Agents

Understanding *what kind* of intelligence an AI system has — and what it cannot do — is essential for working with modern AI tools responsibly. This lesson builds a precise vocabulary for thinking about these questions.

## What Makes Something "Intelligent"?

Philosophers debate this endlessly. For practical purposes, AI researchers follow a **behavioral criterion**: a system behaves intelligently when it perceives its environment, reasons toward a goal, and takes actions that advance that goal effectively.

This sidesteps the hard philosophical question of *consciousness* or *understanding* and focuses on what we can actually measure. Whether a system "truly" understands language is less useful than measuring whether it translates French to Arabic with acceptable accuracy.

## Narrow AI (ANI): The World Today

All AI in production today is **narrow** — optimized for, and only competent at, one specific domain.

| System | What it does brilliantly | What it cannot do at all |
|---|---|---|
| GPT-4 | Generate fluent text across topics | Control a robot arm |
| AlphaFold | Predict protein 3D structure from amino acid sequence | Analyze a financial chart |
| Chess engine (Stockfish) | Play chess at superhuman level | Recognize a face in a photo |
| Fraud detector | Flag suspicious credit card transactions | Translate French |
| DALL-E 3 | Generate photorealistic images from text | Reason about symbolic logic |
| AlphaGo | Play Go at superhuman level | Write a sentence |

The key insight: *performance on task A gives you almost nothing on task B, even when the tasks seem related to humans.* A chess engine that beats every human on Earth is helpless if you ask it to play checkers on the same board. The "intelligence" is locked to the task it was trained for.

### Why Does Narrowness Happen?

Neural networks learn to compress statistical patterns in training data into model weights. A language model learns the distribution over next tokens in human-written text. This produces remarkable fluency but doesn't produce a general-purpose reasoner. The model's "knowledge" is really a very sophisticated pattern-matching machine over text.

## General AI (AGI): The Unsolved Challenge

An AGI would transfer knowledge and reasoning across arbitrary tasks — much like a person does. If you learn to cook, you can also improvise when an ingredient is missing, adapt a recipe for a different culture, teach the skill to someone else, and understand the chemistry of caramelization by analogy to other heat-driven reactions.

Today's narrow systems cannot do this. Several hard unsolved problems stand between current AI and AGI:

**Causal reasoning**: Current systems find correlations in data. Predicting that umbrella sales correlate with rain does not mean the system understands that *rain causes* people to buy umbrellas (not the other way around). Causal inference — the ability to reason about interventions and counterfactuals — remains limited in current systems.

**Common-sense knowledge**: Knowing that ice is cold, that objects fall when dropped, that people have beliefs and intentions — this background knowledge humans absorb through physical experience is largely absent or inconsistently represented in language models.

**Continual learning**: Current systems have a fixed training set. When deployed, they cannot update their weights based on new experiences without risking "catastrophic forgetting" — where learning new information overwrites old. Humans learn continuously throughout life.

**Robust generalization**: A self-driving car trained in California may fail in a Finnish snowstorm because the visual distribution shifted. Humans generalize to genuinely novel environments far more robustly, using causal models of how the world works.

## Intelligent Agents: A Unifying Framework

The textbook definition from Russell & Norvig's *Artificial Intelligence: A Modern Approach* provides a framework that unifies all AI paradigms:

> An agent is anything that can be viewed as perceiving its environment through sensors and acting upon that environment through actuators.

**Sensors** can be cameras, microphones, keyboards, or stock price feeds. **Actuators** can be motors, speakers, displays, or API calls. The key loop is:

```
Percept → Agent Function → Action → Environment → New Percept → ...
```

The **agent function** maps from the full history of percepts to an action. The **agent program** implements this function inside the agent architecture.

### Five Agent Types (in order of sophistication)

**Simple reflex agents** map the current percept directly to an action using condition-action rules. A thermostat: *if temperature < 18°C → turn on heating*. No memory. Cannot handle situations not covered by rules.

**Model-based reflex agents** maintain an internal state — a model of the world — and use it to make better decisions even when the environment is partially observable. A robot vacuum that tracks where it has already cleaned.

**Goal-based agents** choose actions that lead to a desired goal state. They must reason forward: "If I take this action, will I be closer to my goal?" Route-planning GPS is a goal-based agent.

**Utility-based agents** have a richer objective: maximize a **utility function** that captures degrees of desirability. Rather than just "reach the destination," the utility function might weigh speed, fuel cost, and road safety simultaneously. The agent picks the action that maximizes expected utility.

**Learning agents** improve performance over time from experience. They have four conceptual components: a *learning element* (makes improvements), a *performance element* (selects actions), a *critic* (evaluates how well the agent is doing), and a *problem generator* (suggests exploratory actions). Modern ML systems fit here.

## Rationality vs. Human-like Behavior

A persistent misconception: good AI should think *like a human*. In practice, we usually want **rational** behavior: selecting the action that maximizes expected utility given the agent's knowledge and computational budget.

A chess engine thinks nothing like a human. It evaluates millions of positions per second using evaluation functions learned from millions of games. A human grandmaster uses intuition, pattern recognition, and strategic planning developed over years of study. The engine is often stronger — not because it thinks more humanly but because it is more thorough and less subject to fatigue or emotional distraction.

This distinction matters practically: when you evaluate an AI system, judge it by whether it achieves its goal effectively and reliably, not by whether its internal process resembles human cognition.

## Rationality Is Bounded

One refinement from cognitive science: human rationality is **bounded** (Herbert Simon, 1955). Humans cannot process all available information and so use **heuristics** — mental shortcuts that work well on average but fail in specific cases. "Buy what I bought last time" is a heuristic that usually works and requires minimal cognitive effort.

AI systems can be designed to be computationally rational (optimal given constraints on compute time) or boundedly rational (use heuristics when exhaustive search is impractical). Most real AI systems do the latter — chess engines have a fixed search depth budget; language models sample rather than evaluating every possible continuation.

## Key Takeaways

- All deployed AI is narrow; performance on one task does not transfer to others.
- AGI is an open research challenge; timeline estimates vary wildly and honestly.
- The agent model (perceive → reason → act) unifies search algorithms, supervised learning, and reinforcement learning under one roof.
- Rationality — maximizing expected utility — is a more useful design target than human-likeness.
- All practical agents are boundedly rational: they use heuristics and approximations to act within computational constraints.
