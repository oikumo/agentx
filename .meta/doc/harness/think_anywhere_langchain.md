# THINK-ANYWHERE — Theory & LangChain Implementation

---

## Core Theory

### The Problem with Upfront Thinking

Standard LLMs reason *before* generating code:

```
P(c, s | x) = P(s | x) · P(c | x, s)
              ^^^^^^^^^^^   ^^^^^^^^^^^^
              reason first  then code
```

This forces the model to anticipate *all* implementation complexity upfront — before seeing how the code unfolds. This leads to bugs caused by issues that only appear mid-implementation.

### THINK-ANYWHERE: Inline On-Demand Reasoning

The model produces a mixed sequence `y` of code segments and inline thinking blocks:

```
y = ( s,  c(1), h(1), c(2), h(2), ..., c(M), h(M), c(M+1) )
     ^^^  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  upfront        interleaved code + thinking blocks
  <think>             <thinkanywhere> blocks
```

Formal probability factorization:

```
P(y | x) = P(s | x) · ∏ᵢ [ P(c(i) | x, y<c(i)) · P(h(i) | x, y<h(i)) ] · P(c(M+1) | ...)
```

The number `M` and positions of `h(i)` blocks are chosen *dynamically* by the model.

**Final executable code** = strip all thinking blocks:
```
c = c(1) ⊕ c(2) ⊕ ... ⊕ c(M+1)
```

### Key Insight: High-Entropy Position Targeting

The model learns to invoke `<thinkanywhere>` at positions of *high token entropy* — where it is most uncertain. Most common targets:

| Rank | Syntax Type | Why |
|---|---|---|
| 1 | Assignment | Complex computation / state updates |
| 2 | Return | Final output correctness check |
| 3 | Expression | Expression complexity |
| 4 | If | Conditional branching logic |
| 5 | AugAssign | Accumulator updates |

### Training Recipe (Two Stages)

**Stage 1 — Cold-Start SFT (LoRA):**
- Prompt a strong LLM (e.g., Gemini 2.5 Flash) to generate `<thinkanywhere>` annotated code solutions
- Filter malformed outputs; keep ~5,000 samples
- Fine-tune with LoRA to teach the *pattern*

**Stage 2 — RLVR (GRPO):**
- Reward: `R(y) = 0.1 · R_struct + 0.9 · R_correct`
  - `R_struct = 1` if output has both `<think>` and at least one `<thinkanywhere>` block
  - `R_correct = 1` if generated code passes all test cases
- GRPO advantage: `Â_i = (R(yᵢ) - mean(R)) / std(R)` — no value model needed
- This teaches the model *where* to think, not just *that* it can think

---

## LangChain Implementation

### 1. Dependencies

```bash
pip install langchain langchain-openai langchain-core
```

### 2. Prompt Template

```python
from langchain_core.prompts import ChatPromptTemplate

SYSTEM_PROMPT = """You are a coding assistant that generates both code and inline self-guidance signals.
First output <think>...</think> with brief reasoning, then output the final code.

MUST FOLLOW Rules for <thinkanywhere>...</thinkanywhere> tags:
1. You MUST use <thinkanywhere>...</thinkanywhere> tags for self-guidance or intermediate reasoning.
2. <thinkanywhere>...</thinkanywhere> MUST be embedded within an existing program statement token sequence.
3. The code must remain valid and executable after removing all <thinkanywhere>...</thinkanywhere> segments."""

think_anywhere_prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{problem}"),
])
```

### 3. Output Parser

```python
import re
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from dataclasses import dataclass

@dataclass
class ThinkAnywhereOutput:
    raw: str                    # full model output
    upfront_thinking: str       # content inside <think>...</think>
    inline_blocks: list[str]    # list of <thinkanywhere> contents, in order
    executable_code: str        # code with all thinking blocks stripped


def parse_think_anywhere(raw: str) -> ThinkAnywhereOutput:
    # Extract upfront <think> block
    upfront_match = re.search(r"<think>(.*?)</think>", raw, re.DOTALL)
    upfront_thinking = upfront_match.group(1).strip() if upfront_match else ""

    # Extract all inline <thinkanywhere> blocks
    inline_blocks = re.findall(r"<thinkanywhere>(.*?)</thinkanywhere>", raw, re.DOTALL)
    inline_blocks = [b.strip() for b in inline_blocks]

    # Build executable code: strip <think> block, then strip all <thinkanywhere> blocks
    code = raw
    code = re.sub(r"<think>.*?</think>", "", code, flags=re.DOTALL)
    code = re.sub(r"<thinkanywhere>.*?</thinkanywhere>", "", code, flags=re.DOTALL)
    code = code.strip()

    return ThinkAnywhereOutput(
        raw=raw,
        upfront_thinking=upfront_thinking,
        inline_blocks=inline_blocks,
        executable_code=code,
    )


think_anywhere_parser = StrOutputParser() | RunnableLambda(parse_think_anywhere)
```

