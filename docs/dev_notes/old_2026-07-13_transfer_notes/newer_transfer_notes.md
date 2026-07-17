# Add to instructions

========================================================================
CREATE VIRTUAL ENVIRONMENT
========================================================================

cd ~/multimodal-jupy-logger

python -m venv .venv

source .venv/bin/activate

python -m pip install --upgrade pip

python -m pip install -r requirements.txt


========================================================================
REGISTER JUPYTER KERNEL
========================================================================

python -m ipykernel install \
  --user \
  --name mmjl-sagemaker \
  --display-name "Python (MMJL SageMaker)"



# Ideas

Actually, I think there are good reasons **to** use a venv in SageMaker for MMJL.

The only reasons not to would be:

1. The MLU course instructions explicitly require a particular prebuilt kernel and warn against custom environments.
2. The SageMaker instance has storage quotas or lifecycle behavior that make extra environments expensive.
3. You want the absolute minimum setup friction for a one-hour experiment.

None of those seem to apply here.

For MMJL, I would probably do:

```text
~
├── multimodal-jupy-logger/
├── mlu-wjupy-lab/
└── .venvs/
    └── mmjl/
```

or equivalently:

```text
~
├── multimodal-jupy-logger/
│   └── .venv/
└── mlu-wjupy-lab/
```

I slightly prefer the latter because:

```text
MMJL source
MMJL environment
MMJL requirements
```

all live together.

Something like:

```bash
cd ~/multimodal-jupy-logger

python -m venv .venv

source .venv/bin/activate

pip install --upgrade pip

pip install -r requirements.txt
```

then:

```bash
python -m ipykernel install \
  --user \
  --name mmjl-sagemaker \
  --display-name "Python (MMJL SageMaker)"
```

Then every MLU notebook simply chooses:

```text
Python (MMJL SageMaker)
```

and uses:

```python
mmjl_src = (
    Path.home()
    / "multimodal-jupy-logger"
    / "src"
)
```

which is exactly your intended architecture.

The advantages are substantial:

```text
course image updates cannot break MMJL

MMJL upgrades cannot break course kernels

requirements.txt becomes authoritative

reproduction becomes easy

future contributors get deterministic behavior
```

In fact, this is probably even closer to the environment you are testing on Windows in Try 2:

```text
Windows:
repo
├── src
└── .venv_mmjl_try_2

SageMaker:
repo
├── src
└── .venv
```

Those are conceptually the same deployment.

One thing I would add to the instructions email is a new section:

```text
========================================================================
CREATE VIRTUAL ENVIRONMENT
========================================================================

cd ~/multimodal-jupy-logger

python -m venv .venv

source .venv/bin/activate

python -m pip install --upgrade pip

python -m pip install -r requirements.txt


========================================================================
REGISTER JUPYTER KERNEL
========================================================================

python -m ipykernel install \
  --user \
  --name mmjl-sagemaker \
  --display-name "Python (MMJL SageMaker)"
```

Then the workflow becomes:

```text
activate venv
launch Jupyter
select MMJL kernel
run notebook
```

That's about as boring and reproducible as Python gets, which is exactly where infrastructure projects want to live.

One final practical note: before committing to this, it may be worth checking whether your SageMaker environment permits arbitrary `venv` creation and custom kernelspec registration. Most SageMaker Studio environments do, but some managed enterprise images restrict parts of that workflow. If MLU notebooks are already running in user-managed spaces—and your screenshot suggests they are—I'd expect this to work without issue.

If it works, I'd make the venv approach the official recommendation rather than the optional one.

## contents of requirements.txt

```text
jupyterlab
ipykernel
ipywidgets

numpy
scipy
pandas>=2.0.0,<3.0.0
scikit-learn
matplotlib
pillow
imageio

nbformat
nbconvert[webpdf]
traitlets
```

--------------------------------------------------------------------------

--------------------------------------------------------------------------

--------------------------------------------------------------------------

# Never mind.

# Message by Dave

What do I do about packages necessary for notebooks from which I'm taking notes. For example, suppose sklearn were necessary for a lesson notebook, and I had MMJL logging set up.

