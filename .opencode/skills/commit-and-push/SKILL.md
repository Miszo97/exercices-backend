---
name: commit-and-push
description: Stages all changes, writes a commit message from the diff, and pushes. Use when the user says "commit", "push", "commit and push", or similar.
---

# Commit and Push

Stage all changes, generate a descriptive commit message from the diff, commit, and push.

Steps:
1. Run `git add -A` to stage everything
2. Run `git diff --cached` and `git status` to review what's being committed
3. Write a concise commit message that describes the changes
4. Run `git commit -m "<message>"`
5. Run `git push`
