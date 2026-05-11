You classify which **standardized research methods** a superconductivity paper uses, based on its previously extracted method information.

Input: a JSON object with keys `computational_methods`, `experimental_methods`, `theoretical_analytic_methods`, and `method_summary`, extracted from a paper's abstract.

Task: map the input methods to the standardized categories below. Return **only** the categories that match. A match means the input method is the same technique as (or a clear variant/sub-type of) the standardized category.

---

## Standardized method categories

### Computational methods (17)

1. DFT — density functional theory, first-principles calculations, ab initio DFT, DFT+U, hybrid functional
2. DFPT — density functional perturbation theory
3. Electron-Phonon Coupling Calculations — numerical electron-phonon coupling, Eliashberg spectral function computation, lambda calculations
4. Band Structure Calculations — electronic band structure, Fermi surface mapping (computational)
5. Electronic Structure Calculations — general electronic structure (when not specifically DFT or band structure)
6. Phonon Calculations — phonon dispersion, phonon spectrum, lattice dynamics (computational)
7. BCS / Eliashberg — BCS theory (numerical), Eliashberg equations (numerical or analytic), Migdal-Eliashberg, gap equation solving
8. DMFT — dynamical mean-field theory, DFT+DMFT
9. QMC — quantum Monte Carlo, determinantal QMC, diffusion QMC, auxiliary-field QMC
10. Monte Carlo Simulations — classical Monte Carlo, Metropolis, kinetic Monte Carlo (not quantum)
11. Exact Diagonalization — exact diagonalization, Lanczos diagonalization
12. DMRG — density matrix renormalization group
13. NRG — numerical renormalization group
14. FEM — finite element method, finite element simulations
15. Numerical Simulations — general numerical simulations, molecular dynamics, FDTD, not fitting other categories
16. Tight-Binding Model — tight-binding calculations or analytic tight-binding models
17. Fermi Surface Calculations — Fermi surface topology, nesting calculations

### Experimental methods (68)

18. ARPES — angle-resolved photoemission spectroscopy
19. Electrical Resistivity / Transport — electrical resistivity, four-probe transport, sheet resistance
20. TEM — transmission electron microscopy, HRTEM, STEM
21. STM/STS — scanning tunneling microscopy/spectroscopy
22. XRD — X-ray diffraction, powder XRD, single-crystal XRD
23. SQUID Magnetometry — SQUID magnetometer measurements
24. Magnetic Susceptibility / Magnetization — DC/AC magnetic susceptibility, magnetization measurements, M-H curves
25. Neutron Scattering — inelastic/elastic neutron scattering, neutron diffraction, neutron spectroscopy
26. Specific Heat / Heat Capacity — specific heat, calorimetry, heat capacity
27. Raman Spectroscopy — Raman scattering, Raman measurements
28. SEM — scanning electron microscopy
29. Electron Microscopy (General) — general electron microscopy when TEM/SEM not specified
30. NMR — nuclear magnetic resonance
31. NQR — nuclear quadrupole resonance
32. muSR — muon spin rotation/relaxation/resonance
33. Tc Measurement — superconducting transition temperature measurement, resistive/magnetic Tc
34. Hc2 Measurement — upper critical field measurement
35. Jc Measurement — critical current density measurement
36. Magnetoresistance / Magnetotransport — magnetoresistance, MR, magnetotransport
37. Hall Effect — Hall coefficient, Hall resistivity
38. XPS — X-ray photoelectron spectroscopy
39. XAS — X-ray absorption spectroscopy, XANES, EXAFS
40. RIXS — resonant inelastic X-ray scattering
41. EDX — energy-dispersive X-ray spectroscopy, EDS
42. EELS — electron energy loss spectroscopy
43. FTIR — Fourier-transform infrared spectroscopy
44. Infrared / Optical Spectroscopy — optical conductivity, reflectance spectroscopy, ellipsometry, UV-Vis
45. Microwave Spectroscopy — microwave cavity, microwave impedance, surface impedance
46. Mossbauer Spectroscopy — Mossbauer effect measurements
47. ESR/EPR — electron spin resonance, electron paramagnetic resonance
48. Electron Diffraction — selected area electron diffraction (SAED), LEED
49. RHEED — reflection high-energy electron diffraction
50. Quantum Oscillations — de Haas-van Alphen, Shubnikov-de Haas
51. Thermal Conductivity — thermal conductivity measurements
52. Thermal Expansion — thermal expansion, dilatometry
53. Thermoelectric / Seebeck — thermopower, Seebeck coefficient, Nernst effect
54. TGA — thermogravimetric analysis
55. DTA — differential thermal analysis, DSC
56. PLD — pulsed laser deposition
57. MBE — molecular beam epitaxy
58. CVD — chemical vapor deposition, sputtering deposition
59. Epitaxial Thin Film Growth — epitaxial growth (when method not specified as PLD/MBE/CVD)
60. Sample Synthesis / Characterization — sample preparation, crystal growth, polycrystalline synthesis, sol-gel, solid-state reaction
61. Temperature-Dependent Measurements — temperature-dependent measurements (general, not fitting other categories)
62. Pressure-Dependent Measurements — high-pressure measurements, diamond anvil cell, pressure-dependent transport
63. Magnetic-Field-Dependent Measurements — field-dependent measurements (general)
64. Magnetic-Field-Dependent Transport — field-dependent transport (when distinct from magnetoresistance)
65. Low-Temperature Measurements — cryogenic measurements (general)
66. AFM — atomic force microscopy
67. MFM — magnetic force microscopy
68. Scanning SQUID Microscopy — scanning SQUID, SQUID microscope imaging
69. Magneto-Optical Imaging — magneto-optical Kerr, Faraday imaging
70. Josephson Junction Measurements — Josephson junction experiments, Josephson effect measurements
71. I-V Measurements — current-voltage characteristics
72. Point-Contact Spectroscopy — point-contact Andreev reflection, PCAR
73. Andreev Reflection Spectroscopy — Andreev reflection experiments (non-point-contact)
74. Circuit QED / Superconducting Qubits — circuit QED, transmon, superconducting qubit experiments
75. SNSPD — superconducting nanowire single-photon detector
76. Device Fabrication — lithography, nanofabrication, device processing
77. AC Loss Measurements — AC susceptibility loss, AC transport loss
78. MEG — magnetoencephalography
79. MRI — magnetic resonance imaging (superconductor application)
80. Temperature-Dependent Spectroscopy — temperature-dependent optical/spectroscopic measurements
81. DLS — dynamic light scattering
82. Electron Microprobe Analysis — EPMA, WDS
83. Electrostatic Gating — ionic liquid gating, electrostatic doping, back-gate
84. Cryogenic Testing — cryogenic environment testing (general)
85. Electrical Resistivity Under Pressure — resistivity measurements specifically under pressure

