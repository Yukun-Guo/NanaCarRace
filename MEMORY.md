# MEMORY.md — Long-term memories for Nana

This file stores curated, high-value facts Nana (the assistant) should remember long-term.

Rules
- Only store facts the user explicitly asks to remember.
- Avoid secrets (tokens, passwords, keys). Do NOT store sensitive credentials here.
- Keep entries short, factual, and dated.

Entries
- 2026-03-09 — Son: Ethan. (User asked the assistant to remember that their son is named Ethan.)
- 2026-03-09 — Wife: Min Gao; phone: +1-503-206-2464. (User asked to remember Min's name and phone.)
- 2026-03-09 — Cat: Lulu (female). (User asked the assistant to remember their cat's name and gender.)
- 2026-03-10 — Preference: May use the self-improving-agent skill to log learnings and improve behavior, but must notify the user and get approval before installing new skills. (User request)
- 2026-03-10 — Laws: User set three guiding laws for the assistant: (1) must not injure a human being or, through inaction, allow a human being to come to harm; (2) must obey orders given by human beings except where such orders would conflict with the First Law; (3) must protect its own existence as long as such protection does not conflict with the First or Second Law. (User request)
- 2026-03-11 — Preference: When unspecified, "check my email" refers to all unread messages; when summarizing unread emails, send the summary to the user's Telegram account. (User request)
- 2026-03-19 — Note: GitHub token file located at /home/yukun/.openclaw/credentials/github. This file path is recorded as sensitive info; token contents are NOT stored here. Agents should not broadcast or store the token itself. (User request)

How to use
- Update this file when the user asks "remember X" or tells a stable preference, important date, or recurring info.
- Review and prune periodically to keep only relevant items.
