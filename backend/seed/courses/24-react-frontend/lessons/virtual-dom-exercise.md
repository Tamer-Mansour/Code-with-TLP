# Counting Renders

React only re-renders when state actually changes (with `Object.is` equality). Setting the same value twice produces no new render.

In this exercise you'll simulate that behavior: read a sequence of `SET <key> <value>` commands and count how many of them actually change the (key → value) store.

See the prompt for the exact contract.
