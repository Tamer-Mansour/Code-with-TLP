# Score Tracker with Observer Notifications

Implement a `ScoreTracker` (subject) and a simple observer system.

## Classes to implement

- `ScoreTracker` — tracks a named player's score. Observers subscribe to changes.
- Observers are stored by name (a plain string tag). When notified, print `<observer> notified: <player> score is <score>`.

## Commands

Read `N` on the first line, then `N` commands:

- `SET <player> <score>` — set the player's score to `<score>` and notify all subscribers.
- `ADD <player> <delta>` — add `<delta>` to the player's score and notify all subscribers. If the player has no existing score, start from 0.
- `SUBSCRIBE <player> <observer>` — register `<observer>` to receive notifications for `<player>`.
- `UNSUBSCRIBE <player> <observer>` — remove `<observer>` from `<player>`'s subscriber list.
- `SCORE <player>` — print the current score for `<player>`. If unknown, print `0`.

## Notification order

Observers are notified in the order they subscribed.

## Example

```
7
SUBSCRIBE alice watcherA
SUBSCRIBE alice watcherB
SET alice 10
SCORE alice
UNSUBSCRIBE alice watcherA
ADD alice 5
SCORE alice
```

Output:
```
watcherA notified: alice score is 10
watcherB notified: alice score is 10
10
watcherB notified: alice score is 15
15
```
