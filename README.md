# Borrowed Quiet

An original, restrained horror mod for ordinary Minecraft survival.
Sometimes the work continues after you stop.

[Download Borrowed Quiet 1.0.0 (.jar)](https://github.com/applyinnovations/borrowed-quiet/releases/download/v1.0.0/borrowedquiet-1.0.0.jar)
· [Release notes and checksum](https://github.com/applyinnovations/borrowed-quiet/releases/tag/v1.0.0)

Version **1.0.0** is accepted for the supported environment below. See the
[final readiness decision](docs/final-readiness.md) and
[hash-bound acceptance dossier](evidence/acceptance.json).
The complete [scope](docs/specification.md) was committed before implementation.

## Installation

Target: Minecraft Java **26.2**, Java **25**, Fabric Loader **0.19.3** and
[Fabric API **0.152.0+26.2**](https://modrinth.com/mod/fabric-api).
The validation platform is Linux x86-64. Nix and AI services are **not** player
dependencies. Use your legitimately installed Minecraft client.

1. **Download the mod jar.** Get
   [borrowedquiet-1.0.0.jar](https://github.com/applyinnovations/borrowed-quiet/releases/download/v1.0.0/borrowedquiet-1.0.0.jar),
   or open the [v1.0.0 release](https://github.com/applyinnovations/borrowed-quiet/releases/tag/v1.0.0)
   and select that file under **Assets**. Do not extract the jar. GitHub's **Code →
   Download ZIP** downloads source code, not an installable mod. No build tools are
   needed for the release download. If GitHub returns 404, sign in and verify you
   have access to this repository; private-repository assets require access too.
2. **Prepare Minecraft.** Use a legitimate Minecraft Java installation and back up
   any existing worlds. Create a separate Minecraft **26.2** profile/game directory
   for the first installation. Its runtime must use **Java 25**.
3. **Install Fabric.** Use the [Fabric installer](https://fabricmc.net/use/installer/)
   or your launcher's Fabric installation option, selecting Minecraft **26.2** and
   Fabric Loader **0.19.3**. This is a Fabric mod, not a Forge/NeoForge mod. Start
   the Fabric profile once, then quit Minecraft.
4. **Install both jars.** Download **Fabric API 0.152.0+26.2** from the link above.
   Open the selected profile's game directory using your launcher. Inside its
   `mods` folder (create it if absent), place the Fabric API jar and
   `borrowedquiet-1.0.0.jar`. Keep them directly in `mods`, not a nested folder.
   Do not install the source/evidence ZIPs or developer test harness. Fabric Loader
   and Fabric API are separate requirements; installing one does not install both.
5. **Launch and verify.** Select that Fabric profile, enter a local Survival world
   in the Overworld, and run `/borrowedquiet status` in chat. The command requires
   no cheats. It should show the mod's settings; `/borrowedquiet on` enables it if
   previously disabled. Leave the world unpublished to LAN.

For a standard Linux launcher installation the game directory is usually
`~/.minecraft`, but separate launcher instances can use another directory. Always
use the directory belonging to the profile you actually launch. Install this
client-side mod in the client, not on a dedicated server.

The accepted jar's SHA-256 is:

```text
2133042d444e80d3e072ea7b1354adc3dbdd1e6b72a1dada12f8b5081f228b87
```

### Build the installable jar from this repository

This option is for developers using the [documented Nix environment](docs/development.md)
on Linux x86-64. Players receiving the built jar do **not** need Nix.

```sh
git clone git@github.com:applyinnovations/borrowed-quiet.git
cd borrowed-quiet
nix build --no-update-lock-file .#default
```

The output is `result/borrowedquiet-1.0.0.jar`. Install it using steps 2–5 above;
building does not install Fabric API or modify your Minecraft profile.

### What to expect

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
match the specified versions. An unknown `/borrowedquiet` command means the client
has not registered the mod: check the selected Fabric profile and its `mods` folder,
then inspect `logs/latest.log` for a loading error. If nothing happens despite a
working command, check `/borrowedquiet status`,
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