# Message by kamMA

The selected notebook kernel must contain **both**:

1. everything the lesson notebook needs, and
2. everything MMJL needs.

So if the lesson imports:

```python
import sklearn
```

then the environment behind the selected kernel needs `scikit-learn` installed.

## Best practical model

Do not think of it as an “MMJL-only environment.” Think of it as:

```text
course environment
+ MMJL
= notebook kernel
```

For example:

```bash
cd ~/multimodal-jupy-logger

python -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip

python -m pip install \
  jupyterlab \
  ipykernel \
  matplotlib \
  nbformat \
  nbconvert \
  scikit-learn
```

Then register that environment:

```bash
python -m ipykernel install \
  --user \
  --name mmjl-sagemaker \
  --display-name "Python (MLU + MMJL)"
```

The display name should probably reflect that combined purpose:

```text
Python (MLU + MMJL)
```

rather than implying it contains only MMJL.

## When the course has requirements

The better version is:

```bash
python -m pip install \
  -r ~/mlu-wjupy-lab/requirements.txt
```

followed by any MMJL-specific requirements:

```bash
python -m pip install \
  ipykernel \
  nbformat \
  nbconvert
```

MMJL itself does not need to be installed as a package because the setup cell
adds its `src` directory to `sys.path`.

Conceptually:

```text
course requirements
        +
MMJL runtime requirements
        ↓
one combined kernel
```

## Important package-name detail

The installation name is:

```bash
python -m pip install scikit-learn
```

The Python import is:

```python
import sklearn
```

## What about SageMaker’s existing course kernel?

There are two viable approaches.

### Approach A — Use the supplied course environment

Select the existing MLU kernel and add only the MMJL source path:

```python
mmjl_src = (
    Path.home()
    / "multimodal-jupy-logger"
    / "src"
)
```

This is the least disruptive option when the course kernel already has all
the specialized packages.

You would only need to confirm that it also has MMJL’s modest dependencies,
such as IPython and the notebook libraries.

### Approach B — Create a combined environment

Create a new venv, install the course dependencies into it, add the MMJL
dependencies, and select that combined kernel.

This is more reproducible, but potentially more setup work.

## My recommendation for your MLU work

Start with the **existing MLU kernel** because it was built to run the course
notebooks. Test whether MMJL imports and registers there.

In the notebook:

```python
import sys

print(sys.executable)
```

Then test:

```python
import sklearn
import matplotlib
import nbformat
import IPython

print("Course and MMJL dependencies are available.")
```

If that succeeds, simply add MMJL through `sys.path`. There is no need to
rebuild the entire course environment.

Create a dedicated combined venv only if:

* the existing course kernel is missing MMJL dependencies,
* you cannot safely add the missing packages,
* or you need a reproducible environment independent of the managed image.

The governing rule is:

> Choose the environment that can already run the lesson, then add MMJL to
> that environment—not the other way around.

# Message by Dave

I have no way of seeing which requirements each notebook may have, because they come pre-provisioned. Okay, I have a way, and that's to look at every single import. Since the note-taking is an addition, perhaps the requirements should just be added onto whatever kernel already exists and will be used in the course Jupyter notebooks. How do I find this out?

# Message by kamMA, IMPORTANT

Yes—because the course notebooks are already provisioned and presumably already run under a working SageMaker kernel, the cleanest policy is:

> Start with the course’s existing kernel, then add only MMJL’s missing runtime dependencies to that exact kernel.

You do **not** need to reverse-engineer every lesson import first.

## 1. Open an actual course notebook

Use the kernel the course notebook already selects by default.

Before changing anything, run this temporary diagnostic cell:

```python
import sys
import site
from pathlib import Path

print("Python executable:")
print(sys.executable)

print("\nPython version:")
print(sys.version)

print("\nCurrent working directory:")
print(Path.cwd())

print("\nSite-package directories:")
for package_dir in site.getsitepackages():
    print(package_dir)
##endof:  for package_dir in site.getsitepackages()
```

