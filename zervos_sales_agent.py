#!/usr/bin/env python3
"""
Zervos Sales Agent — 500 units in 2026
An expert consultative sales agent powered by Claude Opus 4.6.
Researches each prospect before the conversation begins.
"""

import anthropic

# ── System prompt builder ────────────────────────────────────────────────────

BASE_SYSTEM_PROMPT = """You are Franck, an elite consultative sales agent for Zervos — a premium product
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
5. Use the prospect intelligence brief below to **skip known facts** and open
   with a sharp, personalised question that shows you've done your homework.

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

{intel_section}

Begin by warmly greeting the prospect by name (if known) and opening with a
sharp, personalised question based on what you've learned about them."""


def build_system_prompt(intel: str) -> str:
    if intel:
        section = f"## Prospect intelligence brief\n{intel}"
    else:
        section = ("## Prospect intelligence brief\n"
                   "No pre-call research available. Gather situation context "
                   "from scratch during the conversation.")
    return BASE_SYSTEM_PROMPT.format(intel_section=section)


# ── Prospect researcher ──────────────────────────────────────────────────────

RESEARCH_SYSTEM = """You are a B2B sales intelligence analyst fluent in English, French, and Chinese.
Given a prospect's name and/or company, search the web — including Chinese-language
sources (Baidu, Sina, 36Kr, Caixin, WeChat public accounts, etc.) — to build a
concise pre-call brief (max 350 words) covering:

- Company overview: industry, size, headquarters, main products/services
- Recent news or strategic moves (last 6–12 months) — check both Western AND
  Chinese-language media; Chinese sources often surface deals, partnerships, or
  expansions not yet covered in English press
- Likely business challenges or growth priorities
- Key decision-makers or leadership names if findable
- Any signals that suggest they might benefit from a premium product purchase
- China-specific angle: presence in China, Chinese investors/partners, or
  relevance to Chinese market trends (if applicable)

Search strategy:
1. Start with an English-language search for the company overview.
2. Run at least one Chinese-language query (company name in Chinese if known,
   or romanised name + 公司/集团) to catch any China-side coverage.
3. Synthesise both into a single unified brief.

Be factual. If Chinese sources add nothing new, note that briefly.
Output ONLY the brief — no preamble, no commentary."""


def research_prospect(client: anthropic.Anthropic, prospect_info: str) -> str:
    """
    Run a web-search agentic loop to build a prospect intelligence brief.
    Returns the brief as a plain string.
    """
    print("\n[Researching prospect…]", flush=True)

    messages = [
        {
            "role": "user",
            "content": (
                f"Build a pre-call sales brief for this prospect: {prospect_info}\n"
                "Search the web for relevant information."
            ),
        }
    ]
    tools = [
        {"type": "web_search_20260209", "name": "web_search"},
    ]

    # Agentic loop — run until Claude stops calling tools
    while True:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=2048,
            system=RESEARCH_SYSTEM,
            tools=tools,
            messages=messages,
        )

        # Append assistant turn
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            # Extract the final text block
            brief = next(
                (b.text for b in response.content if b.type == "text"), ""
            )
            return brief.strip()

        if response.stop_reason == "tool_use":
            # Collect all tool results and feed them back as a single user turn
            tool_results = []
            for block in response.content:
                if block.type == "tool_result":
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.tool_use_id,
                        "content": block.content,
                    })
                # web_search results come back as server_tool_use / tool_result
                # The SDK surfaces them automatically in response.content
            if tool_results:
                messages.append({"role": "user", "content": tool_results})
            # If no explicit tool_result blocks, the SDK already handled it;
            # just continue the loop so Claude can produce its final answer.
            continue

        # Unexpected stop reason — return whatever text we have
        brief = next(
            (b.text for b in response.content if b.type == "text"), ""
        )
        return brief.strip()


# ── Sales agent ──────────────────────────────────────────────────────────────


class ZervosSalesAgent:
    """Multi-turn consultative sales agent for Zervos with prospect research."""

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.messages: list[dict] = []
        self.model = "claude-opus-4-6"
        self.system_prompt = build_system_prompt("")  # updated after research

    def _stream_reply(self, user_input: str) -> str:
        """Send a message, stream the response, and return the full reply."""
        self.messages.append({"role": "user", "content": user_input})

        full_reply = ""
        with self.client.messages.stream(
            model=self.model,
            max_tokens=1024,
            thinking={"type": "adaptive"},
            system=self.system_prompt,
            messages=self.messages,
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
                full_reply += text

        print()  # newline after streaming ends
        self.messages.append({"role": "assistant", "content": full_reply})
        return full_reply

    def prepare(self, prospect_info: str):
        """Research the prospect and prime the system prompt."""
        if prospect_info.strip():
            intel = research_prospect(self.client, prospect_info)
            if intel:
                print("\n── Prospect brief ──────────────────────────────────")
                print(intel)
                print("────────────────────────────────────────────────────\n")
            self.system_prompt = build_system_prompt(intel)
        else:
            self.system_prompt = build_system_prompt("")

    def start(self):
        """Open the sales conversation with the agent's personalised greeting."""
        opening = self._stream_reply(
            "Hello, I'm ready to learn more about Zervos."
        )
        return opening

    def chat(self, user_input: str) -> str:
        """Process one prospect turn and return the agent's reply."""
        return self._stream_reply(user_input)

    def run_interactive(self):
        """Run an interactive terminal session."""
        print("\n" + "═" * 60)
        print("  ZERVOS SALES AGENT  |  Target: 500 units in 2026")
        print("═" * 60)
        print("(Type 'quit' or 'exit' to end the conversation)\n")

        # ── Pre-call research ──
        try:
            prospect_info = input(
                "Prospect name / company (press Enter to skip): "
            ).strip()
        except (EOFError, KeyboardInterrupt):
            prospect_info = ""

        self.prepare(prospect_info)

        # ── Opening ──
        print("\nAgent: ", end="")
        self.start()

        # ── Conversation loop ──
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
                print(
                    "\nAgent: Thank you for your time! I'll follow up with a "
                    "summary shortly. Have a great day!\n"
                )
                break

            print("\nAgent: ", end="")
            self.chat(user_input)


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    agent = ZervosSalesAgent()
    agent.run_interactive()
