# Local engine

`venv` links to the installed Python environment containing `unswbc` 1.2.7 and
its packaged WebAssembly game engine. This is the engine symlink explicitly
allowed by the setup brief; keep that installation present on this Mac.

Call `./play.sh` from the workspace. All arguments and commands can use local
paths. Its driver uses the engine's own `EngineModule`, `Pool`, and `Bot` with
native binaries, since the fixed opponent is a native executable. Bots receive
the engine's standard stdin/stdout protocol. Native mode has the engine's wall
timeout but does not measure the judge's WebAssembly CPU-point budget. A seed
repeats pearl randomness; a native bot's independent randomness may differ.

The shell invokes `nice -n 15`; the driver verifies its priority and stops before
starting a game if the OS refuses to set it. The driver holds one of two shared
kernel `flock` slots in `.locks/` throughout engine loading, play, bot cleanup,
and replay/result writing. Concurrent direct driver and wrapper calls use those
same slots. Keep these lock files in place.

Each empty output directory receives `game.replay`, `result.json`, `result.txt`,
and `engine.log`. The JSON contains timing, actual priority, all final length
metrics, the winning rule, map corrections, and bot runtime errors. Existing
nonempty output directories are rejected so earlier results stay intact.
