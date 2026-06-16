Below is a complete notebook sequence. The intended execution order is the notebook’s ordinary top-to-bottom order:

```text
setup
hidden-note regression
reset state
A → B → C → B → A
inspect
export
inspect again
```

The second pass needs only **B → A**, because the first execution of C creates `numbers`.

## 1. Markdown cell — test purpose and execution order

````markdown
# MMJL Capture and Notebook-State Regression Test

This notebook tests:

1. repository-root discovery from anywhere inside the repository
2. `src/` import setup
3. MMJL utility imports
4. Jupyter magic registration
5. literal Markdown and HTML logging
6. `%%jupy_capture`
7. the `%%jupy_tee` alias
8. failed notebook-state execution in visible order:
   `A -> B -> C`
9. successful recovery by moving backward:
   `B -> A`
10. stdout, exception, rich-display, and Matplotlib capture
11. `%jupy_file`
12. manifest inspection and validation
13. Markdown and HTML timeline generation
14. the Python analogs of `tree`, `wc -l`, and `cat`

The notebook-state dependency graph is:

```text
C creates numbers
B consumes numbers and creates squared_numbers
A consumes numbers and squared_numbers, computes a mean, and plots
```

The cells are displayed as:

```text
A
B
C
B again
A again
```

Therefore the first A and B should fail, C should succeed, and the
subsequent B and A should succeed.
````

## 2. Code cell — locate the repository root and configure `sys.path`

```python
import importlib
import os
import sys
from pathlib import Path

starting_dir = Path.cwd().resolve()
repo_root = None
src_path = None
package_path = None

for candidate_path in [starting_dir, *starting_dir.parents]:
    package_path = (
        candidate_path
        / "src"
        / "multimodal_jupy_logger"
    )

    if package_path.is_dir():
        repo_root = candidate_path
        break
    ##endof:  if package_path.is_dir()
##endof:  for candidate_path in [...]

if repo_root is None:
    raise RuntimeError(
        "Could not find a repository root containing "
        "src/multimodal_jupy_logger."
    )
##endof:  if repo_root is None

src_path = repo_root / "src"

os.chdir(repo_root)

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
##endof:  if str(src_path) not in sys.path

importlib.invalidate_caches()

print("starting_dir:", starting_dir)
print("repo_root:", repo_root)
print("src_path:", src_path)
print("current working directory:", Path.cwd())
print("Python executable:", sys.executable)
```

## 3. Code cell — import MMJL and the path-display utilities

```python
from multimodal_jupy_logger import (
    MultimodalJupyLogger,
    jupy_logger_register,
    register_jupy_logger,
)

from multimodal_jupy_logger.utils import (
    count_lines,
    path_display,
    print_file,
    tree,
)

from multimodal_jupy_logger.utils import path_display as dpypd

print("MMJL imports succeeded.")
print("path_display module:", dpypd)
```

## 4. Code cell — prove both utility import styles work

```python
print("Directly imported function:")
print("  tree:", tree)

print("\nModule-namespace functions:")
print("  dpypd.tree:", dpypd.tree)
print("  dpypd.count_lines:", dpypd.count_lines)
print("  dpypd.print_file:", dpypd.print_file)

print("\nDirect and module attributes refer to the same functions:")
print("  tree is dpypd.tree:", tree is dpypd.tree)
print(
    "  count_lines is dpypd.count_lines:",
    count_lines is dpypd.count_lines,
)
print(
    "  print_file is dpypd.print_file:",
    print_file is dpypd.print_file,
)
```

## 5. Code cell — show the relevant repository tree

```python
dpypd.tree(
    this_dir=repo_root,
    dirs_to_exclude=[
        ".git",
        "__pycache__",
        ".venv",
        ".venv_test_mmjl",
        ".ipynb_checkpoints",
    ],
    files_to_exclude=[
        ".pyc",
    ],
)
```

## 6. Code cell — register the magics

Run this after restarting the kernel and loading the updated files.

```python
register_jupy_logger()
```

Expected registration text includes:

```text
%%jupy_log
%%jupy_capture
%%jupy_tee
```

## 7. Code cell — verify that the magics exist

```python
ipython_shell = get_ipython()

magic_names = [
    "jupy_save",
    "jupy_file",
    "jupy_log",
    "jupy_capture",
    "jupy_tee",
    "jupy_markdown",
    "jupy_html",
    "jupy_inspect",
    "jupy_validate",
]

for magic_name in magic_names:
    line_magic = ipython_shell.find_line_magic(magic_name)
    cell_magic = ipython_shell.find_cell_magic(magic_name)

    print(
        f"{magic_name:16s}",
        f"line={line_magic is not None}",
        f"cell={cell_magic is not None}",
    )
##endof:  for magic_name in magic_names
```

