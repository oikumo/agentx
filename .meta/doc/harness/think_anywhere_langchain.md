# THINK-ANYWHERE — Theory & LangChain Implementation

---

## Core Theory

### The Problem with Upfront Thinking

Standard LLMs reason *before* generating code:

```
P(c, s | x) = P(s | x) · P(c | x, s)
              ^^^^^^^^^^^   ^^^^^^^^^^^
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
async def stream_think_anywhere(problem: str):
    """Stream raw output and parse at the end."""
    buffer = ""
    async for chunk in think_anywhere_chain.astream({"problem": problem}):
        # chunk is a ThinkAnywhereOutput only at the final step;
        # use the raw LLM stream instead for live output
        pass

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

```python
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableParallel

def build_sampler(temperature: float = 0.8, k: int = 5) -> ChatOpenAI:
    """For pass@k, sample with temperature > 0."""
    return ChatOpenAI(model="gpt-4o", temperature=temperature, max_tokens=4096)

async def pass_at_k(problem: str, k: int = 5, test_fn=None) -> dict:
    """
    Sample k solutions and check how many pass tests.
    test_fn(code: str) -> bool
    """
    sampler = build_sampler(temperature=0.8, k=k)
    sample_chain = think_anywhere_prompt | sampler | think_anywhere_parser

    tasks = [sample_chain.ainvoke({"problem": problem}) for _ in range(k)]
    import asyncio
    results: list[ThinkAnywhereOutput] = await asyncio.gather(*tasks)

    passed = sum(1 for r in results if test_fn and test_fn(r.executable_code))
    return {
        "pass_at_k": passed / k,
        "k": k,
        "passed": passed,
        "solutions": [r.executable_code for r in results],
        "thinking_counts": [len(r.inline_blocks) for r in results],
    }
```

### 8. Entropy-Aware Position Analysis (Optional Diagnostic)

Replicate the paper's "Thinking Position Analysis" to inspect where your model invokes thinking:

```python
import ast
from collections import Counter

def analyze_thinking_positions(result: ThinkAnywhereOutput) -> dict:
    """
    Identify the syntactic context of each <thinkanywhere> block
    by finding its surrounding AST node in the executable code.
    """
    try:
        tree = ast.parse(result.executable_code)
    except SyntaxError:
        return {"error": "unparseable code", "inline_block_count": len(result.inline_blocks)}

    node_types = [type(node).__name__ for node in ast.walk(tree)]
    syntax_counts = Counter(node_types)

    return {
        "inline_block_count": len(result.inline_blocks),
        "upfront_thinking_tokens": len(result.upfront_thinking.split()),
        "inline_thinking_tokens": sum(len(b.split()) for b in result.inline_blocks),
        "executable_lines": len(result.executable_code.splitlines()),
        "ast_node_distribution": dict(syntax_counts.most_common(10)),
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
