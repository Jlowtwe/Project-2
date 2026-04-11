| # | Type | What it tests |
|---|------|---------------|
| 1 | Normal | Clean transcript with explicit owners and dates — baseline extraction |
| 2 | Normal | Ownership inferred from dialogue context, not direct assignment |
| 3 | Edge case | No owners, no dates — model must flag unassigned rather than hallucinate |
| 4 | Likely to fail | Conflicting constraints + legal blocker — model must surface flags, not just list tasks |
| 5 | Likely to fail | Ambiguous/deferred decision — model must represent unresolved items without treating them as settled |

Each case includes a realistic meeting transcript, the expected structured output, and a rationale explaining what behavior the case is probing.

# Evaluation Set: Meeting Summarization → Action Items

**Task:** Given a meeting transcript, extract a structured list of action items (owner, task, due date).

**Grading rubric per case:**
- `pass` — all action items correctly identified, owner and due date extracted or noted as unspecified
- `partial` — most action items found but minor omissions or inaccuracies
- `fail` — significant misses, hallucinated items, or items requiring human correction before use

---

## Case 1 — Normal Case

**Input:**
```
Meeting: Q2 Marketing Sync
Date: April 10, 2026
Attendees: Sara (Marketing), David (Design), Priya (PM)

Sara: We need the updated brand guidelines sent to the vendor by April 18th. David, can you handle that?
David: Sure, I'll have it done by the 17th to give a buffer.
Priya: I'll set up the campaign tracking dashboard and share it with the team before end of next week.
Sara: Great. I'll schedule a follow-up review meeting for April 25th.
```

**Expected output:**
| Owner  | Action Item                                      | Due Date     |
|--------|--------------------------------------------------|--------------|
| David  | Send updated brand guidelines to vendor          | April 17     |
| Priya  | Set up and share campaign tracking dashboard     | April 17     |
| Sara   | Schedule follow-up review meeting                | April 25     |

**Why this case:** Clean, structured conversation with explicit owners and dates. Tests baseline extraction capability.

---

## Case 2 — Normal Case (Implicit Ownership)

**Input:**
```
Meeting: Engineering Standup
Date: April 10, 2026
Attendees: Leo (Backend), Fatima (QA), Marcus (DevOps)

Leo: I'm blocked on the API refactor until the new schema is merged. Marcus said he'd get to that today.
Fatima: Once that's in, I can start regression testing — probably takes two days.
Marcus: Yeah, the schema PR should be merged by EOD. I'll also update the deployment runbook this week.
```

**Expected output:**
| Owner   | Action Item                              | Due Date              |
|---------|------------------------------------------|-----------------------|
| Marcus  | Merge new schema PR                      | April 10 (EOD)        |
| Fatima  | Begin regression testing after merge     | ~April 12 (dependent) |
| Marcus  | Update deployment runbook                | April 17 (this week)  |

**Why this case:** Ownership is established via attribution in dialogue rather than direct assignment. Tests ability to infer ownership from conversational context.

---

## Case 3 — Edge Case (No Clear Owners or Dates)

**Input:**
```
Meeting: Product Brainstorm
Date: April 10, 2026
Attendees: Whole team (8 people, no roles recorded)

- Someone should look into whether we can integrate Stripe before launch.
- It would be good to do a competitive analysis at some point.
- We talked about maybe doing user interviews in the next sprint.
- The onboarding flow definitely needs another pass.
```

**Expected output:**
| Owner       | Action Item                              | Due Date       |
|-------------|------------------------------------------|----------------|
| Unassigned  | Investigate Stripe integration feasibility | Unspecified  |
| Unassigned  | Conduct competitive analysis             | Unspecified    |
| Unassigned  | Schedule user interviews                 | Next sprint    |
| Unassigned  | Revise onboarding flow                   | Unspecified    |

**Why this case:** No owners, vague timing, passive voice. Tests whether the model correctly flags unassigned items rather than hallucinating owners.

---

## Case 4 — Likely to Fail / Requires Human Review (Conflicting Instructions)

**Input:**
```
Meeting: Budget Review
Date: April 10, 2026
Attendees: Nadia (Finance), James (Operations), Elena (CEO)

Elena: James, please cut the vendor contract renewals by 20% and have a proposal ready by April 20th.
James: That's going to be tough — some of those contracts are multi-year locked in. I'll do what I can, but Nadia, can you look at the numbers with me first?
Nadia: Sure, but I'm out April 14–16. Let's say April 17th?
Elena: Fine, but I still need the full proposal by the 20th.
James: I'll try, but I want to flag that this may not be feasible without legal sign-off.
```

**Expected output:**
| Owner  | Action Item                                         | Due Date   | Flag                              |
|--------|-----------------------------------------------------|------------|-----------------------------------|
| James  | Prepare vendor contract reduction proposal (20%)    | April 20   | Feasibility uncertain; legal sign-off may be required |
| Nadia  | Review budget numbers with James                    | April 17   | Nadia unavailable April 14–16     |
| James  | Obtain legal sign-off on contract changes           | Unspecified | Explicitly flagged as blocker    |

**Why this case:** Conflicting constraints (locked contracts, tight deadline, legal dependency, availability gap). A model that does not surface the flags and blockers — or that presents the action items as straightforward — produces output that is misleading and requires human review before acting on.

---

## Case 5 — Likely to Fail / Requires Human Review (Ambiguous Decisions)

**Input:**
```
Meeting: Feature Prioritization
Date: April 10, 2026
Attendees: Rosa (PM), Tom (Engineering Lead), Amir (Stakeholder)

Amir: I really think the export feature should be the top priority this quarter.
Rosa: We discussed this last week and decided to deprioritize it in favor of the search improvements.
Tom: Right, but Amir raised a good point about enterprise clients. Maybe we revisit?
Rosa: Let's table it for now and move forward with search. We can circle back.
Tom: Okay, so I'll start scoping the search feature. Amir, can you send over the enterprise client feedback?
Amir: Will do.
```

**Expected output:**
| Owner  | Action Item                                    | Due Date    | Flag                                              |
|--------|------------------------------------------------|-------------|---------------------------------------------------|
| Tom    | Begin scoping search improvements feature      | Unspecified | Priority confirmed in this meeting                |
| Amir   | Send enterprise client feedback to team        | Unspecified | —                                                 |
| —      | Export feature priority decision               | —           | Decision deferred; revisit needed — not resolved  |

**Why this case:** A decision appears to be made (search wins) but is not fully agreed upon, and a significant item (export feature) is deferred without a clear owner or date. A model that either omits the deferred item or presents it as resolved will produce incorrect output requiring human correction.