## 8. Markdown cell — notebook-native hidden-text control

This cell tests Jupyter’s own Markdown rendering independently of MMJL.

```markdown
## Notebook-native `<details>` control

<details>
<summary>Click the arrow to reveal the notebook-native text</summary>

This text lives directly in a Jupyter Markdown cell.

If clicking the arrow reveals this paragraph, the notebook frontend is
rendering the HTML element correctly.

</details>
```

## 9. Code cell — log the original Markdown regression case

This preserves the original test: raw `<details>` HTML stored with the
`text/markdown` MIME type.

```python
%%jupy_log --label details-summary-markdown-regression --mime text/markdown
<details>
<summary>Click the arrow to reveal logged Markdown text</summary>

This content was logged as `text/markdown`.

The regression question is whether exported timelines preserve this as
renderable Markdown/HTML or incorrectly turn it into escaped or fenced
source text.

</details>
```

## 10. Code cell — log an HTML control version

This distinguishes a general `<details>` failure from a Markdown-MIME
rendering-policy failure.

```python
%%jupy_log --label details-summary-html-control --mime text/html
<details>
<summary>Click the arrow to reveal logged HTML text</summary>

<p>
This content was logged as <code>text/html</code>. It should be inserted
as HTML in the generated HTML timeline.
</p>

</details>
```

With the current timeline builder, the expected distinction is:

* `text/html`: should render as a collapsible block in the HTML timeline
* `text/markdown`: currently may appear as escaped/fenced source

That would identify a timeline-rendering issue, not a capture failure.

## 11. Code cell — basic `%%jupy_capture` smoke test

```python
%%jupy_capture --label capture-basic
message = "This stdout should be displayed and logged."
print(message)

2 + 3
```

Expected capture roles include:

```text
input
stdout
display
```

The final expression `5` may be represented through one or more MIME
items, commonly including `text/plain`.

## 12. Code cell — basic `%%jupy_tee` alias test

```python
%%jupy_tee --label tee-basic
tee_message = "The %%jupy_tee alias executed this cell."
print(tee_message)

tee_message.upper()
```

## 13. Markdown cell — begin the notebook-state test

### 13.1 Doing this early, because I want to. Code cell.

```python
%matplotlib inline
```

### 13.2

````markdown
# A, B, C, then B, A

The next five capture cells must be run in their displayed order:

```text
A first
B first
C
B second
A second
```

Expected results:

```text
A first  -> NameError because squared_numbers does not exist
B first  -> NameError because numbers does not exist
C        -> creates numbers successfully
B second -> creates squared_numbers successfully
A second -> computes the mean and creates the plot successfully
```

The reset cell immediately below removes any old values that might make
the deliberately incorrect first pass appear to work.
````

## 14. Code cell — reset hidden kernel state

```python
%%jupy_capture --label abc-state-reset
state_names = [
    "numbers",
    "squared_numbers",
    "avg_value",
    "fig",
    "ax",
    "plot_source_path",
]

removed_names = []

for state_name in state_names:
    if state_name in globals():
        globals().pop(state_name)
        removed_names.append(state_name)
    ##endof:  if state_name in globals()
##endof:  for state_name in state_names

print("Removed prior state:", removed_names)
print("A and B should now fail on their first executions.")
```

## 15. Code cell — A, first execution: expected failure

```python
%%jupy_capture --label abc-first-pass-a
import matplotlib.pyplot as plt

avg_value = sum(squared_numbers) / len(squared_numbers)

fig, ax = plt.subplots(figsize=(8, 4))

ax.plot(
    numbers,
    squared_numbers,
    marker="o",
)

ax.axhline(
    avg_value,
    linestyle="--",
    label=f"mean squared value = {avg_value:.2f}",
)

ax.set_title(
    "Forwards-wrong / backwards-right notebook-state test"
)
ax.set_xlabel("number")
ax.set_ylabel("number squared")
ax.grid(True)
ax.legend()

plt.show()
```

Expected result:

```text
NameError involving squared_numbers
```

The capture should still log:

* the input
* the exception
* any output produced before the exception, if present

## 16. Code cell — B, first execution: expected failure

```python
%%jupy_capture --label abc-first-pass-b
squared_numbers = [
    number ** 2
    for number in numbers
]

print("squared_numbers:", squared_numbers)
```

Expected result:

```text
NameError involving numbers
```

## 17. Code cell — C: expected success

