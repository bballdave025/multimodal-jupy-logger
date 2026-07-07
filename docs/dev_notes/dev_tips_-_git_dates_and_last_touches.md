# Dev Tip — Git Dates and "When Did I Work on This?"

Purpose: quick commands for finding exact commit dates, recent project activity, and file-specific history.

## Recent commits with exact dates

```bash
git log -5 --date=short --pretty=format:'%h  %ad  %s'
```

Shows the last 5 commits with:

- short hash
- date
- subject line

More detailed timestamp:

```bash
git log -5 --date=iso --pretty=format:'%h  %ad  %an  %s'
```

## Latest commit date only

```bash
git log -1 --date=short --pretty=format:'%ad'
```

Useful when trying to answer:

> What was the last date this repo was worked on?

## Recent commits with files changed

```bash
git log --stat --date=iso
```

Shows:

- exact commit timestamp
- author
- commit message
- changed files
- insertion/deletion counts

## History for one file

```bash
git log --follow -- path/to/file.md
```

`--follow` continues history across renames.

The standalone `--` means:

> no more command options; what follows is a path

This prevents filenames from being interpreted as command-line options.

Example:

```bash
git log --follow -- docs/dev_notes/PR_PLAN_bootstrap-package-structure.md
```

## One-line file history

```bash
git log --follow \
    --date=short \
    --pretty=format:'%h  %ad  %s' \
    -- path/to/file.md
```

## Show every change made to one file

```bash
git log -p --follow -- path/to/file.md
```

Displays each commit together with the patch affecting that file.

## Show the current version of a file at a past commit

```bash
git show <commit_hash>:path/to/file.md
```

Example:

```bash
git show a1b2c3d:docs/dev_notes/PR_PLAN_bootstrap-package-structure.md
```

Useful for recovering or comparing earlier versions without checking out an old commit.

## Find commits mentioning a word

```bash
git log --grep="NotebookBlock"
```

or

```bash
git log --grep="bootstrap" -i
```

The `-i` performs a case-insensitive search.

## Find commits that changed a particular string

```bash
git log -S "GlobalObservables"
```

This searches for commits where the number of occurrences of the string changed.

Very useful when trying to answer:

> "When did I first introduce this class/function?"

## GitHub web UI equivalent

For repository history:

1. Open the repository.
2. Switch to the desired branch.
3. Click **Commits** near the file list.

For a specific file:

1. Open the file.
2. Click **History**.

GitHub often displays relative dates ("2 months ago"). Opening the commit page provides the exact timestamp.

---

## Personal Note

The combination of:

```bash
git log --follow -- path/to/file.md
```

and

```bash
git show <commit_hash>:path/to/file.md
```

is particularly useful for project archaeology, reconstructing design evolution, recovering earlier implementations, and locating the latest work on long-lived design documents.
