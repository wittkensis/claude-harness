# Scripts and Prototypes

## Python Scripts

```
Python 3.x + minimal deps (requests, pandas if needed)
```

- No virtual env if < 50 lines
- No git for throwaway tools
- No build tooling

```python
# Minimal script template
#!/usr/bin/env python3
import sys

def main():
    pass

if __name__ == '__main__':
    main()
```

## HTML Prototype

```
HTML + jQuery (CDN) + Tailwind (CDN)
```

- Single file, no build step
- For `/Concepts/` folder exploration
- No git unless it survives 1 week

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
</head>
<body class="bg-gray-50">
  <!-- Prototype content -->
  <script>
    $(function() {
      // Prototype logic
    });
  </script>
</body>
</html>
```

## Modular Python (quick data tools)

```python
# No virtual env if < 50 lines
# No git for throwaway
# Minimal dependencies
import json
import requests  # if needed
```

## Anti-Patterns

- Don't use frameworks for simple scripts
- Don't add git to throwaway tools
- Don't create virtual envs for < 50 line scripts
- Don't over-engineer prototypes — they're meant to be thrown away
