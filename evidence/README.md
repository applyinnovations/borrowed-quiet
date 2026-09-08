# Acceptance evidence and rights

`acceptance.json` is the package-bound readiness decision and requirement matrix.
Its absence or a decision other than `ACCEPTED` is not a release pass.

`runtime/` contains captured Minecraft sessions, test reports, metrics, screenshots
and logs; `reviews/` contains acoustic measurements, complete model observations
and directly inspected visual contact sheets. These large files are included in
the separate evidence archive, rather than committed as development inputs.
All evidence paths in the final matrix carry SHA-256 digests.

Minecraft visuals, sounds and music appearing in gameplay recordings remain the
property of their respective rights holders. They are inspection footage shared
under the Minecraft usage guidelines, **not MIT-licensed replacement game assets**.
No Minecraft executable, library, extracted texture/music library, generated save,
account token, model weight or developer cache is included. Standalone listening
excerpts containing vanilla audio are reconstructed locally from the videos when
needed, not distributed as a sound pack. Original mod sounds and geometry retain
their separately documented MIT licence.

`preflight/` and `capability/` are historical capability experiments, not evidence
that the finished mod passed. Rejected early listening/capture findings are marked
in the project refinement record and must not be substituted for final reviews.
