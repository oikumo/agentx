# Design {{NUM}}: {{TITLE}}

> **Phase:** Design — `omt_agent_guide.md §2`, §5–§10 | **Feature:** {{SLUG}}

## Components / screens affected
<!-- Which MVC++ triads (Model/View/Controller) change or get created? -->

## Static structure (classes & files)
| File | Layer | Responsibility |
|------|-------|----------------|
| `ui/screens/<screen>/<screen>_controller.py` | Controller | |
| `ui/screens/<screen>/<screen>_view.py` | View (+ `I<Screen>ViewPartner` ABC) | |
| `model/<entity>/<entity>.py` | Model | |
| `model/<entity>/<entity>_db.py` | DP class (all SQL) | |

## Abstract Partner interface
```python
class I{{TITLE}}ViewPartner(ABC):
    @abstractmethod
    def on_user_input(self, user_input: str) -> None: ...
```

## Functional flow (sequence)
```
User → View.capture_input() → partner.on_user_input()
     → Controller.<operation>() → Model / View.render()
```

## Operation specifications
<!-- One per new Controller method, per §10 (pre/exceptions/post). -->

## MVC++ self-check
- [ ] View does not import Model
- [ ] Model does not import ui
- [ ] Abstract Partner is an `ABC` with `@abstractmethod`
- [ ] SQL only in `*_db.py` / `DP_*`
- [ ] No `*Controller` under `model/`
- [ ] `uv run scripts/omt/mvc_check.py` passes for touched files