> ⚠️ **Stripping safety (F13):** removing a `<thinkanywhere>` block that sits *mid-statement* can silently merge tokens and change semantics — `x = fo<thinkanywhere>…</thinkanywhere>o(1)` strips to `x = oo(1)`. The prompt rules require blocks embedded on token boundaries, but always syntax-check the stripped code before use:

```python
def assert_strip_safe(output: ThinkAnywhereOutput) -> ThinkAnywhereOutput:
    """Fail fast if block-stripping produced unparseable code."""
    compile(output.executable_code, "<string>", "exec")  # raises SyntaxError
    return output
```

> Syntax validity does not prove semantics were preserved — prefer checkpoints trained to place blocks at boundaries, and keep the `validate_code` check from §9 in the pipeline.

### 4. Chain Assembly

```python
from langchain_openai import ChatOpenAI

# Any model capable of instruction-following works here.
# For best results, use a fine-tuned THINK-ANYWHERE checkpoint.
llm = ChatOpenAI(
    model="gpt-4o",       # swap for your fine-tuned model endpoint
    temperature=0,        # greedy sampling, as in the paper
    max_tokens=4096,
)

think_anywhere_chain = think_anywhere_prompt | llm | think_anywhere_parser
```

### 5. Running the Chain

```python
result = think_anywhere_chain.invoke({
    "problem": (
        "Given two strings word1 and word2, return the minimum number of operations "
        "required to convert word1 to word2. You can perform: insert, delete, or replace."
    )
})

print("=== Upfront Thinking ===")
print(result.upfront_thinking)

print(f"\n=== Inline Thinking Blocks ({len(result.inline_blocks)}) ===")
for i, block in enumerate(result.inline_blocks):
    print(f"[{i+1}] {block}")

print("\n=== Executable Code ===")
print(result.executable_code)
```

### 6. Streaming Version

```python
# For live streaming with deferred parsing, stream the LLM directly:
raw_chain = think_anywhere_prompt | llm | StrOutputParser()

async def stream_raw_then_parse(problem: str) -> ThinkAnywhereOutput:
    raw = ""
    async for token in raw_chain.astream({"problem": problem}):
        print(token, end="", flush=True)
        raw += token
    print()
    return parse_think_anywhere(raw)
```

### 7. Batch Evaluation (pass@k)

pass@k is the probability that **at least one of k samples** passes, estimated from
`n ≥ k` samples with the unbiased estimator (Chen et al. 2021):
`pass@k = 1 − C(n−c, k) / C(n, k)` where `c` = number of passing samples.
(A naive passed-over-k ratio is **not** pass@k — it is the per-sample pass rate.)

```python
import math
from langchain_openai import ChatOpenAI

def build_sampler(temperature: float = 0.8) -> ChatOpenAI:
    """For pass@k, sample with temperature > 0."""
    return ChatOpenAI(model="gpt-4o", temperature=temperature, max_tokens=4096)

async def pass_at_k(problem: str, n: int = 20, k: int = 5, test_fn=None) -> dict:
    """
    Unbiased pass@k: sample n >= k solutions, c passing, then
        pass@k = 1 - C(n - c, k) / C(n, k)
    With n = k the estimator degenerates to "at least one sample passed"
    (0/1, high variance) — use n >= 2k (e.g. n=20, k=5).
    test_fn(code: str) -> bool
    """
    if n < k:
        raise ValueError(f"pass@k needs n >= k (got n={n}, k={k})")
    sampler = build_sampler(temperature=0.8)
    sample_chain = think_anywhere_prompt | sampler | think_anywhere_parser

    import asyncio
    tasks = [sample_chain.ainvoke({"problem": problem}) for _ in range(n)]
    results: list[ThinkAnywhereOutput] = await asyncio.gather(*tasks)

    passed = sum(1 for r in results if test_fn and test_fn(r.executable_code))
    estimate = 1.0 - math.comb(n - passed, k) / math.comb(n, k)
    return {
        "pass_at_k": estimate,
        "n": n,
        "k": k,
        "passed": passed,
        "solutions": [r.executable_code for r in results],
        "thinking_counts": [len(r.inline_blocks) for r in results],
    }
```

