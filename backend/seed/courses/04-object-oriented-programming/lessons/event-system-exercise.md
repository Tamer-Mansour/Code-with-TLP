# Exercise: Simple Event System

Build a minimal event bus using the Observer pattern.

Your `EventBus` class maintains a mapping from event names to lists of observer names. Observers can subscribe and unsubscribe dynamically; firing an event notifies all current subscribers in the order they subscribed.

This exercise reinforces:

- Implementing the Observer pattern with a dictionary of subscriber lists.
- Managing dynamic subscription state (subscribe/unsubscribe).
- Processing command-driven input with correct ordered output.

See the problem statement for the exact command format and expected output.
