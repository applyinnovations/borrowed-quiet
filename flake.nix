{
  description = "Minecraft horror project: prerequisite capability environment";

  inputs.nixpkgs.url = "https://releases.nixos.org/nixpkgs/nixpkgs-26.11pre1068924.42f17a57f4f6/nixexprs.tar.xz";

  outputs =
    { nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
      runtimeLock = builtins.fromJSON (builtins.readFile ./deps/runtime.json);
      jarInputs = builtins.filter (f: pkgs.lib.hasSuffix ".jar" f.path) runtimeLock.files;
      fetched = map (f: {
        inherit (f) path;
        file = pkgs.fetchurl { inherit (f) url sha256; };
      }) jarInputs;
      compileDeps =
        pkgs.runCommand "minecraft-fabric-26.2-dependencies" { nativeBuildInputs = [ pkgs.unzip ]; }
          ''
            mkdir -p "$out"
            ${pkgs.lib.concatMapStringsSep "\n" (
              f: ''mkdir -p "$out/$(dirname '${f.path}')"; ln -s '${f.file}' "$out/${f.path}"''
            ) fetched}
            unzip -q "$out/mods/fabric-api.jar" 'META-INF/jars/*' -d "$out/api"
          '';
    in
    {
      packages.${system} = {
        compile-deps = compileDeps;
        audio-review-model = pkgs.fetchurl {
          url = "https://huggingface.co/ggml-org/Qwen2.5-Omni-7B-GGUF/resolve/89b785438c8901d4635e42f50480ba5985a1bbf1/Qwen2.5-Omni-7B-Q4_K_M.gguf";
          hash = "sha256-CYg9/1MdxWkjoEHJyZx8d54m/94yyqg63ut1Auw7UP4=";
        };
        audio-review-projector = pkgs.fetchurl {
          url = "https://huggingface.co/ggml-org/Qwen2.5-Omni-7B-GGUF/resolve/89b785438c8901d4635e42f50480ba5985a1bbf1/mmproj-Qwen2.5-Omni-7B-f16.gguf";
          hash = "sha256-ftBis18V88TKzaxy1SkdsvkI8Xi6T7GeIQtVXyM+Bp0=";
        };
      };
      checks.${system}.preflight-tools =
        pkgs.runCommand "preflight-tools"
          {
            nativeBuildInputs = with pkgs; [
              jdk25
              ffmpeg-full
              jq
              shellcheck
            ];
          }
          ''
            shellcheck ${./scripts/preflight}
            shellcheck ${./scripts/probe-capture}
            shellcheck ${./scripts/probe-listening}
            java -version 2>&1 | grep 'version "25\.'
            ffmpeg -nostdin -v error -f lavfi -i sine=duration=1:sample_rate=48000 \
              -ac 1 -c:a libvorbis probe.ogg
            ffprobe -v error -show_streams -of json probe.ogg \
              | jq -e '.streams | length == 1 and .[0].codec_name == "vorbis" and .[0].channels == 1'
            ffmpeg -nostdin -v error -i probe.ogg -f null -
            mkdir -p "$out"
            echo 'PASS: script lint, Java 25, mono Vorbis encode/inspect/decode. No runtime or listening claim.' > "$out/result.txt"
          '';
      devShells.${system}.default = pkgs.mkShell {
        LIBGL_DRIVERS_PATH = "${pkgs.mesa}/lib/dri";
        LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
          pkgs.mesa
          pkgs.libglvnd
          pkgs.libX11
          pkgs.libXcursor
          pkgs.libXrandr
          pkgs.libXinerama
          pkgs.libXi
          pkgs.libXxf86vm
          pkgs.libXrender
          pkgs.libXext
          pkgs.libxkbcommon
          pkgs.wayland
          pkgs.alsa-lib
          pkgs.libpulseaudio
          pkgs.openal
          pkgs.flite
        ];
        packages = with pkgs; [
          jdk25
          gradle
          git
          curl
          jq
          python3
          ffmpeg-full
          sox
          pulseaudio
          xdpyinfo
          xorg-server
          xdotool
          mesa-demos
          shellcheck
          nixfmt
          ruff
          time
          procps
          unzip
          zip
          llama-cpp
        ];
      };
    };
}
