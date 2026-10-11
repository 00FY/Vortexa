# Windows Console UTF-8 Encoding

When developing standalone CLI runner scripts or demo utilities in Python on Windows:
- Always configure `sys.stdout` to UTF-8 at the script entrypoint to avoid `UnicodeEncodeError` when emitting modern status symbols:
  ```python
  import sys
  if hasattr(sys.stdout, "reconfigure"):
      sys.stdout.reconfigure(encoding="utf-8")
  ```
