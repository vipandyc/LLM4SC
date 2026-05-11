*Example 1*

Input: Anisotropic bipolaron flat bands, Hall mobility edge, and metal-semiconductor duality in overdoped high-Tc oxides.

The hole bipolaron band structure is derived for oxide superconductors, yielding two flat anisotropic bands. The strong anisotropy produces effectively one-dimensional localization in a random field, which accounts for the metal-like value of the Hall effect together with the semiconductorlike doping dependence of resistivity in overdoped oxides. The same picture explains the doping dependence of Tc and λH(0), the low-temperature behavior of resistivity and of the Hall effect, the temperature dependence of Hc2(T), and robust features observed in angle-resolved photoemission spectroscopy of several high-Tc copper oxides.

Output: {"system": "cuprates; oxides", "model": "N/A", "pure el-ph coupling": 0, "bipolaron el-ph coupling": 5, "AFM fluctuation": 0, "FM fluctuation": 0, "charge density wave": 0, "nematic fluctuation": 0, "plasmon fluctuation": 0, "pure el correlation": 0, "spin liquid el correlation": 0}.

*Example 2*

Input: Intermetallic compounds containing f-electron elements exhibit a rich variety of superconducting phases and are prime candidates for unconventional pairing with complex order-parameter symmetries. For instance, superconductivity has been observed both at the border of magnetic order and deep inside ferromagnetically and antiferromagnetically ordered states, suggesting that magnetism may promote rather than destroy superconductivity. Superconducting phases situated near valence transitions or in the vicinity of magnetopolar order are candidates for novel pairing interactions — for example, fluctuations of the conduction-electron density or of the crystal electric field, respectively. The experimental status of the study of the superconducting phases of f-electron compounds is reviewed.

Output: {"system": "f-electron compounds", "model": "N/A", "pure el-ph coupling": 0, "bipolaron el-ph coupling": 0, "AFM fluctuation": 4, "FM fluctuation": 4, "charge density wave": 0, "nematic fluctuation": 0, "plasmon fluctuation": 0, "pure el correlation": 0, "spin liquid el correlation": 0}.

*Example 3*

Input: We propose a scenario in which a quantum critical point associated with the formation of incommensurate charge-density waves underlies the principal properties of the high-temperature superconducting cuprates in both their normal and superconducting phases. The singular interaction that develops near this charge-driven quantum critical point produces the non-Fermi-liquid behavior that is universally observed at optimal doping. The same interaction drives d-wave Cooper pair formation, yielding a superconducting critical temperature that varies strongly with doping in the overdoped regime and exhibits a plateau in the optimally doped regime. In the underdoped regime, a pairing potential that depends on temperature promotes local pair formation without global superconducting coherence, leading to an unusual temperature dependence of the pseudogap and to a non-trivial relation between the pairing temperature and the gap magnitude. This latter feature is in good qualitative agreement with previously unexplained aspects of the experiments.

Output: {"system": "cuprates", "model": "N/A", "pure el-ph coupling": 0, "bipolaron el-ph coupling": 0, "AFM fluctuation": 0, "FM fluctuation": 0, "charge density wave": 5, "nematic fluctuation": 0, "plasmon fluctuation": 0, "pure el correlation": 0, "spin liquid el correlation": 0}.

*Example 4*

Input: We study a low Tc metallic superconductor weakly coupled to the soft fluctuations that arise from proximity to a nematic quantum critical point (NQCP). We show that: (1) a BCS–Eliashberg treatment remains valid except within a parametrically narrow interval surrounding the NQCP, (2) the symmetry of the superconducting state (d wave, s wave, p wave) is typically set by noncritical interactions, while the nematic fluctuations enhance Tc across all pairing channels, and (3) in two dimensions this enhancement increases as criticality is approached until the weak-coupling description breaks down, whereas in three dimensions the enhancement is substantially weaker.

Output: {"system": "N/A", "model": "N/A", "pure el-ph coupling": 0, "bipolaron el-ph coupling": 0, "AFM fluctuation": 0, "FM fluctuation": 0, "charge density wave": 0, "nematic fluctuation": 5, "plasmon fluctuation": 0, "pure el correlation": 0, "spin liquid el correlation": 0}.

*Example 5*

