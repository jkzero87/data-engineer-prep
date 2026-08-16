# PROYECTO — suach & chimi

Two local AI agents built on one machine (RTX 5060 Ti 16GB, Ryzen 5 5600G, 32GB RAM,
Ubuntu). They are **not two products**. They are **two arms of one experiment**.

---

## 1. Philosophy and method

These rules outrank every design decision below them. They were paid for in bugs.

- **Mechanical verification outranks model judgement.** `grep` and `ast` locate and
  count; the model interprets. Large context is for *understanding*, not for counting.
- **Test aggressively, don't theorise.** This is software — trying something is free.
  When the question is "does X work?", the answer is to run it, not to explain why it
  probably isn't needed.
- **Fix the decision rule before running the experiment.** Thresholds are written down
  first, so the result can't be reinterpreted after the fact to say what we hoped.
- **Print the content; don't measure `len()` and don't trust the marker.** Three separate
  times an eval reported FAIL and the model was right — the check was wrong.
- **Never conclude from a field you truncated yourself.**
- **Triggers must be mechanical.** A fallback that fires on "the answer looked wrong" is
  not detectable, so it doesn't exist. Escalate on `MAX_STEPS`, capped history, context
  error — things a machine can see.
- **A config only counts if it completes inference,** not if it loads.
- **Numbers are re-verified against the raw records before being written down** — never
  from memory, never from an agent's narration.
- **A limitation gets a solution, not acceptance.** The only legitimate limit is a real
  hardware limit, proven by measurement.

---

## 2. The question

> On modest hardware, is it better to coordinate **two models with automatic routing**,
> or to run **one model** that is the best the hardware can hold?

Most tasks don't need more than a 4B, and a 4B is fast. Some tasks need the smartest
model the machine can run. The interesting claim of the two-model design is that the
switch between them should be **automatic** — the user should never have to choose.

If that works, it makes local AI deployable on modest hardware: you pay the cost of the
big model only on the tasks that actually need it.

If it doesn't work — if one competent model matches it with far less machinery — that is
an equally valuable result, and the simpler system wins.

**Current suspicion, held loosely:** two agents may not be as useful as they sound. The
point of the experiment is to find out, not to defend either side.

---

## 3. The two arms

| arm | architecture | today |
|---|---|---|
| **suach** | two coordinated models, automatic escalation | 4B executor + 35B-A3B brain + web search |
| **chimi** | one model, the largest that performs | Qwen3.8-27B dense with local tools |

The axis that separates them is **model count and routing** — not capability domain.
Both arms will eventually need local files *and* internet. Any difference in what they
can do today is a difference in maturity, not in design.

### Harness

**"Harness" is a pattern, not a project.** It is the governing layer: plan → verify →
retry. The agent *acts*; the harness *governs*. Both arms have one or will get one.
Naming a project "harness" was the original confusion this document exists to end.

An important asymmetry between the arms: `suach` verifies against **web evidence**, so
its judge must be a model. `chimi` verifies against **files**, where `grep`, `ast.parse`
and exit codes are available — so its harness can be mechanical, which is stronger.

---

## 4. Why these names

Greek mythology is overused. The parallel comes from Colombian indigenous cosmology
instead — specifically **Muisca**, from the altiplano cundiboyacense.

- **chimi** — from **Chiminigagua**, the primordial creative principle: the single
  source that exists *before* duality, and from which Sué was made. One model, one
  origin, everything comes from it.
- **suach** — from **Sué** (sun) and **Chía** (moon), the divine couple. The Muisca held
  them as a married pair, progenitors of everything, and understood the balance between
  the two opposing forces as necessary for harmony. Two powers that only work as a
  system — which is exactly the claim the two-model architecture is making.

The cosmology maps onto the experiment on its own: the one source came first, the
complementary pair came after. The experiment asks which is actually better here.

**Honest note on the search.** The first idea was a two-headed creature (Greek: Orthrus).
No *documented* two-headed being was found in Colombian indigenous mythology, and none
was invented to fill the gap. What these traditions do have is the **complementary
pair** — two distinct forces that only function together. That is a better metaphor for
coordinated models than a monster with two heads would have been.

**Available, not yet decided:** **Juyá** and **Pulowi**, the Wayúu primordial pair, as
names for the two models *inside* suach. The ethnography describes Juyá as mobile and
singular, Pulowi as fixed and multiple — a fair description of a fast small model that
darts around versus a heavy one that sits and thinks.

### Naming rules

- Paths, repos and identifiers: **ASCII, lowercase, no accents** — `chimi`, `suach`,
  `sue`, `chia`. Accents live in prose only. Non-ASCII in paths and git remotes causes
  breakage that is hard to grep for.
- Five characters each, because they get typed constantly.

---

## 5. Where things live

| what | where |
|---|---|
| verified state of each arm | `PROJECT_TRUTH.md` inside each repo |
| this document | goals, the experiment, and naming — the *why*, not the state |

`PROJECT_TRUTH.md` holds measurements, certified fixes, code maps and baselines, with
the command that produced each fact and its date. This file holds the reasons. When they
disagree about a number, `PROJECT_TRUTH.md` wins — it is closer to the evidence.