I added the imports and random numbers rather than arbitrary ones.

```python
%%jupy_capture --label abc-cell-c
import numpy as np
import matplotlib.pyplot as plt

# numbers = [
#     -5,
#     -3,
#     -1,
#     0,
#     2,
#     4,
#     6,
# ]

## Older global-random-state style, like MLU
# numbers = np.random.randint(1, 11, size=10)


rng = np.random.default_rng()
numbers = rng.integers(1, 11, size=10)

print("numbers:", numbers)
```

## 18. Code cell — B, second execution: expected success

```python
%%jupy_capture --label abc-second-pass-b
squared_numbers = [
    number ** 2
    for number in numbers
]

print("numbers:", numbers)
print(f"squared_numbers: {squared_numbers}")
```

## 19. ~~Code cell~~ — ~~configure Matplotlib inline rendering~~ 

### Note: trying this earlier, in 13.1

~~Run this before the successful A cell.~~

~~\`\`\``python`~~<br/>
~~`%matplotlib inline`~~<br/>
~~\`\`\`~~

## 20. Code cell — A, second execution: expected success and plot capture

```python
%%jupy_capture --label abc-second-pass-a
#done before#import matplotlib.plotly as plt
# P.S. kamMA's Jupyter must not need a numpy import?

avg_value = sum(squared_numbers) / len(squared_numbers)

fig, ax = plt.subplots(figsize=(8, 4))

ax.plot(
    numbers,
    squared_numbers,
    marker="o",
    label="squared values",
)

ax.axhline(
    avg_value,
    linestyle="--",
    label=f"mean squared value = {avg_value:.2f}",
)

ax.set_title(
    "Forwards-wrong / backwards-right notebook-state test"
)
ax.set_xlabel("number")
ax.set_ylabel("number squared")
ax.grid(True)
ax.legend()

plot_source_path = (
    repo_root
    / "jupy_log"
    / "staging"
    / "abc_backwards_right.png"
)

plot_source_path.parent.mkdir(
    parents=True,
    exist_ok=True,
)

fig.savefig(
    plot_source_path,
    dpi=150,
    bbox_inches="tight",
)

print("avg_value:", avg_value)
print("plot_source_path:", plot_source_path)

plt.show()
```

This tests two related but distinct things:

* inline PNG capture by `%%jupy_capture`
* creation of a file that `%jupy_file` can log explicitly

## 21. Code cell — test `%jupy_file` with the saved plot

```python
%jupy_file --label abc-explicit-plot --mime image/png jupy_log/staging/abc_backwards_right.png
```

The magic currently appends `-01` to the supplied label because it
supports logging multiple paths in one call.

## 22. Code cell — initial manifest inspection and validation

```python
%jupy_inspect

print("\n" + "-" * 72 + "\n")

%jupy_validate
```

## 23. Code cell — instantiate a direct logger for programmatic inspection

This logger points at the same root as the registered magics.

```python
log_root = repo_root / "jupy_log"
logger = MultimodalJupyLogger(root=log_root)

manifest_rows = logger.read_manifest_rows()

print("log_root:", log_root)
print("manifest:", logger.manifest)
print("artifact directory:", logger.artifacts)
print("manifest rows:", len(manifest_rows))
```

## 24. Code cell — inspect the most recent manifest rows

```python
recent_row_count = 20
recent_rows = manifest_rows[-recent_row_count:]

for row in recent_rows:
    print(
        row.get("artifact_sequence", ""),
        "capture=" + (row.get("capture_sequence", "") or "-"),
        "role=" + row.get("role", ""),
        "mime=" + row.get("mime", ""),
        "label=" + row.get("label", ""),
    )
##endof:  for row in recent_rows
```

Look for groups corresponding to:

```text
details-summary-markdown-regression
details-summary-html-control
capture-basic
tee-basic
abc-state-reset
abc-first-pass-a
abc-first-pass-b
abc-cell-c
abc-second-pass-b
abc-second-pass-a
abc-explicit-plot
```

## 25. Code cell — inspect the log tree with `dpypd.tree`

```python
dpypd.tree(
    this_dir=log_root,
    dirs_to_exclude=[
        "__pycache__",
    ],
    files_to_exclude=[
        ".pyc",
    ],
)
```

## 26. Code cell — use the `wc -l` analog

```python
manifest_line_count = dpypd.count_lines(
    logger.manifest,
    do_print=True,
)