Input: We show that several distinct order parameters can serve to characterize a class of P- and T-violating phases in spin systems, which we designate chiral-spin states. A closely related, precise notion of chiral-spin-liquid states is also identified. Soluble models are constructed, based on P- and T-symmetric local-spin Hamiltonians, that possess chiral-spin ground states. Mean-field theories that give rise to chiral spin liquids are proposed. Frustration is essential for the stabilization of these states. The quantum numbers of quasiparticles in the vicinity of the chiral spin liquids are analyzed, and these quasiparticles generally obey fractional statistics. On the basis of these ideas, we speculate that superconducting states exhibiting unusual values of the flux quantum may exist.

Output: {"system": "N/A", "model": "N/A", "pure el-ph coupling": 0, "bipolaron el-ph coupling": 0, "AFM fluctuation": 0, "FM fluctuation": 0, "charge density wave": 0, "nematic fluctuation": 0, "plasmon fluctuation": 0, "pure el correlation": 0, "spin liquid el correlation": 5}.

*Example 6*

Input: We used ultrafast optical spectroscopy to probe the quasiparticle relaxation dynamics of the iron-based superconductor CsCa2Fe4As4F2 (Tc ∼ 29 K). A pseudogap (PG = 3.3 ± 0.3 meV) was found to open below T* ≈ 60 K, preceding the development of the superconducting gap Δ(0) = 6.6 ± 0.4 meV. At high excitation fluence a coherent A1g phonon mode at 5.49 THz was observed, showing deviations from purely anharmonic behavior below Tc. The electron-phonon coupling constant for this mode was estimated as λA1g ≈ 0.23. These results shed light on the interplay among electron-phonon interactions, the pseudogap, and the superconducting pairing mechanism in CsCa2Fe4As4F2.

Reasoning: el-ph coupling constant is studied and linked to superconductivity, but the tone is not as strong, so a score of 2 is given.

Output: {"system": "CsCa2Fe4As4F2; Fe-based superconductor", "model": "N/A", "pure el-ph coupling": 2, "bipolaron el-ph coupling": 0, "AFM fluctuation": 0, "FM fluctuation": 0, "charge density wave": 0, "nematic fluctuation": 0, "plasmon fluctuation": 0, "pure el correlation": 0, "spin liquid el correlation": 0}.

*Example 7*

Input: Frustration-Induced Superconductivity in the t-t’ Hubbard Model

The two-dimensional Hubbard model is widely regarded as containing the essential physics behind high-Tc superconductivity in cuprate materials, yet definitive proof remains lacking. Competing magnetic orders, in particular, can strongly contend with superconducting phases. In this work we investigate the ground-state behavior of the doped two-dimensional t-t’ Hubbard model on a square lattice using the infinite projected entangled-pair state method with either U(1) or SU(2) spin symmetry. The U(1) formulation accommodates antiferromagnetic orders, whereas the SU(2) implementation excludes them; contrasting results between these symmetries therefore yield a detailed picture of how magnetism influences superconductivity. The inclusion of a 𝑡′ term introduces particle–hole asymmetry and thus enables a systematic comparison between electron- and hole-doped regimes. We show that (i) a positive 𝑡′/𝑡 markedly enhances superconducting order parameters; (ii) beyond a sufficiently large doping, the t−t′ Hubbard model prefers a uniform superconducting state over stripe states that exhibit charge and spin modulations; and (iii) increasing magnetic frustration—either by strengthening next-nearest-neighbor couplings or by raising the charge doping—suppresses stripe order and promotes superconductivity.

Reasoning: Magnetic frustration gives the most positive score (3) to "spin liquid el correlation" compared to AFM fluctuation and CDW (only briefly mentioned and expressed weak opinion).

Output: {"system": "N/A", "model": "Hubbard model", "pure el-ph coupling": 0, "bipolaron el-ph coupling": 0, "AFM fluctuation": 1, "FM fluctuation": 0, "charge density wave": 1, "nematic fluctuation": 0, "plasmon fluctuation": 0, "pure el correlation": 0, "spin liquid el correlation": 3}.

*Example 8*

