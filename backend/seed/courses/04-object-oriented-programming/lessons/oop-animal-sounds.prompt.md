# Animal Sounds via Polymorphism

Implement an animal hierarchy that uses polymorphism to produce sounds. Your program reads commands that create animals and ask them to speak.

## Commands

- `CREATE <animal_type> <name>` — create an animal of the given type with the given name. Supported types: `Dog`, `Cat`, `Cow`, `Duck`.
- `SPEAK <name>` — make the named animal speak. Output format: `<name> says <sound>`.
- `TYPE <name>` — print the type of the named animal.

## Sounds

| Animal | Sound |
|--------|-------|
| Dog | woof |
| Cat | meow |
| Cow | moo |
| Duck | quack |

## Input Format

The first line is an integer `N` — the number of commands.
The next `N` lines each contain one command.

All names are unique single words.

## Output Format

- `SPEAK`: print `<name> says <sound>`
- `TYPE`: print the animal type (e.g., `Dog`)
- `CREATE`: no output

## Example

**Input:**
```
6
CREATE Dog Rex
CREATE Cat Whiskers
CREATE Duck Donald
SPEAK Rex
SPEAK Whiskers
TYPE Donald
```

**Output:**
```
Rex says woof
Whiskers says meow
Duck
```
