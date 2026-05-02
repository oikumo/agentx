To practice TDD in the true **Kent Beck style**, you have to shift your mindset: it’s not a testing technique—it’s a **design technique**. Beck’s philosophy is rooted in the mantra: *"Clean code that works."*

Here is a deep dive into the TDD "Skill" for Python, optimized for `uv` and aligned with Beck’s specific patterns.

---

## 1. The Core Philosophy: "The Goal is Courage"
In Beck's view, the primary bottleneck in software is **fear**. Fear of breaking things, fear of complexity, and fear of change. TDD provides a safety net that gives you the *courage* to refactor aggressively.

### The Two Rules
1.  **Never** write a single line of production code unless you have a failing automated test.
2.  **Eliminate duplication.** (Beck defines "clean code" as code that expresses all its ideas and contains no duplication).

---

## 2. Implementation Strategies: How to Move Fast
Beck identifies three main ways to get to "Green." In a `uv` project, these keep your feedback loop under one second.



### A. Fake It ('Til You Make It)
If you aren't sure how to implement the logic, return a hardcoded constant to get the test to green. This proves the test and the interface work.

*   **Test:** `assert add(1, 1) == 2`
*   **Production Code:** `def add(a, b): return 2`
*   **The Philosophy:** You shift the burden from "solving the problem" to "making the test pass." Once Green, you refactor the constant into a variable.

### B. Triangulation
When you are unsure of the correct abstraction, use **two or more** tests to force the generalization.
*   Test 1: `add(1, 1) == 2` (Code returns `2`)
*   Test 2: `add(1, 2) == 3` (Code is now forced to actually perform `a + b`)

### C. Obvious Implementation
If the solution is simple (like a basic getter or a trivial math operation), just write it. Don't waste time faking it if the "Green" path is immediate.

---

## 3. The "Dependency and Duplication" Loop
Beck’s TDD is a dance between **Dependency** and **Duplication**. 
*   **Dependency** is when a change here requires a change there.
*   **Duplication** is a symptom of dependency.

When you write a test like `assert calculate(5) == 10`, and then write code `def calculate(n): return 10`, there is **duplication** between the test and the code. You remove that duplication by changing the code to `return n * 2`.

---

## 4. High-Performance TDD with `uv`
To maintain the "Beck Rhythm," your environment must be invisible. 

### Instantaneous Test Runs
Use `uv` to keep your environment hermetic and fast. Use the `--looponfail` equivalent or a watcher to trigger on save:

```bash
# Install a watcher
uv add pytest-watch --dev

# Start the 'heartbeat'
uv run ptw
```

### Dependency Injection (The Beck Way)
Beck often favors simple objects. If you need to mock, keep it minimal. Use `uv` to manage `pytest-mock` if needed, but strive for "Plain Old Python Objects" (POPOs) first.

```python
# test_logic.py
def test_user_greeting():
    # Instead of complex mocks, use a simple 'Fake' object or Protocol
    class MockUser:
        name = "Kent"
    
    assert greet(MockUser()) == "Hello, Kent"
```

---

## 5. The "TDD Skill" Checklist
When implementing a feature, run through these Beck-inspired steps:
1.  **Pick a small story:** What is the smallest thing that could possibly work?
2.  **Write the test:** Express the intent, not the implementation.
3.  **Run with `uv run pytest`:** Confirm it fails (Red).
4.  **Quick Green:** Use "Fake It" or "Obvious Implementation."
5.  **Refactor:** Look at your code and your test. Is there duplication? Is the intent clear?
6.  **Repeat:** Smallest possible steps.

> "I'm not a great programmer; I'm just a good programmer with great habits." — Kent Beck

How complex is the feature you're looking to implement with this TDD workflow?