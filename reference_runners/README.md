# Reference runner pattern

The working machines used small Python wrappers to assign actor-specific paths in imported `utils.defaults` modules before invoking Stage 2/3 or ContourCraft. This avoids repeatedly editing a shared repo, but exact attributes differ across dirty checkouts.

Use this pattern rather than copying an Actor05/08 runner verbatim:

```python
import os
from pathlib import Path

data_root = Path(os.environ["GG_DATA_ROOT"])
output_root = Path(os.environ["GG_OUTPUT_ROOT"])
assert data_root.is_dir()
output_root.mkdir(parents=True, exist_ok=True)

# Import the target entrypoint, assign its documented DEFAULTS/output root,
# then invoke its parser with explicit actor/sequence/template arguments.
# Print resolved paths and the source commit before starting work.
```

Do not embed paths, credentials, or checkpoint locations. Do not assume an Actor-specific filename such as `inference_actor05.py` is generic; that reuse was observed as technical debt.