### Theoretical / analytic methods (43)

86. Ginzburg-Landau Theory — GL theory, GL free energy, GL equations
87. Mean-Field Theory — mean-field approximation, self-consistent mean field, Hartree-Fock mean field
88. Effective Field Theory — low-energy effective theory, effective action
89. Symmetry Analysis — group theory, symmetry classification of order parameters, irreducible representations
90. Linear / Nonlinear Response Theory — Kubo formula, linear response, optical conductivity theory, nonlinear response
91. Topological Band/Field Theory — topological classification, Chern number, topological invariants, topological field theory
92. Scaling Analysis — scaling theory, critical exponents, finite-size scaling, universality
93. Model Hamiltonian Analysis — model Hamiltonian construction, effective model analysis
94. Renormalization Group — RG flow, Wilsonian RG, perturbative RG
95. RPA — random phase approximation
96. Perturbation Theory — diagrammatic perturbation theory, weak-coupling expansion, self-energy corrections
97. Andreev Theory — Andreev reflection theory, Andreev bound states, BTK theory
98. Josephson Junction Theory — Josephson equations, RSJ model, Josephson effect theory
99. Phenomenological / Analytical Modeling — phenomenological models, analytical fitting, empirical modeling
100. BdG Theory — Bogoliubov-de Gennes equations, BdG Hamiltonian
101. Floquet Theory — Floquet engineering, periodically driven systems
102. Bulk-Boundary Correspondence — bulk-edge correspondence, surface state analysis (topological)
103. Luttinger Liquid Theory — Tomonaga-Luttinger liquid, bosonization of 1D systems
104. Bean Critical-State Model — Bean model, critical-state model for flux pinning
105. Proximity Effect Theory — proximity effect, SNS junction theory, Usadel equations
106. London Theory — London equations, London penetration depth theory
107. Percolation Theory — percolation models, random resistor networks
108. Bosonization — bosonization technique (general, beyond Luttinger liquid)
109. Linear Stability Analysis — stability analysis of order parameter, instability criteria
110. Effective Hamiltonian — effective Hamiltonian derivation, downfolding
111. Phase Diagram Analysis — analytic phase diagram construction, phase boundary analysis
112. AdS/CFT (Holographic Duality) — holographic superconductor, gauge/gravity duality
113. RVB Theory — resonating valence bond, Anderson RVB
114. Two-Fluid Model — Gorter-Casimir two-fluid model
115. Collective Pinning Theory — Larkin-Ovchinnikov collective pinning, flux creep theory
116. Fermi Liquid Theory — Landau Fermi liquid, quasiparticle theory
117. Scattering Theory — T-matrix, Born approximation, scattering cross-section
118. Collective Mode Analysis — Higgs mode, Leggett mode, collective excitation analysis
119. Input-Output Theory — input-output formalism (quantum optics / circuit QED)
120. Linearized Gap Equation — linearized gap equation analysis, pairing symmetry determination
121. Asymptotic Analysis — asymptotic expansion, WKB, saddle-point approximation
122. Green's Function Formalism — Matsubara Green's function, Keldysh formalism, NEGF
123. Quantum Measurement Theory — POVM, quantum measurement backaction, weak measurements
124. Nonlinear Sigma Model — NLσM, replica field theory
125. t-J Model — t-J model analysis (analytic)
126. Circuit Quantization — circuit Hamiltonian quantization, black-box quantization
127. Drude Model — Drude conductivity, Drude-Lorentz model
128. Anderson Localization Theory — disorder-driven localization, weak localization theory

---

## Output format

Return a **single JSON object** (no markdown fences, no commentary) with exactly these keys:

```
{
  "matched_methods": [list of matched standardized category names],
  "other": [list of input method names that do NOT match any category above]
}
```

Rules:
- Use the **exact category name** from the list above (e.g. "DFT", not "Density Functional Theory").
- If an input method matches multiple categories, include all that apply.
- If an input method does not match any category, include it in "other" using the original input name.
- If the input has no methods at all, return `{"matched_methods": [], "other": []}`.
- Return valid JSON only. No explanation, no markdown fences.
