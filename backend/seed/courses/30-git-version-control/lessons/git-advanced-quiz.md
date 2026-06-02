# Quiz: Advanced Git and Team Workflows

**Q1. What does `git bisect run <script>` do?**
- [ ] Runs the script once on HEAD and reports the result
- [x] Automatically marks commits good/bad by running the script at each bisect step
- [ ] Creates a new branch for each bisect step
- [ ] Executes the script only on the first bad commit found

**Q2. The reflog expires entries after (default):**
- [ ] 7 days
- [ ] 30 days
- [x] 90 days for reachable commits
- [ ] It never expires

**Q3. Which git hook runs BEFORE you type a commit message and can abort the commit?**
- [x] pre-commit
- [ ] post-commit
- [ ] commit-msg
- [ ] prepare-commit-msg

**Q4. In trunk-based development, unfinished features are hidden using:**
- [ ] Long-lived feature branches
- [ ] Draft pull requests
- [x] Feature flags (feature toggles)
- [ ] Stash entries

**Q5. `git fetch --prune` does what?**
- [ ] Deletes all local branches
- [ ] Removes old git objects to save disk space
- [x] Deletes remote-tracking refs for branches deleted on the remote
- [ ] Removes all stash entries

**Q6. After a bad `git rebase`, what is the fastest way to return to the pre-rebase state?**
- [x] `git reset --hard HEAD@{N}` using the reflog to find the pre-rebase SHA
- [ ] `git rebase --abort` (only works while the rebase is in progress)
- [ ] Re-clone the repository
- [ ] `git revert HEAD`

**Q7. Which annotated tag command is correct?**
- [ ] `git tag v1.0.0`
- [x] `git tag -a v1.0.0 -m "First release"`
- [ ] `git tag --annotate v1.0.0`
- [ ] `git commit --tag v1.0.0`

**Q8. In GitHub Flow, when should you open a pull request?**
- [ ] Only when all features are complete and tests pass
- [ ] After at least one week of work on the branch
- [x] As early as possible — even as a draft to signal work in progress
- [ ] Only after getting approval from a senior developer

**Q9. `git cherry-pick -x <sha>` adds what to the commit message?**
- [ ] The author of the original commit
- [ ] A `Signed-off-by` line
- [x] A line saying `(cherry picked from commit <sha>)`
- [ ] The branch name the commit came from

**Q10. The `core.hooksPath` config setting is useful because:**
- [ ] It makes hooks run faster
- [ ] It disables the default `.git/hooks/` directory
- [x] It points Git to a tracked directory so hooks can be shared via version control
- [ ] It sets the timeout for hook execution
