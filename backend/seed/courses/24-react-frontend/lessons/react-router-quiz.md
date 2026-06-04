# Quiz: Routing with React Router

**Q1. Which component wraps your entire app to enable client-side routing with the HTML5 History API?**
- [ ] `<Router>`
- [x] `<BrowserRouter>`
- [ ] `<HashRouter>`
- [ ] `<MemoryRouter>`

**Q2. In React Router v6, how do you define a route that renders `<UserProfile>` when the URL is `/users/42`?**
- [ ] `<Route url="/users/:id" render={<UserProfile />} />`
- [x] `<Route path="/users/:id" element={<UserProfile />} />`
- [ ] `<Route path="/users/:id" component={UserProfile} />`
- [ ] `<Route to="/users/:id"><UserProfile /></Route>`

**Q3. What hook gives you the dynamic segment value from a URL like `/users/42`?**
- [ ] `useLocation`
- [ ] `useNavigate`
- [x] `useParams`
- [ ] `useMatch`

**Q4. You want to redirect a user to `/login` if they are not authenticated. Which React Router hook do you use for programmatic navigation?**
- [ ] `useLocation`
- [ ] `useHistory`
- [x] `useNavigate`
- [ ] `useRedirect`

**Q5. What is the purpose of an "outlet" in React Router v6 nested routing?**
- [ ] It provides a fallback for 404 pages
- [x] It marks the position in a layout route where child routes are rendered
- [ ] It wraps routes with an error boundary
- [ ] It preloads the next route's data

**Q6. Which component renders an `<a>` tag that automatically gets an `active` class when its `to` path matches the current URL?**
- [ ] `<Link>`
- [ ] `<Anchor>`
- [x] `<NavLink>`
- [ ] `<ActiveLink>`

**Q7. A route that renders as a parent to group child routes and inject a shared layout is called a:**
- [ ] Index route
- [ ] Wildcard route
- [ ] Splat route
- [x] Layout route
