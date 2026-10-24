# CLAUDE.md

Starters for AllSense by OtterBridge modules: `frame-template/` (JSON, no code), `python-module/` (an outside module with tests against the fake phone) and `skills/allsense-module/SKILL.md` (how a person or agent builds a module). Public, MIT.

## Working here

- **The user makes every commit and push.** Edit files and run the tests, then hand over: what changed, the test results, and a one-line commit message suggestion. Never run `git commit`, `git push`, tags or releases; add no Co-Authored-By line unless asked.
- **Public repository:** never write the user's serials, IPs, Wi-Fi details, home location, tokens or file paths into it. Machine facts go in `CLAUDE.local.md` (git-ignored).

## Test

```bash
.venv/Scripts/python -m pytest -q python-module                     # the starter module against the fake phone
.venv/Scripts/allsense-template check frame-template/example.json    # parses, prints a byte map
```

Setup: `python -m venv .venv`, then `.venv/Scripts/pip install -e ../otterbridge-allsense-protocol -e ../otterbridge-allsense-python pytest` (until both are on PyPI).

## How it fits

- Everything here builds on the protocol and test kit in `otterbridge-allsense-protocol` and the clients; a protocol change lands there first.
- The skill and READMEs link to the docs site (https://docs.allsense.otterbridge.org/) and the other repos by URL, never by local path, so a copied folder still makes sense.
- The app is closed source: in-app modules aren't part of this repo. People who need a new link inside the app open an issue in the home repo (`otterbridge-allsense`).
