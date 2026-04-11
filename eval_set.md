| # | Type | What it tests |
|---|------|---------------|
| 1 | Normal | Clean transcript with explicit owners and dates — baseline extraction |
| 2 | Normal | Ownership inferred from dialogue context, not direct assignment |
| 3 | Edge case | No owners, no dates — model must flag unassigned rather than hallucinate |
| 4 | Likely to fail | Conflicting constraints + legal blocker — model must surface flags, not just list tasks |
| 5 | Likely to fail | Ambiguous/deferred decision — model must represent unresolved items without treating them as settled |

Each case includes a realistic meeting transcript, the expected structured output, and a rationale explaining what behavior the case is probing.
