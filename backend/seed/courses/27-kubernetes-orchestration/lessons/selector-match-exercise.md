# Selector Matching

A Service finds its pods by **label selector**. A selector `app=web` matches pods that carry `app: web` among their labels. Multiple selectors `app=web,env=prod` require both.

In this exercise you'll implement that matching logic.

See the prompt.
