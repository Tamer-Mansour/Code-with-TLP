# Shape Validator

A common runtime task — check that a JSON object has all the required fields a TypeScript interface declares. Tools like Zod and io-ts generate this code for you; here you'll write the core check by hand.

Read a comma-separated list of required field names, then a series of JSON documents. For each document, output `OK`, `MISSING <fields>`, or `INVALID`.

See the prompt for the exact contract.
