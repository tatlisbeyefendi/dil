# Contributing

Thanks for looking. A few ground rules keep this engine honest.

## The one rule that matters

**Every rule needs a test with a real Turkish form.** If you add a suffix, add the word that
proves it — `okumuyorum`, not `okumak + yor + um`. Turkish has enough exceptions that a green
test suite is the only evidence a rule is right.

## Setup

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e .
pip install pytest ruff
python3 -m pytest
```

## Before you open a pull request

```bash
make check     # ruff + pytest
```

- Keep the package dependency-free. This tool is expected to run on a bare Python install,
  including a phone SSH session and a CI runner with no network.
- New irregular stems go in `src/dil/lexicon.py` with a note, not into `if` statements.
- Plain text output only: no colour, no cursor tricks, tables must survive `| less` and a
  terminal that is 80 columns wide.

## Reporting a wrong form

Open an issue with the input, what you got, and what Turkish actually says. Include the source
(TDK sözlük, a grammar reference) if you can — the fix is one line once the case is clear.
