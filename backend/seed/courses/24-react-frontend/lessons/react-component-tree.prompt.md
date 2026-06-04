# Component Tree Renderer

React organizes UI as a tree of components. Given a flat list of component relationships and a root component name, output the component tree as an indented hierarchy.

## Input

Lines of the form `Parent Child` (one relationship per line), followed by a **blank line**, then a single line with the **root component name**.

## Output

The component tree printed as an indented hierarchy. Each component is printed as `<ComponentName>`. Use **2 spaces** of indentation per depth level. Children appear in the order they were first declared in the input.

## Examples

**Example 1**

Input:
```
App Header
App Main
App Footer
Main ArticleList
Main Sidebar
ArticleList ArticleCard

App
```

Output:
```
<App>
  <Header>
  <Main>
    <ArticleList>
      <ArticleCard>
    <Sidebar>
  <Footer>
```

**Example 2**

Input:
```
Root Alpha
Root Beta
Alpha Child1
Beta Child2

Root
```

Output:
```
<Root>
  <Alpha>
    <Child1>
  <Beta>
    <Child2>
```

**Example 3**

Input:
```
App Nav

App
```

Output:
```
<App>
  <Nav>
```

## Notes

- A component with no declared children is a leaf node — print it with no children below.
- Each component appears exactly once in the output (no cycles in the input).
- The blank line separator is guaranteed to appear between the relationships and the root.
