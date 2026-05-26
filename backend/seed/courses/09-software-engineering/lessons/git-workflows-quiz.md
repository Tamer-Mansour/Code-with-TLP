# Quiz: Branching Workflows and Semantic Versioning

**Q1. In GitFlow, which branch serves as the integration target for completed feature branches?**
- [ ] `main`
- [x] `develop`
- [ ] `release`
- [ ] `staging`

**Q2. Trunk-Based Development requires feature flags primarily because:**
- [ ] Feature flags speed up the CI pipeline
- [ ] Feature flags replace the need for unit tests
- [x] Incomplete features can be merged to the trunk without being visible to users, keeping the trunk always deployable
- [ ] Feature flags enable automatic rollback of deployments

**Q3. Given the current version `1.4.2`, which version should be released when a new optional parameter (with a default value) is added to a public API function?**
- [ ] `2.0.0`
- [x] `1.5.0`
- [ ] `1.4.3`
- [ ] `1.4.2-beta.1`

**Q4. In Semantic Versioning, when is the MAJOR version incremented?**
- [ ] When any new feature is added
- [ ] When a dependency is updated
- [x] When a backward-incompatible (breaking) change is made to the public API
- [ ] When a security vulnerability is patched

**Q5. The `^` prefix in an npm `package.json` dependency (e.g. `"express": "^4.18.2"`) means:**
- [ ] Install exactly version 4.18.2 and no other
- [ ] Install the latest version available regardless of major version
- [x] Install any compatible version >= 4.18.2 and < 5.0.0
- [ ] Install the latest patch release in the 4.x series only

**Q6. What is the main advantage of GitHub Flow over GitFlow for a team doing continuous deployment?**
- [ ] GitHub Flow supports multiple concurrent release versions
- [ ] GitHub Flow provides stricter access controls on the main branch
- [x] GitHub Flow has no `develop` branch and fewer ceremonies, making it faster to get code from a PR to production
- [ ] GitHub Flow requires fewer automated tests to be safe
