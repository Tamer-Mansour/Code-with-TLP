# Simple Event System

Implement a simple event system using the Observer pattern. Your `EventBus` class lets observers subscribe to named events and receive data when those events are fired.

## Commands

- `SUBSCRIBE <event_name> <observer_name>` — register an observer for an event
- `UNSUBSCRIBE <event_name> <observer_name>` — remove an observer from an event
- `FIRE <event_name> <data>` — trigger the event; print one line per currently subscribed observer in subscription order: `<observer_name> received <data>`
- `COUNT <event_name>` — print the number of observers currently subscribed to that event

## Input Format

The first line is an integer `N` — the number of commands.
The next `N` lines each contain one command.

Event names and observer names are single words with no spaces.
Data passed to `FIRE` is a single word.

## Output Format

- `FIRE`: for each subscribed observer (in subscription order), print `<observer_name> received <data>`.
- `COUNT`: print the integer count.
- `SUBSCRIBE` / `UNSUBSCRIBE`: no output.

## Example

**Input:**
```
8
SUBSCRIBE click buttonA
SUBSCRIBE click buttonB
SUBSCRIBE hover tooltip
FIRE click pressed
COUNT click
UNSUBSCRIBE click buttonA
FIRE click pressed
COUNT click
```

**Output:**
```
buttonA received pressed
buttonB received pressed
2
buttonB received pressed
1
```