The most important output is `sys.executable`.

It may resemble:

```text
/opt/conda/bin/python
```

or:

```text
/home/sagemaker-user/.conda/envs/some-course-env/bin/python
```

That tells you exactly which Python environment backs the selected notebook
kernel.

## 2. Record the kernel identity

In another cell:

```python
from IPython import get_ipython

ipython_shell = get_ipython()

print("Kernel implementation:")
print(type(ipython_shell).__name__)

print("\nKernel display information:")
print(ipython_shell.kernel)
```

The JupyterLab kernel picker will usually give the more human-readable name,
but `sys.executable` is the authoritative answer about the environment.

## 3. Check MMJL’s required imports

Do not install yet. First see what is missing:

```python
import importlib.util

required_modules = {
    "IPython": "ipython",
    "nbformat": "nbformat",
    "nbconvert": "nbconvert",
    "matplotlib": "matplotlib",
}

missing_packages = []

for module_name, package_name in required_modules.items():
    module_spec = importlib.util.find_spec(module_name)

    if module_spec is None:
        print(f"[MISSING] {module_name}")
        missing_packages.append(package_name)
    else:
        print(f"[FOUND]   {module_name}")
    ##endof:  if module_spec is None
##endof:  for module_name, package_name in required_modules.items()

print("\nPackages needing installation:")
print(missing_packages)
```

For the core MMJL logger, you may discover that everything is already there.

PDF export can remain optional. It may require more than the core logger does.

## 4. Add only the missing packages to the current course kernel

Inside a notebook, use `%pip`, not bare `pip` through `subprocess`.

For example:

```python
%pip install nbformat nbconvert
```

IPython’s `%pip` magic installs into the environment associated with the
currently running kernel. That is the critical property here.

After installation, restart the kernel:

```text
Kernel → Restart Kernel
```

Then rerun the import checks.

### Why `%pip` is appropriate here

This is a different situation from embedding automatic installation into the
portable smoke-test notebook.

You are manually performing a one-time environment setup step while looking
directly at the course kernel. That is reasonable.

The distinction is:

```text
Bad:
  notebook silently installs packages every time it runs

Good:
  user explicitly inspects the selected course kernel
  user explicitly installs missing MMJL dependencies once
  notebook thereafter only imports and uses MMJL
```

## 5. Confirm `%pip` targets the same Python

Before installing, you can verify:

```python
import sys

print(sys.executable)
```

Then:

```python
%pip --version
```

The path printed by `%pip --version` should correspond to the same environment
as `sys.executable`.

For even more explicit installation, use:

```python
import sys

!{sys.executable} -m pip --version
```

and, when needed:

```python
import sys

!{sys.executable} -m pip install nbformat nbconvert
```

I prefer `%pip` in Jupyter, but both approaches deliberately target the
current kernel interpreter.

## 6. Test course functionality before and after

Before adding anything, run one small existing lesson cell that uses a course
dependency, perhaps:

```python
import sklearn
import numpy
import pandas
import matplotlib

print("Course imports still work.")
```

After installing the MMJL dependencies and restarting the kernel, rerun that
same check.

Then test MMJL:

```python
from pathlib import Path
import importlib
import sys

mmjl_src = (
    Path.home()
    / "multimodal-jupy-logger"
    / "src"
)

if str(mmjl_src) not in sys.path:
    sys.path.insert(0, str(mmjl_src))
##endof:  if str(mmjl_src) not in sys.path

importlib.invalidate_caches()

from multimodal_jupy_logger import register_jupy_logger

print("MMJL import passed.")
```

If both the course imports and MMJL import pass, you have the desired combined
environment without reconstructing the course environment yourself.

## 7. Registering another kernel is probably unnecessary

Because you are augmenting the existing course kernel, you normally should
not register a new kernel.

The existing notebook already knows which kernel to use. You are adding
dependencies to that environment, not creating a replacement.

The practical workflow becomes:

