{
  description = "Borrowed Quiet: complete pinned build, runtime and inspection environment";

  inputs.nixpkgs.url = "https://releases.nixos.org/nixpkgs/nixpkgs-26.11pre1068924.42f17a57f4f6/nixexprs.tar.xz";

  outputs =
    { nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
      cudaPkgs = import nixpkgs {
        inherit system;
        config = {
          allowUnfree = true;
          cudaSupport = true;
          cudaCapabilities = [ "12.0" ];
        };
      };
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
      modPackage =
        pkgs.runCommand "borrowedquiet-1.0.0"
          {
            nativeBuildInputs = [
              pkgs.jdk25
              pkgs.python3
            ];
          }
          ''
            mkdir -p "$out"
            python3 ${./scripts/build-java.py} ${./src} ${compileDeps} "$out/borrowedquiet-1.0.0.jar"
          '';
    in
    {
      packages.${system} = {
        audio-review-engine = cudaPkgs.llama-cpp;
        audio-review-model-v3 = pkgs.fetchurl {
          url = "https://huggingface.co/ggml-org/Qwen3-Omni-30B-A3B-Instruct-GGUF/resolve/6e35a28f4a19b18730f8949b0c579c6429649ab8/Qwen3-Omni-30B-A3B-Instruct-Q4_K_M.gguf";
          sha256 = "d9e2876556e7873e02c0359f832432ee2d67ab7dd0cee3efe0f77fd7a1f4dd85";
        };
        audio-review-projector-v3 = pkgs.fetchurl {
          url = "https://huggingface.co/ggml-org/Qwen3-Omni-30B-A3B-Instruct-GGUF/resolve/6e35a28f4a19b18730f8949b0c579c6429649ab8/mmproj-Qwen3-Omni-30B-A3B-Instruct-bf16.gguf";
          sha256 = "f0dfe825fb692d426362b1ac79678fc08daa4758f7151526cad110515f122883";
        };
        default = modPackage;
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
      checks.${system} = {
        core-and-resources =
          pkgs.runCommand "borrowedquiet-core-resources"
            {
              nativeBuildInputs = [
                pkgs.jdk25
                pkgs.python3
                pkgs.ffmpeg-full
              ];
            }
            ''
              mkdir -p "$out"
              export BQ_EXTRA_CLASSPATH=${modPackage}/borrowedquiet-1.0.0.jar
              python3 ${./scripts/build-java.py} ${./tests/unit} ${compileDeps} tests.jar
              python3 ${./scripts/unit-tests.py} ${compileDeps} "$BQ_EXTRA_CLASSPATH" tests.jar > "$out/unit.txt"
              python3 ${./scripts/check-resources.py} ${./.} "$BQ_EXTRA_CLASSPATH" > "$out/resources.txt"
              python3 ${./scripts/check-asset-reproduction.py} ${./.} > "$out/asset-reproduction.txt"
            '';
        static-analysis =
          pkgs.runCommand "borrowedquiet-static-analysis"
            {
              nativeBuildInputs = [
                pkgs.python3
                pkgs.ruff
                pkgs.shellcheck
                pkgs.google-java-format
                pkgs.nixfmt
              ];
            }
            ''
                  cd ${./.}
                ruff check --no-cache scripts assets
                ruff format --no-cache --check scripts assets
              shellcheck scripts/preflight scripts/probe-capture scripts/probe-listening scripts/review-assets scripts/test-runtime scripts/validate
              shellcheck --shell=bash scripts/cuda-driver-env
                  google-java-format --dry-run --set-exit-if-changed $(find src/java tests -name '*.java')
                  nixfmt --check flake.nix
                  mkdir -p "$out"
                  echo PASS > "$out/static.txt"
            '';
        preflight-tools =
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
      };
      devShells.${system}.default = pkgs.mkShell {
        shellHook = ''
          source ${./scripts/cuda-driver-env}
        '';
        BQ_DBUS_CONFIG = "${pkgs.dbus}/share/dbus-1/session.conf";
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
        packages =
          with pkgs;
          [
            jdk25
            google-java-format
            git
            curl
            jq
            python3
            ffmpeg-full
            sox
            pulseaudio
            dbus
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
          ]
          ++ [ cudaPkgs.llama-cpp ];
      };
    };
}
