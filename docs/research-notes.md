# Initial research notes — 8 September 2026

Status: design research completed; resulting commitments are in
[the pre-implementation specification](specification.md). Research does not establish
that this particular mod will frighten anyone. No human playtesting is claimed.

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

## Additional first-hand and cross-media study

- **Practitioner interview:** [Alistair Hope, PlayStation Blog](https://blog.playstation.com/archive/2014/03/26/behind-terror-alien-isolation-exclusive-interview)
  describes a single credible threat, response to player noise/light, multiple
  survival approaches, and horror continuing while the creature is offscreen.
  His account of Alien's lived-in design connects withholding with coherent
  production design. Adopt offscreen implication and contextual response; reject
  a compulsory lethal pursuer, borrowed creature and scripted campaign. The GDC
  abstract was inspected, but its embedded talk did not expose playable media.
  This complete primary interview is the substantive first-hand replacement, not
  a claim to have viewed the inaccessible lecture.
- **Filmmaker interview:** [Kiyoshi Kurosawa on Cloud](https://embed.letterboxd.com/journal/kiyoshi-kurosawa-cloud-interview/)
  explains using environmental sound instead of rhythmic score during violence,
  and keeping interacting people in a shared spatial frame. Adopt clear spatial
  relationships and diegetic sound; reject gunshot intensity as a horror shortcut.
  This is practitioner testimony, not an experiment or a claim to have screened
  the full film. No film imagery or soundtrack is selected as an asset.
- **Primary literary work:** [H. G. Wells, The Red Room](https://www.gutenberg.org/files/23218/23218-h/23218-h.htm)
  was read as a study in a narrator's changing interpretation of ordinary space.
  The room and attempts at reassurance become sources of anticipation; the ending
  refuses a simple visible ghost. Adopt interpretive uncertainty; reject helpless
  loss of lighting and physical injury, which would interfere with Minecraft work
  and imply world malfunction. No text is copied.

## Creative rationale — the agent's design inferences

Ordinary survival already provides player-chosen objectives. Horror could reinterpret
the sounds and spaces surrounding those objectives. A repeated acoustic motif could
suggest an unseen presence; changes in its distance or response to activity could imply intent.
The experience would need bounded event duration, substantial recovery, variation that
survives repeat exposure, and dependable player controls. These are design hypotheses.

Potential observable criteria include timecoded periods of anticipation and recovery,
sound-source movement in recorded playback, recognizable but non-identical motifs,
and successful completion of survival tasks during natural scheduling. Neither event
logs nor an AI's interpretation would measure human fear or enjoyment.

The chosen grammar is **imitation, answer, partial embodiment**. Borrowed Pace makes
the player's own stopping meaningful; The Other Wall implies a listener rather than
random ambient noise; The Fold offers a limited interpretation without a compulsory
fight. All three share original dry material sounds. Long quiet intervals preserve
attention to survival, while recognition changes an event and provides agency.
These are hypotheses to inspect against the timecoded rubric, not validated
psychological parameters. Six bounded one-shots and one restrained shape are the
complete content; variance comes from context, position, timing and response.

## Technical sources inspected

- [Minecraft 26.2 release](https://www.minecraft.net/en-us/article/minecraft-java-edition-26-2)
  and [26.3 pre-release 2](https://www.minecraft.net/de-de/article/minecraft-26-3-pre-release-2).
  Mojang's live version manifest also reported release `26.2`, snapshot `26.3-pre-2`.
- [Fabric version-matched porting guidance](https://docs.fabricmc.net/develop/porting/)
  confirms a maintained 26.2 path. The specification selects Loader/API and direct
  Java compilation against the unobfuscated client, without a mapping pipeline.
- [Fabric automated tests](https://docs.fabricmc.net/develop/automatic-testing)
  informed an actual separately launched graphical client GameTest. A compiled
  test jar generated a world and moved the player 8.37 blocks. This is a capability
  result, not a mod feature test.
- [Nix flakes](https://nix.dev/concepts/flakes.html),
  [flake check](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-flake-check),
  [develop](https://nix.dev/manual/nix/stable/command-ref/new-cli/nix3-develop).
  Locking an input is distinct from proving reproducible outputs.
- [Minecraft EULA](https://www.minecraft.net/en-us/eula): a mod must not redistribute
  the game, and access to a downloadable client is not evidence of an owned game licence.
- [Official trial](https://www.minecraft.net/en-us/free-trial): the documented flow requires
  Microsoft sign-in and provides approximately 100 minutes of in-game time. It is not
  sufficient evidence for unrestricted multi-hour survival validation.
