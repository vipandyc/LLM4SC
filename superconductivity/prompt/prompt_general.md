Here are some competing unconventional superconducting mechanisms: (with explanation)

(a) Coupling with phonons.
(a1) Unconventional superconductivity is solely driven by electron-phonon coupling.
- Only BCS theory, or some generalization beyond BCS theory.
(a2) Unconventional superconductivity is driven by bipolarons induced by strong electron-phonon coupling.
- Includes study on bipolarons rather than pure BCS electron phonon coupling.

(b) Electronic fluctuation.
(b1) Unconventional superconductivity is driven by anti-ferromagnetic (AFM) spin fluctuation.
(b2) Unconventional superconductivity is driven by ferromagnetic (FM) spin fluctuation.
- AFM and FM fluctuation may coexist and compete, ok to give positive scores to both, if applicable.
(b3) Unconventional superconductivity is driven by fluctuation of charge density wave (CDW).
- Breakdown of CDW phases focusing on charge, but not spin.
(b4) Unconventional superconductivity is driven by nematic spin fluctuation or orbital fluctuation.
- Driven by nematicity instead of AFM or FM. Also includes orbital fluctuation, since orbital fluctuation can induce nematic fluctuation.
(b5) Unconventional superconductivity is driven by plasmon/overscreening mechanism.
- Driven by effective electron–electron attraction mediated by collective charge oscillations (plasmons) or by overscreening in systems with extremely large dielectric response.

(c) Strong electronic coupling.
(c1) Unconventional superconductivity is solely driven by strong correlation of electrons.
- Contrary to spin fluctuation, superconductivity emerges purely from attraction from strong electron correlation, or large effective U/t, or flat electron band.
(c2) Unconventional superconductivity is driven by spin liquid-related electron correlation.
- Different from all above, here includes magnetic frustration, absence of long-range magnetic order, resonating valence bond (RVB) mechanisms, fractional quasiparticles, anyon superconductivity and chiral spin liquids. More broadly, pairing emerging from a quantum-disordered magnetic state rather than a conventional AFM/FM background.


Input: text: str

Arguments:
    - text: str; The title and abstract of a paper.

Requested output: A JSON dictionary with the following keys:
{
  "system": str,
  "model": str,
  "pure el-ph coupling": float,
  "bipolaron el-ph coupling": float,
  "AFM fluctuation": float,
  "FM fluctuation": float,
  "charge density wave": float,
  "nematic fluctuation": float,
  "plasmon fluctuation": float,
  "pure el correlation": float,
  "spin liquid el correlation": float.
}

Keys:
    - "system": str
        Brief description of the physical/material system studied.
        If not applicable or unable to determine, use "N/A".
        Example: "FeSe; Fe-based superconductor"
    
    - "model": str
        The theoretical model or/and method used in the paper.
        If not applicable or unable to determine, use "N/A".
        Example: "Hubbard model", "Density functional theory", "Dynamical mean field theory"
    
    - "pure el-ph coupling": float
        Opinion score from 0 to 5 for mechanism "(a1) Unconventional superconductivity is solely driven by electron-phonon coupling."
        Key words: "electron–phonon coupling", "phonon-mediated pairing", "BCS", "Eliashberg", "Debye frequency", "λ (el-ph coupling constant)", "Migdal", "phonon glue".

    - "bipolaron el-ph coupling": float
        Opinion score from 0 to 5 for mechanism "(a2) Unconventional superconductivity is driven by bipolarons induced by strong electron-phonon coupling."
        **Keywords**: "bipolaron", "polaronic pairs", "strong el-ph coupling forms bipolarons", "localized pairs", "polaron band", "polaronic superconductivity".
    
    - "AFM fluctuation": float
        Opinion score from 0 to 5 for mechanism "(b1) Unconventional superconductivity is driven by anti-ferromagnetic (AFM) spin fluctuation."
        **Keywords**: "AFM fluctuation", "antiferromagnetic fluctuations", "near AFM order", "spin fluctuation mediated pairing", "paramagnon", "AFM QCP".
    
    - "FM fluctuation": float
        Opinion score from 0 to 5 for mechanism "(b2) Unconventional superconductivity is driven by ferromagnetic (FM) spin fluctuation."
        **Keywords**: "ferromagnetic fluctuation", "FM fluctuations", "near ferromagnetic order", "triplet pairing from FM fluctuations", "Stoner instability".

    - "charge density wave": float
        Opinion score from 0 to 5 for mechanism "(b3) Unconventional superconductivity is driven by fluctuation of charge density wave (CDW)."
        **Keywords**: "charge density wave", "CDW", "CDW quantum critical point", "charge order", "incommensurate charge order", "charge instability", "striped phase".

    - "nematic fluctuation": float
        Opinion score from 0 to 5 for mechanism "(b4) Unconventional superconductivity is driven by nematic spin fluctuation or orbital fluctuation."
        **Keywords**: "nematic fluctuation", "nematicity", "Ising nematic QCP", "orbital fluctuations", "broken rotational symmetry", "electronic nematic order".

    - "plasmon fluctuation": float
        Opinion score from 0 to 5 for mechanism "(b5) Unconventional superconductivity is driven by plasmon/overscreening mechanism."
        **Keywords**: "plasmon-mediated pairing", "overscreening", "dynamical screening", "negative dielectric function", "low carrier density superconductor", "LO phonon–plasmon coupling", "quantum paraelectric", "plasmon mechanism".
    
    - "pure el correlation": float
        Opinion score from 0 to 5 for mechanism "(c1) Unconventional superconductivity is solely driven by strong correlation of electrons."
        **Keywords**: "strongly correlated electrons", "large U/t", "Mott physics", "flat bands", "Hubbard model pairing", "repulsion-induced attraction", "correlated insulator", "pure electronic mechanism", "local Coulomb repulsion drives pairing".

    - "spin liquid el correlation": float
        Opinion score from 0 to 5 for mechanism "(c2) Unconventional superconductivity is driven by spin liquid-related electron correlation."
        **Keywords**: "spin liquid", "quantum spin liquid", "RVB (resonating valence bond)", "magnetic frustration", "no long-range magnetic order", "fractional excitations", "spinons", "holons", "chiral spin liquid", "anyonic superconductivity", "fractional statistics".        

Notes:
    - A score of 5 means strong support.
    - A score of 0 means not relevant, or not supporting.
    - It is possible to score all mechanisms as 0, i.e. all not relevant, for example papers discussing topological superconductivity, or extending superconductivity to other subfields like high-energy physics and fluids.
    - If uncertain of the score of the mechanism, assign 0. If unable to extract a clear mechanism into these categories above, assign 0 for all mechanisms.

Below are some examples with abstract, and the expected output. Reasoning (which justifies the output) may be given to you when appropriate, but don't include it in your output.
