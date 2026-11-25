# Documentation index

| Document | What it covers |
|---|---|
| [architecture.md](architecture.md) | Stack, folders, diagrams, design decisions |
| [api.md](api.md) | Every endpoint, request/response, status codes |
| [business-rules.md](business-rules.md) | Slot, validation and booking rules; the four defects |
| [testing-guide.md](testing-guide.md) | Bug flags, `data-testid` selectors, doctor ids, scenario ideas |
| [bdd-guide.md](bdd-guide.md) | BDD and Gherkin explained with our feature files |
| [behave-guide.md](behave-guide.md) | Behave: steps, context, hooks, tags, running, reports |
| [playwright-guide.md](playwright-guide.md) | Playwright: locators, waits, assertions, API testing, debugging |

Suggested reading order for learning: `bdd-guide` -> `behave-guide` -> `playwright-guide`,
then open `tests/features/booking_flow.feature` and follow one scenario through the code.
