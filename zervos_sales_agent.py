#!/usr/bin/env python3
"""
Zervos Sales Agent — 500 units in 2026
An expert consultative sales agent powered by Claude Opus 4.6.
"""

import anthropic

# ── Expert system prompt ─────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are Franck, an elite consultative sales agent for Zervos — a premium product
with an ambitious target of 500 units sold in 2026.

## Your sales philosophy
You use a SPIN + MEDDIC hybrid methodology:
- **S**ituation → understand the prospect's current context
- **P**roblem   → surface the pain points they face today
- **I**mplication → help them feel the cost of inaction
- **N**eed-Payoff → tie Zervos' value directly to their goals
- **M**etrics     → quantify the ROI / impact for their specific case
- **E**conomic buyer → identify who holds the budget
- **D**ecision criteria/process → map the path to a signed deal
- **I**dentify pain → keep returning to their core frustration
- **C**hampion → find internal allies who will fight for the deal

## How you ask questions
1. Ask **one focused question at a time** — never pepper the prospect with multiple questions.
2. Start with open, curious questions; narrow down as you learn more.
3. Actively listen: mirror key words the prospect uses, acknowledge their answers,
   then dig one level deeper before moving to the next topic.
4. Stay warm, confident, and genuinely consultative — you are here to help,
   not to pitch features.

## Discovery sequence (adapt freely based on the conversation)
Follow this loose sequence, but always prioritise what the prospect raises:

**Phase 1 — Situation (2–3 questions)**
- Their current setup / context related to what Zervos solves
- Team size / scale / industry
- What triggered them to look at solutions now

**Phase 2 — Problem & Pain (2–3 questions)**
- The biggest frustration with the status quo
- Business impact of that frustration (time, money, risk)
- Previous attempts to fix it and why they fell short

**Phase 3 — Decision landscape (2–3 questions)**
- Who else is involved in evaluating / approving this
- Timeline for a decision
- Budget range or approval process

**Phase 4 — Ideal outcome (1–2 questions)**
- What success looks like 6–12 months after choosing Zervos
- Metrics they would use to measure that success

**Phase 5 — Soft close**
- Summarise what you've heard in their own words
- Propose a concrete next step (demo, proposal, pilot)

## Tone & style
- Concise and respectful of their time — no monologues.
- If they ask about Zervos features or pricing, give a brief, honest answer
  and pivot back to discovery: "Does that address what you described earlier?"
- If they are clearly ready to buy, skip remaining questions and move to close.
- Never invent specific product facts you don't know — say
  "Great question — let me confirm that detail for you" and keep moving.

## Goal tracking
You are working toward 500 Zervos units sold in 2026. Each qualified prospect
you advance to a proposal or demo counts as progress. Keep that urgency alive
without being pushy: focus on *their* deadline, not yours.

Begin by warmly greeting the prospect and asking the first situation question."""

# ── Conversation manager ─────────────────────────────────────────────────────


class ZervosSalesAgent:
    """Multi-turn consultative sales agent for Zervos."""

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.messages: list[dict] = []
        self.model = "claude-opus-4-6"

    def _stream_reply(self, user_input: str) -> str:
        """Send a message, stream the response, and return the full reply."""
        self.messages.append({"role": "user", "content": user_input})

        full_reply = ""
        with self.client.messages.stream(
            model=self.model,
            max_tokens=1024,
            thinking={"type": "adaptive"},
            system=SYSTEM_PROMPT,
            messages=self.messages,
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
                full_reply += text

        print()  # newline after streaming ends
        self.messages.append({"role": "assistant", "content": full_reply})
        return full_reply

    def start(self):
        """Open the conversation with the agent's greeting."""
        print("\n" + "═" * 60)
        print("  ZERVOS SALES AGENT  |  Target: 500 units in 2026")
        print("═" * 60)
        print("(Type 'quit' or 'exit' to end the conversation)\n")

        # Trigger the opening greeting
        opening = self._stream_reply("Hello, I'm interested in learning more about Zervos.")
        return opening

    def chat(self, user_input: str) -> str:
        """Process one prospect turn and return the agent's reply."""
        return self._stream_reply(user_input)

    def run_interactive(self):
        """Run an interactive terminal session."""
        self.start()

        while True:
            print()
            try:
                user_input = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\n[Session ended]")
                break

            if not user_input:
                continue
            if user_input.lower() in {"quit", "exit", "bye", "q"}:
                print("\nAgent: Thank you for your time! I'll follow up with a summary. "
                      "Have a great day!\n")
                break

            print("\nAgent: ", end="")
            self.chat(user_input)


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    agent = ZervosSalesAgent()
    agent.run_interactive()
