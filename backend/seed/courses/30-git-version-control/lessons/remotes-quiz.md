# Quiz: Remotes and Collaboration

**Q1. What is the difference between `git fetch` and `git pull`?**
- [ ] They are identical; `fetch` is just an older alias for `pull`
- [x] `git fetch` downloads remote changes into remote-tracking branches without touching your working branch; `git pull` fetches AND then merges (or rebases)
- [ ] `git fetch` also updates your local branch; `git pull` only downloads
- [ ] `git fetch` requires authentication; `git pull` does not

**Q2. After running `git fetch origin`, the downloaded commits are stored in:**
- [ ] Your local `main` branch immediately
- [ ] The staging area
- [x] Remote-tracking branches like `origin/main`, which you review before merging
- [ ] A temporary stash

**Q3. What does `origin` refer to in a typical Git workflow?**
- [ ] The first commit in the repository
- [ ] The branch you cloned from
- [x] The default alias for the remote repository URL you cloned from
- [ ] The HEAD of the remote

**Q4. You want to push your local `feature` branch to the remote for the first time. Which command sets up tracking automatically?**
- [ ] `git push feature`
- [ ] `git push --track origin feature`
- [x] `git push -u origin feature`
- [ ] `git remote add feature`

**Q5. A "pull request" (PR) is:**
- [ ] A Git command that pulls changes from a specific user
- [x] A GitHub/GitLab feature (not a Git command) that proposes merging one branch into another and triggers a code review
- [ ] Another name for `git fetch`
- [ ] A request sent to your team to run `git pull`

**Q6. When you fork a repository on GitHub, you:**
- [ ] Create a branch on the original repository
- [ ] Download the repository to your local machine
- [x] Create your own copy of the repository under your account, which you can push to freely
- [ ] Get write access to the original repository

**Q7. `git push --force-with-lease` is safer than `git push --force` because:**
- [ ] It compresses the pushed data
- [ ] It only works on private repositories
- [x] It refuses to overwrite the remote if someone else has pushed since your last fetch, preventing accidental data loss
- [ ] It automatically creates a backup branch before pushing
