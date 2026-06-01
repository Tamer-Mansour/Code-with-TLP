# Quiz: Git Basics

**Q1. A Git branch is, internally:**
- [ ] A copy of the entire codebase
- [x] A file containing the SHA of one commit
- [ ] A snapshot of staged changes
- [ ] A diff against main

**Q2. Each commit object stores:**
- [ ] Only a diff vs its parent
- [x] A pointer to a full tree (snapshot), plus parent SHA(s) and metadata
- [ ] The author, date, and an inline patch
- [ ] A reference to a remote

**Q3. The staging area is also called:**
- [ ] HEAD
- [ ] reflog
- [x] index
- [ ] stash

**Q4. To undo a commit that's already pushed publicly you should:**
- [ ] `git reset --hard` and force-push
- [ ] Manually delete it from the remote
- [x] `git revert <sha>` and push the new commit
- [ ] `git commit --amend`

**Q5. `git pull --rebase` does:**
- [ ] Reset your local branch to the remote
- [x] Fetches the remote, then rebases your local commits onto it (no merge commit)
- [ ] Merges blindly
- [ ] Resets the remote to your local

**Q6. To save uncommitted work without committing, use:**
- [ ] `git revert`
- [ ] `git reset`
- [x] `git stash`
- [ ] `git cherry-pick`