> ⚠️ **Sandbox warning:** `test_fn` executes model-generated code. Run evaluations
> inside a container/VM with no secrets, no network access, and CPU/memory/time
> limits — never directly on a host you care about.

### 8. Entropy-Aware Position Analysis (Optional Diagnostic)

Replicate the paper's "Thinking Position Analysis" to inspect where your model invokes thinking.
Each block is attributed to a syntactic context by parsing the code prefix that precedes it
in the **raw** output (the stripped code alone cannot reveal block positions):

```python
import ast
import re
from collections import Counter

def analyze_thinking_positions(result: ThinkAnywhereOutput) -> dict:
    """
    Attribute each <thinkanywhere> block to the type of the statement whose
    region the block was emitted after, by parsing the code prefix preceding
    the block in the raw output. Best-effort: an unparseable prefix (e.g. a
    block placed mid-statement) lands in the "unattributed" bucket.
    """
    def context_of(prefix: str) -> str:
        try:
            tree = ast.parse(prefix.strip())
        except SyntaxError:
            return "unattributed"
        node = tree.body[-1] if tree.body else None
        # descend to the innermost last statement (block may target a nested line)
        while node is not None:
            for attr in ("body", "orelse", "finalbody"):
                stmts = getattr(node, attr, None)
                if isinstance(stmts, list) and stmts:
                    node = stmts[-1]
                    break
            else:
                return type(node).__name__
        return "unattributed"

    # segments[i] = code emitted before block i (the last segment trails the final block)
    segments = re.split(r"<thinkanywhere>.*?</thinkanywhere>", result.raw, flags=re.DOTALL)
    kinds = [
        context_of(re.sub(r"<think>.*?</think>", "", seg, flags=re.DOTALL))
        for seg in segments[:-1]
    ]
    position_counts = Counter(kinds)

    return {
        "inline_block_count": len(result.inline_blocks),
        "attributed_positions": dict(position_counts.most_common()),
        "upfront_thinking_tokens": len(result.upfront_thinking.split()),
        "inline_thinking_tokens": sum(len(b.split()) for b in result.inline_blocks),
        "executable_lines": len(result.executable_code.splitlines()),
    }
```

### 9. Full Pipeline with LCEL

```python
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

def validate_code(output: ThinkAnywhereOutput) -> ThinkAnywhereOutput:
    """Optional: run a quick syntax check on the extracted code."""
    try:
        compile(output.executable_code, "<string>", "exec")
        output.syntax_valid = True
    except SyntaxError as e:
        output.syntax_valid = False
        output.syntax_error = str(e)
    return output

full_pipeline = (
    think_anywhere_prompt
    | llm
    | think_anywhere_parser
    | RunnableLambda(validate_code)
)

# Invoke
result = full_pipeline.invoke({"problem": "Write a function to check if a number is prime."})
print(f"Syntax valid: {result.syntax_valid}")
print(f"Inline thinking blocks used: {len(result.inline_blocks)}")
print(result.executable_code)
```

---

## Summary: What Each Component Does

| Component | Role | Maps to Paper |
|---|---|---|
| `SYSTEM_PROMPT` | Defines the `<thinkanywhere>` format rules | Training template (Table 1) |
| `think_anywhere_prompt` | Injects the problem into the template | Input `x` |
| `llm` | Generates mixed sequence `y` | Policy `πθ` |
| `parse_think_anywhere` | Separates `s`, `h(i)`, `c(i)` from `y` | Eq. 2 & 4 |
| `result.executable_code` | Final code `c = c(1) ⊕ ... ⊕ c(M+1)` | Eq. 4 |
| `result.inline_blocks` | The `h(i)` thinking blocks | `<thinkanywhere>` blocks |
| `pass_at_k` | Evaluates capability ceiling | pass@k analysis (Figure 4) |
| `analyze_thinking_positions` | Checks where the model reasons | Thinking Position Analysis (Figure 2) |

---

## Notes on Model Choice

- **Out-of-the-box (no fine-tuning):** Most frontier models (GPT-4o, Claude Sonnet, Gemini) can follow the prompt template and produce `<thinkanywhere>` blocks via prompting alone — but the paper shows prompting-only significantly underperforms trained variants (56.9 vs 70.3 avg). Use this as a prototype.
- **Fine-tuned checkpoint:** For production, fine-tune on ~5,000 cold-start samples with LoRA, then run GRPO. The paper's model is available at https://github.com/jiangxxxue/Think-Anywhere.
- **Temperature:** Use `temperature=0` (greedy) for deterministic evaluation; `temperature=0.8` for pass@k sampling.
