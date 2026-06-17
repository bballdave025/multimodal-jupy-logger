## First, comments from kamMA

1. **Yes.** A cell magic such as:

```python
%%jupy_log ...
```

must be the first **nonblank** line in the cell. Blank lines before it are tolerated; comments, `try:`, `if`, assignments, or other Python statements before it prevent IPython from recognizing the cell as a cell-magic invocation.

A cell magic owns the remainder of the cell as its body. It is not ordinary Python syntax, so this cannot work:

```python
try:
    %%jupy_log ...
```

Python’s parser sees `%%` inside a Python suite and rejects it before `try` can do anything.

2. **Yes.** Python parses and compiles the entire cell before executing its first statement. Therefore, an ordinary syntax error anywhere in that cell means **none of the cell runs**.

That is why this does not skip the invalid section:

```python
if do_skip_errors:
    raise SystemExit

%%jupy_log ...
```

The parser encounters invalid Python before execution begins, so it never reaches `raise SystemExit`.

Also, `if False:` does not help:

```python
if False:
    invalid Python here
```

Dead code must still be syntactically valid.

But commenting it out is **not** your only documentation option.

### Best options

Use a Markdown cell containing a fenced example:

````markdown
```python
%%jupy_log --label example --mime text/markdown
<details>
...
</details>
```
````

Or store the problematic source as a string:

```python
example_source = '''
%%jupy_log --label example --mime text/markdown
<details>
...
</details>
'''

print(example_source)
```

Or, if you specifically want to test and catch a syntax error, defer parsing with `compile()` or `exec()`:

```python
source = '''
try:
    %%jupy_log --label example
except Exception:
    pass
'''

try:
    compile(source, "<documented-example>", "exec")
except SyntaxError as ex:
    print(type(ex).__name__)
    print(ex)
##endof:  try/except
```

For programmatically invoking your actual cell magic from ordinary Python, use IPython’s API:

```python
body = '''
<details>
<summary>Click to reveal</summary>

Hidden text.

</details>
'''

get_ipython().run_cell_magic(
    "jupy_log",
    "--label details-test --mime text/markdown",
    body,
)
```

That call can live inside `if`, `try`, loops, or helper functions because it is ordinary valid Python.

One further detail from your notebook: `raise SystemExit(...)` exits execution only after parsing succeeds. It cannot protect a later syntax error in the same cell. And `except Exception` does not catch `SystemExit`, because `SystemExit` inherits directly from `BaseException`, not `Exception`.

---

## Second, some specifics of my learning-ish

# Jupyter Cell Magics Must Be First

**Date:** 2026-06-17
**Context:** MMJL capture and notebook-state smoke testing

## Observation

A Jupyter cell magic such as:

```python
%%jupy_capture
```

must be the first nonblank line in its cell. Comments or ordinary Python
statements before it prevent IPython from recognizing it as a cell magic.

This does not work:

```python
# Test capture
%%jupy_capture
print("hello")
```

Nor can a cell magic be placed inside ordinary Python control flow:

```python
try:
    %%jupy_capture
    print("hello")
except Exception:
    pass
```

## Why conditional skipping did not work

Python parses the entire cell before executing any statement. Therefore,
a syntax error later in the cell prevents earlier code from running.

This means neither:

```python
if False:
    invalid syntax
```

nor an early conditional exit can protect syntactically invalid code.
Code inside a branch that will never execute must still be valid Python.

## Practical conclusion

For ordinary notebook tests, place cell magics first:

```python
%%jupy_capture --label example
print("hello")
```

To preserve invalid or intentionally non-executable examples, use:

* a Markdown fenced-code block
* commented source
* a string containing the example
* `compile()` when deliberately testing parser behavior
* `get_ipython().run_cell_magic(...)` when invoking a cell magic from
  Python control flow

This discovery explains errors involving cell magics, comments, `try`
blocks, and attempted conditional skipping.
