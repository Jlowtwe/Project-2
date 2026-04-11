# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "google-genai",
# ]
# ///

import os
import textwrap
from google import genai

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MODEL = "gemini-2.0-flash"

SYSTEM_PROMPT = """\
You are an expert meeting assistant. Your job is to read a raw meeting transcript \
and extract every action item discussed.

Return your response in this exact format:

ACTION ITEMS
============
1. [Owner] | [Task description] | [Due date or "Unspecified"]
2. [Owner] | [Task description] | [Due date or "Unspecified"]
...

FLAGGED FOR HUMAN REVIEW
=========================
- List any items that are ambiguous, unassigned, conflicting, or need a decision \
before work can begin. If none, write "None".

Rules:
- If an owner is not explicitly stated, write "Unassigned".
- If a due date is not explicitly stated, write "Unspecified".
- Do not invent or assume information that is not in the transcript.
- Surface blockers, conflicts, and deferred decisions under the review section.
"""

# ---------------------------------------------------------------------------
# Sample meeting transcripts (mirrors the eval_set cases)
# ---------------------------------------------------------------------------

TRANSCRIPTS = {
    "1": {
        "title": "Q2 Marketing Sync (Normal Case)",
        "text": textwrap.dedent("""\
            Meeting: Q2 Marketing Sync
            Date: April 10, 2026
            Attendees: Sara (Marketing), David (Design), Priya (PM)

            Sara: We need the updated brand guidelines sent to the vendor by April 18th. David, can you handle that?
            David: Sure, I'll have it done by the 17th to give a buffer.
            Priya: I'll set up the campaign tracking dashboard and share it with the team before end of next week.
            Sara: Great. I'll schedule a follow-up review meeting for April 25th.
        """),
    },
    "2": {
        "title": "Engineering Standup (Implicit Ownership)",
        "text": textwrap.dedent("""\
            Meeting: Engineering Standup
            Date: April 10, 2026
            Attendees: Leo (Backend), Fatima (QA), Marcus (DevOps)

            Leo: I'm blocked on the API refactor until the new schema is merged. Marcus said he'd get to that today.
            Fatima: Once that's in, I can start regression testing — probably takes two days.
            Marcus: Yeah, the schema PR should be merged by EOD. I'll also update the deployment runbook this week.
        """),
    },
    "3": {
        "title": "Product Brainstorm (Edge Case — No Owners or Dates)",
        "text": textwrap.dedent("""\
            Meeting: Product Brainstorm
            Date: April 10, 2026
            Attendees: Whole team (8 people, no roles recorded)

            - Someone should look into whether we can integrate Stripe before launch.
            - It would be good to do a competitive analysis at some point.
            - We talked about maybe doing user interviews in the next sprint.
            - The onboarding flow definitely needs another pass.
        """),
    },
    "4": {
        "title": "Budget Review (Conflicting Instructions — Human Review Required)",
        "text": textwrap.dedent("""\
            Meeting: Budget Review
            Date: April 10, 2026
            Attendees: Nadia (Finance), James (Operations), Elena (CEO)

            Elena: James, please cut the vendor contract renewals by 20% and have a proposal ready by April 20th.
            James: That's going to be tough — some of those contracts are multi-year locked in. I'll do what I can, but Nadia, can you look at the numbers with me first?
            Nadia: Sure, but I'm out April 14–16. Let's say April 17th?
            Elena: Fine, but I still need the full proposal by the 20th.
            James: I'll try, but I want to flag that this may not be feasible without legal sign-off.
        """),
    },
    "5": {
        "title": "Feature Prioritization (Ambiguous Decision — Human Review Required)",
        "text": textwrap.dedent("""\
            Meeting: Feature Prioritization
            Date: April 10, 2026
            Attendees: Rosa (PM), Tom (Engineering Lead), Amir (Stakeholder)

            Amir: I really think the export feature should be the top priority this quarter.
            Rosa: We discussed this last week and decided to deprioritize it in favor of the search improvements.
            Tom: Right, but Amir raised a good point about enterprise clients. Maybe we revisit?
            Rosa: Let's table it for now and move forward with search. We can circle back.
            Tom: Okay, so I'll start scoping the search feature. Amir, can you send over the enterprise client feedback?
            Amir: Will do.
        """),
    },
}

# ---------------------------------------------------------------------------
# Core function
# ---------------------------------------------------------------------------

def summarize_meeting(client: genai.Client, transcript: str) -> str:
    """Send a transcript to Gemini and return the extracted action items."""
    response = client.models.generate_content(
        model=MODEL,
        contents=transcript,
        config=genai.types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.2,
        ),
    )
    return response.text

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def print_divider(char: str = "─", width: int = 60) -> None:
    print(char * width)

def choose_transcript() -> tuple[str, str]:
    """Prompt user to pick a transcript or paste their own."""
    print("\n" + "=" * 60)
    print("  MEETING → ACTION ITEMS  |  Powered by Google Gemini")
    print("=" * 60)
    print("\nChoose a sample meeting transcript:\n")
    for key, t in TRANSCRIPTS.items():
        print(f"  [{key}] {t['title']}")
    print("  [0] Paste your own transcript\n")

    choice = input("Enter choice: ").strip()

    if choice == "0":
        print("\nPaste your transcript below. Press Enter twice when done:\n")
        lines = []
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
        return "Custom Transcript", "\n".join(lines)
    elif choice in TRANSCRIPTS:
        t = TRANSCRIPTS[choice]
        return t["title"], t["text"]
    else:
        print("Invalid choice. Using transcript 1.")
        t = TRANSCRIPTS["1"]
        return t["title"], t["text"]

def main() -> None:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY environment variable is not set.\n"
            "Get your key at https://aistudio.google.com/app/apikey"
        )

    client = genai.Client(api_key=api_key)

    title, transcript = choose_transcript()

    print(f"\nProcessing: {title}")
    print_divider()
    print("TRANSCRIPT")
    print_divider()
    print(transcript.strip())
    print_divider()
    print("Sending to Gemini...\n")

    result = summarize_meeting(client, transcript)

    print_divider()
    print("RESULT")
    print_divider()
    print(result.strip())
    print_divider()

if __name__ == "__main__":
    main()
