# Library Catalog (Composition)

Implement a multi-shelf library catalog.

## Classes

- `Book(title, author)` — represents a book.
- `Shelf(name)` — holds books on a named shelf.
- `Library` — contains multiple shelves.

## Commands

Read `N` on the first line, then `N` commands:

- `ADD_SHELF <name>` — add a shelf with the given name.
- `ADD_BOOK <shelf> <title> <author>` — add a book to the named shelf.
- `LIST_SHELF <shelf>` — print all books on the shelf, one per line as `<title> by <author>`, in insertion order. If the shelf is empty, print `EMPTY`.
- `SEARCH <title>` — print the shelf name that contains a book with exactly this title. If not found, print `NOT FOUND`. If on multiple shelves, print the first shelf that contained it.
- `COUNT <shelf>` — print the number of books on the shelf.

## Example

```
8
ADD_SHELF fiction
ADD_SHELF science
ADD_BOOK fiction Dune Herbert
ADD_BOOK fiction Foundation Asimov
ADD_BOOK science ABriefHistory Hawking
LIST_SHELF fiction
COUNT science
SEARCH Foundation
```

Output:
```
Dune by Herbert
Foundation by Asimov
1
fiction
```