Input: Unconventional superconductivity that cannot be accounted for by weak electron–phonon coupling has been realized intrinsically in a two-dimensional superlattice formed by stacking two graphene sheets with a small relative twist. At twist angles near 1.1°—the first “magic” angle—the electronic band structure of this twisted bilayer graphene develops flat bands close to zero Fermi energy, producing correlated insulating phases at half-filling. When the system is electrostatically doped away from these correlated insulators, we detect tunable zero-resistance states with a superconducting critical temperature reaching up to 1.7 kelvin. The resulting temperature versus carrier-density phase diagram closely resembles that of copper oxide superconductors (cuprates), featuring dome-shaped regions associated with superconductivity. Additionally, quantum oscillations observed in the longitudinal resistance reveal small Fermi surfaces in the vicinity of the correlated insulating states, analogous to those seen in underdoped cuprates. The comparatively high superconducting Tc in twisted bilayer graphene, given the very small Fermi surface (corresponding to a carrier density of about 10^11 per square centimetre), ranks it among materials with the strongest electron pairing strengths. As a precisely tunable, purely carbon-based, two-dimensional superconductor, twisted bilayer graphene provides an ideal platform for studying strongly correlated phenomena and may offer insights relevant to the physics of high-critical-temperature superconductors and quantum spin liquids.

Reasoning: The abstract suggests superconducting phase in graphene superlattices could arise from strong pairing strength between electrons, this corresponds best to "pure el correlation" and "spin liquid el correlation", though not directly, so a score of 2 and 2 are assigned.

Output: {"system": "Magic-angle graphene superlattices", "model": "N/A", "pure el-ph coupling": 0, "bipolaron el-ph coupling": 0, "AFM fluctuation": 0, "FM fluctuation": 0, "charge density wave": 0, "nematic fluctuation": 0, "plasmon fluctuation": 0, "pure el correlation": 2, "spin liquid el correlation": 2}.

*Example 9*

Input: Signatures of superconductivity near 80 K in a nickelate under high pressure

Although high-transition-temperature (high-Tc) superconductivity in cuprates has been recognized for more than three decades, its microscopic origin remains unknown1,2,3,4. Cuprates are, to date, the only class of unconventional superconductors that display bulk superconductivity with Tc exceeding the liquid-nitrogen boiling point of 77 K. In this work, high-pressure electrical resistance and mutual inductive magnetic susceptibility measurements reveal superconducting signatures in single crystals of La3Ni2O7, reaching a maximum Tc of 80 K at pressures between 14.0 GPa and 43.5 GPa. Under these high-pressure conditions the superconducting state adopts an orthorhombic structure in the Fmmm space group, in which the  and  orbitals of the Ni cations are strongly hybridized with oxygen 2p orbitals. Our density functional theory calculations show that superconductivity appears concomitantly with the metallization of σ-bonding bands lying below the Fermi level; these bands are formed from the  orbitals together with the apical oxygen ions that link the Ni–O bilayers. Therefore, our findings not only offer significant insight into high-Tc superconductivity in this Ruddlesden–Popper double-layered perovskite nickelate, but also introduce a previously unrecognized family of compounds for probing the mechanism of high-Tc superconductivity.

Reasoning: Only some orbital and band coupling are mentioned, but mechanism is unclear in the abstract. Thus assign 0 support for all mechanisms.

Output: {"system": "La3Ni2O7; Nicklate", "model": "Density functional theory", "pure el-ph coupling": 0, "bipolaron el-ph coupling": 0, "AFM fluctuation": 0, "FM fluctuation": 0, "charge density wave": 0, "nematic fluctuation": 0, "plasmon fluctuation": 0, "pure el correlation": 0, "spin liquid el correlation": 0}.

*Example 10*

Input: Electron–electron and electron–phonon interactions are central to correlated materials, acting as key ingredients for spin, charge and pair correlations. Here we investigate their effects in strongly correlated systems by performing unbiased quantum Monte Carlo simulations of the square-lattice Hubbard–Holstein model at half-filling. We analyze the competition and interplay between antiferromagnetism (AFM) and charge-density wave (CDW) order, establishing a very rich phase diagram. In the regime between AFM and CDW phases we find an enhancement of superconducting pairing correlations, favoring nonlocal s-wave pairs. Our study sheds light on past inconsistencies in the literature, in particular regarding the emergence of CDW in the pure Holstein model.

Reasoning: Electron-phonon interaction and electron on-site U repulsion is considered in the Hubbard-Holstein model simulation, and are thus linked to superconductivity. The superconducting phase is found between AFM and CDW, so superconductivity is the result of competition between AFM and CDW. Given the relation we can assign one score to each.

