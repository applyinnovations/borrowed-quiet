# Borrowed Quiet

An original, restrained horror mod for ordinary Minecraft survival.
Sometimes the work continues after you stop.

Version **1.0.0** is accepted for the supported environment below. See the
[final readiness decision](docs/final-readiness.md) and
[hash-bound acceptance dossier](evidence/acceptance.json).
The complete [scope](docs/specification.md) was committed before implementation.

## Player setup

Target: Minecraft Java **26.2**, Java **25**, Fabric Loader **0.19.3** and
[Fabric API **0.152.0+26.2**](https://modrinth.com/mod/fabric-api).
The validation platform is Linux x86-64. Nix and AI services are **not** player
dependencies. Use your legitimately installed Minecraft client.

1. Install the matching [Fabric Loader](https://fabricmc.net/use/installer/) into
   a Minecraft 26.2 profile. Start that profile once, then quit.
2. Put `borrowedquiet-1.0.0.jar` and the specified Fabric API jar in that profile's
   `mods` directory. Do not install the developer test harness.
3. Launch the Fabric profile and enter an ordinary local Survival world.

The experience begins quietly: at least two minutes of eligible play before its
first opportunity. Continue mining, building, farming and exploring. It introduces
no required quest, combat enemy, dimension or progression item.

## Comfort and control

Content: implied surveillance, unexplained footsteps/taps, brief abstract shapes.
No gore, speech, flashing lights, forced camera motion, deliberate crashes, damage
or changes to player volume settings. Headphones are optional; subtitles help
identify direction. There is no need to turn the volume up to hear a scare.

Commands require no cheats:

| Command | Effect |
|---|---|
| `/borrowedquiet off` / `on` | Stop / enable the experience |
| `/borrowedquiet gentle` / `normal` / `intense` | Choose spacing; Normal is default |
| `/borrowedquiet volume 0.4` | Mod gain from 0 to 1; default 0.7 |
| `/borrowedquiet visuals false` | Disable the abstract visual encounter |
| `/borrowedquiet reducedmotion true` | Remove its contraction animation |
| `/borrowedquiet status` | Show current settings |

Minecraft's Master and Ambient/Environment sliders also apply. Enable vanilla
subtitles in accessibility settings. Settings live in `config/borrowedquiet.json`
inside the selected game directory. Malformed settings disable the experience and
remain preserved; a settings command stores a valid replacement and keeps the
invalid original as a timestamped backup.

Events operate only in the Overworld, in unpublished local single-player Survival.
Menus, sleep, low health, damage, falling and water/lava immersion interrupt them.
Nether, End, Creative, spectator, remote servers and LAN-published worlds are quiet.
Multiplayer horror, hardcore, shaders, other gameplay mods and custom resource-pack
compatibility are not advertised.

## Disable, remove and troubleshoot

Use `/borrowedquiet off` for an immediate stop that persists across restarts.
To uninstall, quit Minecraft and remove only `borrowedquiet-1.0.0.jar` from `mods`.
The optional configuration file can remain. No saved blocks, items or entities
require conversion. Keep ordinary world backups when changing any mod installation.

An incompatible-mod screen usually means Minecraft, Loader or Fabric API does not
match the specified versions. If nothing happens, check `/borrowedquiet status`,
your mode/dimension and volume controls; several minutes of silence are intentional.
Opening a menu or changing settings interrupts an encounter and starts recovery.
Reopening a world starts a new warm-up. Configuration warnings appear in
`logs/latest.log`.

## Project and validation

See [development](docs/development.md), [research](docs/research-notes.md),
[architecture and rights](docs/architecture-and-rights.md) and
[asset records](assets/register.json). A build alone is not a readiness decision.

```sh
nix flake check --no-update-lock-file
nix build --no-update-lock-file .#default
nix develop --no-update-lock-file --command ./scripts/test-runtime
nix develop --no-update-lock-file --command ./scripts/validate
```

Original work: [MIT](LICENSE). Third-party inputs retain their own terms.
This is not an official Minecraft product and is not approved by or associated
with Mojang or Microsoft.
