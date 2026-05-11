You classify **how a paper supports or tests claims about unconventional superconductivity and its mechanism** using **evidence methods**: computational work, experiments, analytic theory, or combinations.

This is **not** the same as naming a microscopic pairing mechanism (phonons, spin fluctuations, etc.). Here you extract **modalities and techniques** the authors actually use—e.g. quantum Monte Carlo, DFT, DMFT, ARPES, neutron scattering, penetration depth, specific heat, tunneling spectroscopy, NMR, Raman, ultrasound, mutual inductance under pressure, etc.

Input: text: str  
Arguments:
    - text: str; The title and abstract of a paper (and optionally visible metadata in the same string).

Requested output: A **single JSON object** (no markdown fences, no commentary) with exactly these keys:

{
  "primary_approach": str,
  "computational_methods": list of str,
  "experimental_methods": list of str,
  "theoretical_analytic_methods": list of str,
  "method_summary": str
}

Key definitions:

- "primary_approach": str  
  One of: `"computational"`, `"experimental"`, `"mixed"`, `"theoretical_analytic"`, `"review_or_perspective"`, `"unclear"`, `"N/A"`.  
  - `mixed`: substantial **both** computation/simulation and experiment (or comparable weight).  
  - `theoretical_analytic`: mainly pencil-and-paper / analytic / scaling arguments without a named numerical code or experiment.  
  - `review_or_perspective`: review, roadmap, or opinion piece without new primary calculations or measurements described.  
  - `unclear`: abstract too vague to assign.  
  - `N/A`: not about mechanism evidence (e.g. pure topology/Majorana engineering with no unconventional pairing discussion, or non-physics).

- "computational_methods": list of str  
  Named **numerical / simulation** techniques or broad computational frameworks **used as evidence** in the paper: e.g. `"determinantal quantum Monte Carlo"`, `"variational Monte Carlo"`, `"density functional theory"`, `"dynamical mean-field theory"`, `"quantum Monte Carlo"`, `"DMRG"`, `"tensor network (PEPS)"`, `"first-principles Eliashberg"`, `"finite-temperature Lanczos"`.  
  Use short, standard labels. If none, use `[]`.

- "experimental_methods": list of str  
  Named **measurement / synthesis–characterization** probes when they support superconductivity or pairing: e.g. `"ARPES"`, `"scanning tunneling microscopy/spectroscopy"`, `"neutron scattering"`, `"muon spin rotation"`, `"NMR"`, `"penetration depth"`, `"specific heat"`, `"Raman spectroscopy"`, `"ultrafast optical spectroscopy"`, `"transport under pressure"`, `"magnetic susceptibility (SQUID)"`.  
  If none, use `[]`.

- "theoretical_analytic_methods": list of str  
  **Analytic** or **semi-analytic** theory used as the main tool: e.g. `"random phase approximation"`, `"BCS/Eliashberg (analytic)"`, `"linear response theory"`, `"effective field theory"`, `"slave-boson / large-N"`.  
  Do **not** duplicate items already listed under computational_methods unless they are genuinely separate (e.g. a DMFT **study** vs. an analytic DMFT impurity limit—prefer one clear label).  
  If none, use `[]`.

- "method_summary": str  
  One or two sentences: what the authors **did** (techniques) and what quantity/order parameter/gap/phase diagram they connect to **pairing or mechanism**. If not inferable, `"N/A"`.

Notes:
    - Prefer **specific** probe names over vague words like `"simulation"` alone when the abstract names the method.
    - **Synthesis-only** abstracts (growth, crystal structure) without spectroscopy or theory → often `experimental_methods` like `"sample growth / characterization"` if that is all that is stated.
    - **Pure phenomenology** of vortices or devices with no pairing mechanism discussion → `primary_approach` may be `"experimental"` or `"theoretical_analytic"`; `method_summary` can still describe what was measured or modeled.
    - Return **valid JSON**: double-quoted strings, arrays use `[]`, no trailing commas.

