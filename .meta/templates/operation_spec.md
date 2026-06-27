# Operation Spec: {{TITLE}}

> Template for a Controller operation docstring — `omt_agent_guide.md §10`.

```python
def {{operation}}(self, ...) -> ...:
    """
    Operation: <one-sentence description>.

    Preconditions:
      - <what must be true before the operation starts>

    Exceptions:
      - <error condition>: <how it is handled>

    Postconditions:
      - <what is guaranteed true after success>
    """
```
