# Initial research notes — 8 September 2026

Status: initial research only. No scope specification has been committed or implemented;
the mandatory capability gate remains open. No selected production assets exist.

## Evidence and its limits

- **Research synthesis and theory:** [Grupe and Nitschke (2013)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4276319/)
  link anticipation of uncertain threats with anxiety and propose an integrated model.
  This concerns anxiety research; it does not establish a reliable recipe for enjoyable game horror.
- **Theory:** [Miller, White and Scrivner](https://pubmed.ncbi.nlm.nih.gov/38104602/)
  propose predictive processing as an explanation of engagement with horror.
  Treat changes in expectations as a design resource, not a validated fear algorithm.
- **Empirical field study:** [Andersen et al. (2020)](https://pure.au.dk/ws/files/219262042/0956797620972116.pdf)
  report an inverted-U relationship between fear and enjoyment across repeated self-reports
  at a haunted attraction. A population result in that setting cannot specify an individual
  Minecraft player's preferred intensity or optimal event intervals.
- **Practitioner experience:** [Thomas Grip, “9 Years, 9 Lessons on Horror”](https://frictionalgames.com/2019-10-9-years-9-lessons-on-horror/)
  discusses restrained scare frequency, environmental interpretation, consistent worlds,
  incomplete information, narrative, and agency. His recommendation to reduce engaging
  ordinary mechanics should not be adopted wholesale: this brief explicitly preserves survival.
- **Practitioner reference located, full talk not reviewed:** [Alistair Hope, “Building Fear in Alien: Isolation”](https://www.gdcvault.com/play/1021852/Building-Fear-in-Aliens).
  The session abstract describes an underpowered player, creature senses, and audiovisual immersion.
  Reading the abstract is not equivalent to inspecting the lecture or its demonstrations.

## Preliminary design inferences, not a committed scope

Ordinary survival already provides player-chosen objectives. Horror could reinterpret
the sounds and spaces surrounding those objectives. A repeated acoustic motif could
suggest an unseen presence; changes in its distance or response to activity could imply intent.
The experience would need bounded event duration, substantial recovery, variation that
survives repeat exposure, and dependable player controls. These are design hypotheses.

Potential observable criteria include timecoded periods of anticipation and recovery,
sound-source movement in recorded playback, recognizable but non-identical motifs,
and successful completion of survival tasks during natural scheduling. Neither event
logs nor an AI's interpretation would measure human fear or enjoyment.

No claim is made that the required complete reference study or creative rationale is finished.

## Technical sources inspected

- [Minecraft 26.2 release](https://www.minecraft.net/en-us/article/minecraft-java-edition-26-2)
  and [26.3 pre-release 2](https://www.minecraft.net/de-de/article/minecraft-26-3-pre-release-2).
  Mojang's live version manifest also reported release `26.2`, snapshot `26.3-pre-2`.
- [Fabric version-matched porting guidance](https://docs.fabricmc.net/develop/porting/)
  confirms a maintained 26.2 path. Loader/toolchain selection is not yet committed.
- [Fabric automated tests](https://docs.fabricmc.net/develop/automatic-testing)
  were located for feasibility; no game tests have been implemented or run.
- [Nix flakes](https://nix.dev/concepts/flakes.html),
  [flake check](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-check),
  [develop](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-develop).
  Locking an input is distinct from proving reproducible outputs.
- [Minecraft EULA](https://www.minecraft.net/en-us/eula): a mod must not redistribute
  the game, and access to a downloadable client is not evidence of an owned game licence.
- [Official trial](https://www.minecraft.net/en-us/free-trial): the documented flow requires
  Microsoft sign-in and provides approximately 100 minutes of in-game time. It is not
  sufficient evidence for unrestricted multi-hour survival validation.