Output: {"system": N/A", "model": "Hubbard-Holstein model", "pure el-ph coupling": 3, "bipolaron el-ph coupling": 0, "AFM fluctuation": 1, "FM fluctuation": 0, "charge density wave": 1, "nematic fluctuation": 0, "plasmon fluctuation": 0, "pure el correlation": 3, "spin liquid el correlation": 0}.

*Example 11*

Input: We investigate the proximity effect between an s-wave superconductor and the surface states of a strong topological insulator. The induced two-dimensional state closely mimics a spinless p_x + i p_y superconductor, yet it does not break time reversal symmetry. Such a state supports Majorana bound states localized at vortices. We show that linear junctions between superconductors, mediated by the topological insulator, constitute a nonchiral one-dimensional wire for Majorana fermions, and that circuits assembled from these junctions provide a way to create, manipulate, and fuse Majorana bound states.

Reasoning: This work discusses topological insulators and the superconductivity arises from topology. This is unrelated to unconventional superconductivity for our purpose, and should be all N/A or scored 0. Same applies for Majorana.

Output: {"system": N/A", "model": "N/A", "pure el-ph coupling": 0, "bipolaron el-ph coupling": 0, "AFM fluctuation": 0, "FM fluctuation": 0, "charge density wave": 0, "nematic fluctuation": 0, "plasmon fluctuation": 0, "pure el correlation": 0, "spin liquid el correlation": 0}.

*Example 12*

Input: Superconducting vortices carrying a temperature-dependent fraction of the flux quantum

In type-II bulk superconductors, magnetic field enters the material in the form of quantum vortices, each enclosing a magnetic flux equal to the flux quantum. The flux quantum is a universal quantity that depends only on fundamental constants. Using scanning superconducting quantum interference device (SQUID) magnetometry, we examined isolated vortices in the hole-overdoped Ba1−xKxFe2As2 (x = 0.77). At many positions we detected objects that carried only a portion of a flux quantum, with the magnitude of that partial flux changing continuously with temperature. We demonstrated that these objects can be moved and manipulated, and we interpret them as quantum vortices with nonuniversally quantized (fractional) magnetic flux whose value is set by the temperature-dependent parameters of a multicomponent superconductor.

Reasoning: Though related to superconductivity, it’s focusing on device/application or vortex dynamics. Those are not related to the physical mechanisms of unconventional superconductivity.

Output: {"system": N/A", "model": "N/A", "pure el-ph coupling": 0, "bipolaron el-ph coupling": 0, "AFM fluctuation": 0, "FM fluctuation": 0, "charge density wave": 0, "nematic fluctuation": 0, "plasmon fluctuation": 0, "pure el correlation": 0, "spin liquid el correlation": 0}.

*Example 13*

Input: Superconducting ground state of noninteracting particles that obey fractional statistics.

In a previous paper, Kalmeyer and Laughlin argued that the elementary excitations of the original Anderson resonating-valence-bond model might obey fractional statistics. Here we show that an ideal gas composed of such particles constitutes a new kind of superconductor.

Output: {"system": N/A", "model": "N/A", "pure el-ph coupling": 0, "bipolaron el-ph coupling": 0, "AFM fluctuation": 0, "FM fluctuation": 0, "charge density wave": 0, "nematic fluctuation": 0, "plasmon fluctuation": 0, "pure el correlation": 2, "spin liquid el correlation": 5}.

*Example 14* [Resonating–valence-bond theory of phase transitions and superconductivity in La2CuO4-based compounds| Phys. Rev. Lett.]

Input: Resonating–valence-bond description of phase transitions and superconductivity in La2CuO4-based compounds.

We associate the enigmatic high-temperature “twitch” transition in La2CuO4 with the mean-field resonating-valence-bond transition of the Heisenberg model proposed by Baskaran, Zou, and Anderson. The observed structural distortions arise from Coulomb correlations within the pair wave function. In the undoped material the pseudo–Fermi surface of the spin soliton nests, and antiferromagnetic order sets in at 240 K. We conclude with a brief discussion of superconductivity and the character of the excitations in this system.

Output: {"system": La2CuO4; cuprate", "model": "N/A", "pure el-ph coupling": 0, "bipolaron el-ph coupling": 0, "AFM fluctuation": 0, "FM fluctuation": 0, "charge density wave": 0, "nematic fluctuation": 0, "plasmon fluctuation": 0, "pure el correlation": 2, "spin liquid el correlation": 5}.

*Example 15*

Input: Spin-triplet superconductivity from excitonic effect in doped insulators.

Spin-triplet superconductors, while central to fundamental physics and of potential use in topological quantum computing, remain scarce in solid-state materials despite decades of research. Here we introduce a three-particle mechanism for spin-triplet superconductivity in multiband systems, in which an effective attraction between doped electrons is generated from the Coulomb repulsion via a virtual interband transition that involves a third electron [V. Cr´epel, L. Fu, Sci. Adv. 7, eabh2233 (2021)]. The theory is controlled analytically by an interband hybridization parameter and is demonstrated explicitly for doped band insulators using an extended Hubbard model. Our exciton-mediated pairing framework shows how, in principle, a two-particle bound state can emerge from strong electron repulsion upon doping, thereby opening a viable route to Bose–Einstein condensate (BEC)–Bardeen–Cooper–Schrieffer (BCS) physics in solid-state systems. Motivated by this theory, we propose that recently discovered dilute superconductors such as ZrNCl, WTe2, and moir´e materials can host spin-triplet pairing, and we compare the expected consequences of our proposal with available experimental data.

Output: {"system": N/A", "model": "extended Hubbard model", "pure el-ph coupling": 0, "bipolaron el-ph coupling": 0, "AFM fluctuation": 0, "FM fluctuation": 0, "charge density wave": 1, "nematic fluctuation": 1, "plasmon fluctuation": 0, "pure el correlation": 4, "spin liquid el correlation": 0}.

*Example 16*

Input: Superconductivity at very low density: The case of strontium titanate.

When doped, strontium titanate becomes superconducting down to carrier concentrations as low as n = 5×10^17 cm−3, a regime in which the Fermi energy is many orders of magnitude smaller than the longitudinal optical phonon frequencies. In this low-density limit the only optical excitation with a characteristic frequency below the Fermi energy is the plasmon. Unlike in conventional metals, the effective interaction is weak because the crystal provides strong screening, which makes it possible to formulate a controlled theory of plasmon-mediated superconductivity. We demonstrate that pairing driven solely by the plasmon can reproduce the experimentally observed transition temperatures only if the crystal’s dielectric screening is reduced in lightly doped samples relative to the insulating material. We furthermore identify distinctive signatures of the plasmon pairing mechanism that should appear in the tunneling density of states above the superconducting gap.

Output: {"system": SrTiO3", "model": "N/A", "pure el-ph coupling": 0, "bipolaron el-ph coupling": 0, "AFM fluctuation": 0, "FM fluctuation": 0, "charge density wave": 0, "nematic fluctuation": 0, "plasmon fluctuation": 5, "pure el correlation": 0, "spin liquid el correlation": 0}.

*Example 17*

Input: By solving the gap equation numerically from first principles, we have examined the mechanism of superconductivity in n-type semiconducting SrTiO3. The experimentally observed transition temperature, as a function of carrier density and applied stress, is reproduced quite well when the calculation includes both the plasmon and the polar optic phonon associated with the stress-induced ferroelectric transition. The conduction band of SrTiO3 is taken to follow the single-valley model proposed by Mattheiss, and all physical input parameters—effective mass, dielectric constant, and phonon dispersion relation—are taken from experimental measurements, so that the theory contains no adjustable parameters. The effect of other phonons, such as the acoustic modes, was also evaluated and found to be small.

Output: {"system": SrTiO3", "model": "first principle", "pure el-ph coupling": 5, "bipolaron el-ph coupling": 0, "AFM fluctuation": 0, "FM fluctuation": 0, "charge density wave": 0, "nematic fluctuation": 0, "plasmon fluctuation": 5, "pure el correlation": 0, "spin liquid el correlation": 0}.

*Example 18*

Input: We demonstrate the existence of bound two-electron states in an almost depleted two-dimensional island. These paired states are supported by particular compact arrangements of four single-electron levels. Their formation does not require phonon mediation and is driven solely by the disorder-induced potential relief together with the electron-electron (Coulomb) repulsion. We estimate the density of such two-electron states and describe how they evolve with applied magnetic field.

Output: {"system": N/A", "model": "N/A", "pure el-ph coupling": 0, "bipolaron el-ph coupling": 0, "AFM fluctuation": 0, "FM fluctuation": 0, "charge density wave": 0, "nematic fluctuation": 0, "plasmon fluctuation": 0, "pure el correlation": 5, "spin liquid el correlation": 0}.

*Example 19*

Input: Bipolaronic superconductivity.

Superconducting behavior of narrow-band electrons is analyzed in the strong-coupling limit. It is demonstrated that bipolarons—localized spatially nonoverlapping Cooper pairs formed by a strong electron-phonon interaction—can, under certain conditions, display superconducting properties characteristic of superfluid charged Bose systems. These bipolarons constitute an example of the "molecular" superconductivity proposed by Schafroth, Butler, and Blatt [Helv. Phys. Acta 30 93 (1957)]. The Meissner effect and the penetration depth of bipolaronic superconductors are investigated, and the relationship between Bardeen-Cooper-Schrieffer superconductors and bipolaronic ones is discussed.

Output: {"system": N/A", "model": "N/A", "pure el-ph coupling": 0, "bipolaron el-ph coupling": 5, "AFM fluctuation": 0, "FM fluctuation": 0, "charge density wave": 0, "nematic fluctuation": 0, "plasmon fluctuation": 0, "pure el correlation": 0, "spin liquid el correlation": 0}.

*Example 20*

Input: Spin-fluctuation-mediated even-parity pairing in heavy-fermion superconductors.

We show that antiferromagnetic spin fluctuations observed in heavy-fermion solids favor anisotropic even-parity pairings, while they suppress both odd-parity pairings and isotropic even-parity pairings.

Reasoning: Even-parity pairing, and it mentioned "...impeded by antiferromagnetic fluctuation", so it is pure FM fluctuation.

Output: {"system": N/A", "model": "N/A", "pure el-ph coupling": 0, "bipolaron el-ph coupling": 0, "AFM fluctuation": 5, "FM fluctuation": 0, "charge density wave": 0, "nematic fluctuation": 0, "plasmon fluctuation": 0, "pure el correlation": 0, "spin liquid el correlation": 0}.

*Example 21*

Input: Quantum critical points (QCPs), where a second-order phase transition is continuously tuned to zero temperature, are currently a central focus of solid-state physics1,2. The intense interest stems from the observation of striking phenomena at QCPs, notably the emergence of unconventional superconductivity (SC)3. While QCPs associated with the suppression of magnetic order are relatively common and have been studied extensively, QCPs originating from structural transitions are rare and remain poorly explored. Here we report the observation of a charge density wave (CDW) type of structural ordering in LuPt2In, which undergoes a second-order transition at TCDW = 490 K. Gradual substitution of Pd for Pt suppresses TCDW continuously to T = 0, producing a QCP at 58% Pd substitution. We observe a strong enhancement of bulk SC precisely at this QCP, pointing to a novel type of interaction between CDW and SC.

Output: {"system": LuPt2In", "model": "N/A", "pure el-ph coupling": 0, "bipolaron el-ph coupling": 0, "AFM fluctuation": 0, "FM fluctuation": 0, "charge density wave": 5, "nematic fluctuation": 0, "plasmon fluctuation": 0, "pure el correlation": 0, "spin liquid el correlation": 0}.

*Example 22*

Input: We employ determinantal quantum Monte Carlo to calculate the properties of a lattice model of spin itinerant electrons as it is tuned through a quantum phase transition into an Ising nematic phase. Nematic fluctuations drive superconductivity, producing a broad superconducting dome that encloses the nematic quantum critical point. For temperatures above , we observe strikingly non-Fermi liquid behavior, including a "nodal–antinodal dichotomy" reminiscent of that seen in several transition metal oxides. Moreover, the critical fluctuations strongly influence the low-frequency optical conductivity, yielding behavior consistent with "bad metal" phenomenology.

Output: {"system": N/A", "model": "determinantal quantum Monte Carlo", "pure el-ph coupling": 0, "bipolaron el-ph coupling": 0, "AFM fluctuation": 0, "FM fluctuation": 0, "charge density wave": 0, "nematic fluctuation": 5, "plasmon fluctuation": 0, "pure el correlation": 0, "spin liquid el correlation": 0}.

*Example 23*

Input: Ferromagnetic Spin Fluctuation Induced Superconductivity in Sr2RuO4.
We present a quantitative model for triplet superconductivity in Sr2RuO4 based on first-principles calculations of the electronic structure and the magnetic susceptibility. In this framework superconductivity is driven by ferromagnetic spin fluctuations that are strong at small wave vectors. The calculated effective mass renormalization, the renormalized susceptibility, and the superconducting critical temperature are all in good agreement with experiment. The superconducting order parameter is of comparable magnitude on all three sheets of the Fermi surface.

Output: {"system": Sr2⁢RuO4", "model": "first principles", "pure el-ph coupling": 0, "bipolaron el-ph coupling": 0, "AFM fluctuation": 0, "FM fluctuation": 5, "charge density wave": 0, "nematic fluctuation": 0, "plasmon fluctuation": 0, "pure el correlation": 0, "spin liquid el correlation": 0}.