```text
open course notebook
→ retain its existing kernel
→ inspect sys.executable
→ check MMJL imports
→ install only missing MMJL packages with %pip
→ restart kernel
→ rerun course import check
→ add MMJL source path
→ begin logging
```

## 8. Check whether changes persist

SageMaker environments vary in how persistent their files and package
installations are.

After installing and restarting:

```python
import nbformat
import sys

print(sys.executable)
print(nbformat.__version__)
```

Then close and reopen the Jupyter space later and run the same cell.

If the package remains, setup was persistent.

If it disappears after the space or image restarts, keep a small manual setup
cell or shell note such as:

```python
%pip install nbformat nbconvert
```

but do not run it automatically on every notebook execution.

## 9. Minimal dependency stance for the PR

For the current PR, first try only the core logger requirements. A likely
check is:

```python
import IPython
import matplotlib

print("Core notebook dependencies available.")
```

Then test MMJL import through the copied source.

Only add:

```text
nbformat
nbconvert
```

when testing or using the PDF/notebook-file transformation module.

That protects the course environment from unnecessary changes while keeping
PDF optional, exactly as intended for this PR.

The guiding rule is now:

> Preserve the provisioned lesson kernel, inspect it, and add the smallest
> missing MMJL layer to it.

# Message by Dave

Well, the nice thing is that every course environment gets reset when a student starts (or restarts) a course.

# Message by kamMA

That makes the “augment the existing course kernel” approach even better.

Because each course restart restores a clean provisioned environment:

* you cannot permanently poison the course setup,
* any MMJL dependency additions are naturally temporary,
* you do not need to maintain a separate replica of every course environment,
* and the reset itself becomes your rollback mechanism.

The practical pattern becomes:

```text
start or restart course
→ use its default kernel
→ run a small MMJL dependency check
→ install only what is missing
→ restart kernel if required
→ add MMJL src path
→ begin logging
```

That is preferable to a dedicated MMJL venv for actual course work, because the course kernel already contains whatever specialized packages that lesson needs.

I would therefore separate the roles:

```text
Try 2 / development testing:
  clean independent venv
  full requirements.txt
  reproducibility test

Actual SageMaker MLU use:
  provisioned course kernel
  minimal MMJL dependency additions
  source loaded from ~/multimodal-jupy-logger/src
```

A small manual setup cell could check availability without installing automatically:

```python
import importlib.util
import sys

required_modules = {
    "IPython": "ipython",
    "matplotlib": "matplotlib",
}

optional_pdf_modules = {
    "nbformat": "nbformat",
    "nbconvert": "nbconvert",
}

for module_name, package_name in required_modules.items():
    found = importlib.util.find_spec(module_name) is not None

    print(
        "[FOUND]" if found else "[MISSING]",
        module_name,
        f"(pip package: {package_name})",
    )
##endof:  for module_name, package_name in required_modules.items()

print("\nPython:", sys.executable)
```

Then you explicitly run `%pip install ...` only when something is missing.

This also means the setup email should probably contain two distinct routes:

```text
Route A — smoke-test/reproducibility environment
  create venv
  install requirements.txt
  register kernel

Route B — real course usage
  keep provisioned course kernel
  check MMJL dependencies
  install only missing packages with %pip
  restart kernel
  add MMJL source path
```

That split matches your actual use much better than trying to force one environment strategy onto both development validation and day-to-day course work.

---

---

## Remember, from `requirements.txt`

```text
jupyterlab
ipykernel
ipywidgets

numpy
scipy
pandas>=2.0.0,<3.0.0
scikit-learn
matplotlib
pillow
imageio

nbformat
nbconvert[webpdf]
traitlets
```

## Probably Not (at least for AWS SageMaker, but yes for everywhere else

Run once for a new MMJL virtual environment:

```powershell
python -m ipykernel install --user --name mmjl-test --display-name "Python (MMJL test)"
```

Verify registration:

```powershell
jupyter kernelspec list
```

Then select:

```text
Python (MMJL test)
```

inside JupyterLab.

This step only needs to be repeated if:

* a new venv is created,
* the old venv is deleted,
* or the kernelspec is manually removed.