print(
    "Expected manifest data rows:",
    manifest_line_count - 1,
)
print(
    "Rows returned by read_manifest_rows:",
    len(manifest_rows),
)
print(
    "Counts agree:",
    manifest_line_count - 1 == len(manifest_rows),
)
```

## 27. Code cell — use the `cat` analog on the manifest

```python
dpypd.print_file(
    logger.manifest,
    show_line_numbers=True,
)
```

Verify visually that:

* `artifact_sequence` increases monotonically
* capture artifacts share a `capture_sequence`
* the first failed A and B have exception rows
* the later B and A have successful output rows
* filenames contain both the sequence and epoch milliseconds

## 28. Code cell — generate both timelines

```python
markdown_timeline_path = logger.build_markdown()
html_timeline_path = logger.build_html()

print("Markdown timeline:", markdown_timeline_path)
print("HTML timeline:", html_timeline_path)
```

The equivalent magic calls are:

```python
%jupy_markdown
%jupy_html
```

Using the direct logger here makes the returned paths easy to retain.

## 29. Code cell — count timeline lines

```python
dpypd.count_lines(
    markdown_timeline_path,
    do_print=True,
)

dpypd.count_lines(
    html_timeline_path,
    do_print=True,
)
```

## 30. Code cell — print the Markdown timeline

```python
dpypd.print_file(
    markdown_timeline_path,
    show_line_numbers=False,
)
```

Things to check:

* artifact and capture sequences appear
* roles appear
* failed A and B occur before successful C, B, and A
* Python input is preserved
* exception text is preserved
* image links are present
* the Markdown `<details>` regression item is probably fenced rather than rendered

## 31. Code cell — inspect the raw HTML timeline source

This may be lengthy, but it is useful for this first pass.

```python
dpypd.print_file(
    html_timeline_path,
    show_line_numbers=True,
)
```

Search visually for:

```text
details-summary-markdown-regression
details-summary-html-control
abc-first-pass-a
abc-first-pass-b
abc-second-pass-a
image/png
```

## 32. Code cell — render the generated HTML timeline in the notebook

```python
from IPython.display import HTML, display

display(
    HTML(
        filename=str(html_timeline_path),
    )
)
```

Regression expectations:

* the `text/html` control should show a clickable `<details>` arrow
* the `text/markdown` version may show escaped `<details>` source
* the successful A plot should appear if its captured `image/png` path is
  usable from the generated timeline
* exception entries should be visible in chronological artifact order

## 33. Code cell — final validation after exports

```python
missing_paths = logger.validate_manifest()

print("\nFinal status:")
print("  manifest rows:", len(logger.read_manifest_rows()))
print("  missing artifact paths:", len(missing_paths))
print("  Markdown timeline exists:", markdown_timeline_path.exists())
print("  HTML timeline exists:", html_timeline_path.exists())
print("  explicit plot source exists:", plot_source_path.exists())
```

## 34. Code cell — final ordering assertions

```python
final_rows = logger.read_manifest_rows()

artifact_sequences = [
    int(row["artifact_sequence"])
    for row in final_rows
]

sequences_are_monotonic = (
    artifact_sequences
    == sorted(artifact_sequences)
)

sequences_are_unique = (
    len(artifact_sequences)
    == len(set(artifact_sequences))
)

filenames_have_sequence_prefixes = all(
    Path(row["path"]).name.startswith(
        f"{int(row['artifact_sequence']):06d}_"
    )
    for row in final_rows
)

print("Artifact sequences monotonic:", sequences_are_monotonic)
print("Artifact sequences unique:", sequences_are_unique)
print(
    "Filenames begin with artifact sequence:",
    filenames_have_sequence_prefixes,
)
```

## 35. Markdown cell — record the result

```markdown
# Test-result notes

Record the observations here:

- [ ] repository-root discovery worked
- [ ] imports worked
- [ ] utility module alias worked
- [ ] individual utility imports worked
- [ ] magics registered
- [ ] notebook-native `<details>` worked
- [ ] `text/markdown` regression behavior observed
- [ ] `text/html` control rendered
- [ ] `%%jupy_capture` executed and logged
- [ ] `%%jupy_tee` executed and logged
- [ ] first A failed as expected
- [ ] first B failed as expected
- [ ] C succeeded
- [ ] second B succeeded
- [ ] second A succeeded
- [ ] inline Matplotlib plot was captured
- [ ] explicit `%jupy_file` plot was logged
- [ ] manifest sequences were monotonic
- [ ] capture groups were visible
- [ ] filenames contained millisecond timestamps
- [ ] validation reported no missing artifacts
- [ ] Markdown timeline was generated
- [ ] HTML timeline was generated
- [ ] timeline execution history was reconstructable
```
