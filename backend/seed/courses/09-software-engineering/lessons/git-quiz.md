# Quiz: Version Control with Git

**Q1. What does `git add` do?**
- [ ] Creates a new commit
- [x] Moves changes from the working directory to the staging area
- [ ] Pushes changes to the remote repository
- [ ] Creates a new branch

**Q2. A fast-forward merge is possible when:**
- [ ] Both branches have diverged with new commits since the split
- [ ] There are merge conflicts to resolve
- [x] The target branch has not advanced since the feature branch was created
- [ ] The `--no-ff` flag is passed

**Q3. What is the "golden rule" of rebasing?**
- [ ] Always rebase before pushing to keep history linear
- [ ] Rebase is only safe for advanced users
- [ ] Never rebase after a merge conflict
- [x] Never rebase commits that have already been pushed to a shared remote branch

**Q4. In a merge conflict file, what does the section between `<<<<<<< HEAD` and `=======` contain?**
- [ ] The incoming branch changes
- [ ] The merged result
- [x] The changes from the current branch (HEAD)
- [ ] Git metadata about the conflict

**Q5. What command temporarily shelves uncommitted changes so you can switch branches cleanly?**
- [ ] `git save`
- [ ] `git hold`
- [x] `git stash`
- [ ] `git pause`

**Q6. In GitFlow, which branch type is used to apply an emergency fix directly to a released version?**
- [ ] `feature/`
- [ ] `release/`
- [x] `hotfix/`
- [ ] `bugfix/`
