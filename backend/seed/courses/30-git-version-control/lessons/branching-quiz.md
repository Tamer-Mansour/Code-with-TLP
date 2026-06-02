# Quiz: Branching, Merging, and Rebasing

**Q1. What does `git merge --no-ff feature` always create, even when a fast-forward is possible?**
- [ ] A detached HEAD
- [x] A merge commit with two parents
- [ ] A new branch
- [ ] A tag pointing to the tip of feature

**Q2. After running `git rebase main` on a feature branch, the feature branch commits have:**
- [ ] The exact same SHA as before
- [x] New SHAs because their parent has changed
- [ ] Been deleted from the repository
- [ ] Been merged into main automatically

**Q3. Which command copies a single commit's diff onto the current branch as a new commit?**
- [ ] git merge
- [ ] git rebase
- [x] git cherry-pick
- [ ] git stash pop

**Q4. A "fast-forward" merge is only possible when:**
- [x] The current branch is a direct ancestor of the branch being merged in
- [ ] Both branches have the same number of commits
- [ ] There are no staged changes
- [ ] The remote and local are in sync

**Q5. What is the main risk of `git rebase` compared to `git merge`?**
- [ ] Rebase is slower than merge
- [ ] Rebase cannot handle conflicts
- [x] Rebasing rewrites commit SHAs, which breaks shared branch history
- [ ] Rebase deletes the source branch automatically

**Q6. You want to undo the last commit but keep the changes staged. Which command is correct?**
- [ ] `git reset --hard HEAD~1`
- [x] `git reset --soft HEAD~1`
- [ ] `git revert HEAD`
- [ ] `git restore --staged .`

**Q7. `git cherry-pick A..B` (two dots) applies commits:**
- [ ] From the beginning of history up to B
- [ ] A through B inclusive
- [x] After A up to and including B (A itself is excluded)
- [ ] Only commit A and commit B, skipping commits in between

**Q8. Which merge strategy produces the cleanest linear history?**
- [ ] Octopus merge
- [ ] Merge commit (--no-ff)
- [x] Rebase then fast-forward merge
- [ ] Squash merge onto main without rebasing
