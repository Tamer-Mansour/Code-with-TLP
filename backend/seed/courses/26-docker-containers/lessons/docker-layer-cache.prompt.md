# Layer Cache Hit Count

## Input

```
N
<previous instruction 1>
<previous instruction 2>
... N lines
M
<current instruction 1>
... M lines
```

- N is the number of instructions in the previous Dockerfile.
- M is the number of instructions in the current Dockerfile.

## Output

A single integer: the number of leading instructions that match exactly between previous and current. (Once they diverge — or one file runs out — the count stops.)

## Examples

Input:

```
3
FROM node:20
COPY package.json .
RUN npm install
3
FROM node:20
COPY package.json .
RUN npm install
```

Output: `3` (identical)

Input:

```
3
FROM node:20
COPY package.json .
RUN npm install
3
FROM node:20
COPY package.json .
RUN npm ci
```

Output: `2` (first two match, third differs)

Input:

```
2
FROM node:18
RUN apt update
2
FROM node:20
RUN apt update
```

Output: `0` (very first line differs)

Input:

```
3
FROM x
COPY .
RUN .
2
FROM x
COPY .
```

Output: `2`

## Notes

- Whitespace inside an instruction line is significant.
- Empty Dockerfiles → output 0.
