# BUTCH GRAVES 3D — Developer notes

How to swap in your own music and voices, how the engine and its tools work, and how to build the game. For how to
play, see the [manual](MANUAL.md); for how the project was made and tested, see the [README](README.md).

## Using your own music, sounds and voices

All audio is looked up through **`/snd/sounds.txt` inside the JAR**. To swap sounds:

1. Open the `.jar` with 7-Zip or WinRAR (it's a ZIP file).
2. Drop your files in (any folder, e.g. `snd/`).
3. Edit `snd/sounds.txt` and point the keys at your files, e.g.
   `music.level1 = /snd/my_metal_song.mid` or `voice.kill1 = /snd/my_line.wav`.
4. Leave a value empty (`voice.kill1 =`) to silence that sound.
5. If you install with the `.jad`, update its `MIDlet-Jar-Size:` to the new JAR size (or install the `.jar` alone).

The file type comes from the extension: `.mid`, `.wav`, `.amr`, `.mp3`, `.aac` (whatever your phone supports).
Tip: 8 kHz mono WAV works almost everywhere; AMR is ~5x smaller for voice if your phone plays it.

Keys: `music.title, music.story, music.level1..level20, music.win, music.dead, music.cutscene`, 56 `sfx.*` keys and
88 `voice.*` keys (Butch's lines plus the cutscene voices of both styles), all listed in the file.

## How it works

- **Renderer** (`src/E.java`): fixed-point DDA raycaster (no floats, CLDC 1.0 safe) with Wolfenstein-style sliding doors and
  pushwall secrets, scrolling conveyor, river, waterfall and lava textures, flashing shock floors and spike floors,
  per-cell textured floors and ceilings (row casting), a 360° panoramic sky, distance fog and a Doom-style 32-level colormap
  that fades to the fog's own colour (deep green in the jungle, white in San Lazaro, blood red in the Other World),
  per-cell lighting baked from jack-o'-lanterns/candles/lamps with flicker, lightning flashes, muzzle and explosion lights,
  palette flashes for damage and pickups, z-buffered billboard sprites (with 50% translucency for ghosts), particles,
  a Doom-style screen melt, and a strip-based upscaler for the low detail modes.
- **Memory**: art is split into a small always-loaded pack (`res/d.bin`: palette, weapons, effects, pickups) and ~200 asset
  groups (`res/g/*.bin`). Each level file lists the groups it needs, and the engine unloads the previous level's art before
  loading the next, so a level never holds more than ~390 KB of art even though the game has five episodes of it.
- **Cutscenes** (`src/G.java`): scripted in code and played in the real engine. Actors are ordinary billboard sprites
  moved by the script, with camera moves, voice lines, subtitles, sound cues, screen shake and fades. Close-ups draw a
  pre-rendered portrait (two mouth frames for lip flap) with the same scaler as the weapon, over a rotating rays backdrop.
  Long lines get a taller subtitle band, and cutscenes, story pages and the level-clear screen ignore fire until it has
  been released, so a held or hammered fire button never skips anything.
- **Art**: every monster, weapon, prop and Butch himself was modelled as signed-distance-field geometry and ray-marched in Python
  (`tools/sdf.py`, `monsters*.py`, `props*.py`, `weapons.py`, `hero.py`), like Doom's photographed clay
  models. Butch's guns are held high enough that his bare hands (leather wrist straps, knuckles) show on every frame, and
  the gun and hands are never shaded darker than half-lit, so they don't vanish in a dark corridor or the fog
  (`test/sim/WpnShow.java` renders every frame in-game at several light levels). Textures and skies are procedural
  (`tools/textures*.py`). Dead monsters' eyes go dark. Everything shares one 256-colour palette:
  223 shaded colours plus 31 "fullbright" colours (glowing eyes, fire, stained glass) that stay bright in the dark.
- **Audio**: original General-MIDI soundtrack composed in code (`tools/gen_audio*.py`): surf-horror, a broken
  calliope waltz, swamp blues, a gothic invention, circus metal, spooky synthwave, an industrial machine groove, synth-metal,
  a brassy adventure march over jungle drums, a Spanish-tinged guitar and marimba groove, slow foggy trip-hop with a music
  box that's out of tune with everything else, and a war-drum ritual in E Phrygian for the last boss. The title theme opens with Bach's Toccata in D minor
  (public domain). The level-clear jingle is a quiet spooky-lounge tune (vibraphone over harpsichord and organ).
  Sound effects are synthesized. Butch's voice is espeak-ng with the MBROLA us2 voice run through ffmpeg (pitch down,
  telephone EQ, hard compression, slap echo, a little grit) for that crunchy 90s sound. The other characters and the
  talking monsters use Kokoro, a small neural text-to-speech model (`tools/tts.py`), through similar ffmpeg chains, with
  espeak-ng as the fallback when Kokoro isn't installed.
  The sound engine runs on a background worker with a watchdog: it always silences the WAV effects before stopping or
  switching the MIDI music (doing it the other way round deadlocks the audio on many phones), drops late effects instead of
  queueing them, and replaces a worker that hangs inside the phone's audio API. It keeps at most five effect players open.
  The player's gun gets a second copy of its sound instead of stopping and restarting the one still playing (many
  emulators silently ignore that restart), and its shots skip the queue. The music comes first. Some phones stop the MIDI
  on their own: they take its channel for one effect too many, or ignore the loop count and stop at the end of the track.
  The engine notices (the player's state, and whether its media clock still runs), starts the music again where it
  stopped, and from then on plays only as many effects at once over it as the phone has channels for. When effects can't
  play over the MIDI at all, they are skipped while music plays; when the audio hangs while both play, the effects back
  off (fewer players, then none but the gun's and no voices over the music), never the music. Without music, effect
  hangs shrink the player pool and finally turn effects off for the session; music that hangs while starting gets
  another try on the next level, as does everything else. Opening a new effect player while the MIDI plays is the riskiest thing a phone
  does, so the engine rations it: your gun always gets one, getting hurt, pickups, explosions, bosses and traps may open
  one twice a second, and everything else (growls, hits, clicks) plays only if its player is already open or nothing has
  been opened for over a second; a busy sound in its first seconds is never evicted for a minor one. Butch's pain grunts
  are spaced out too. In a minute of boss fight this opens about 60 players instead of about 180. The boss tracks and the
  busiest level tracks are also thinned (`tools/thin_midi.py`: chords keep two notes, kick and hi-hats play eighths, 16th-note
  riffs play eighths) so the phone's synth has CPU to spare for the effects; every part and melody is still there.
  `test/snd/run.sh`, `test/snd/rungun.sh` and `test/snd/runboss.sh` (a minute of boss fight) check all this against a fake
  MMAPI that models those phone failures (deadlocks, hangs, resource limits, no mixing, lost restarts, the music's channel
  taken for an effect, loop counts ignored); `runboss.sh` reports how much of the fight the music really played.
- **Levels** (`tools/gen_levels*.py`): built in code, validated (enclosure, door orientation, key/exit reachability, including
  teleporters, both lever states of the shifting walls, jumps over pits, and the escape after the idol is lifted) and checked in a desktop simulator (`test/sim`) that runs a bot
  through every level at every difficulty.

## Building

Requirements: JDK 8 (javac with `-source 1.3 -target 1.3`), a MIDP 2.0 / CLDC 1.0 API jar, ProGuard (for preverification).

```
./build.sh            # full version  -> dist/ButchGraves3D.jar/.jad
LITE=1 ./build.sh     # no voices     -> dist/ButchGraves3D_lite.jar/.jad
```
Edit the `TC=` paths at the top of `build.sh`. In NetBeans (Java ME), create a MIDP 2.0 / CLDC 1.0 project,
copy `src/` and `res/` in, and set the MIDlet class to `BG`.

Regenerating assets (Python 3 + numpy + Pillow; for voices: ffmpeg, espeak-ng + mbrola-us2/us3/en1, and for the other
characters Kokoro (`pip install kokoro-onnx` and the
`kokoro-v1.0.onnx` + `voices-v1.0.bin` model files from the kokoro-onnx GitHub releases, in `tools/kokoro/` or
`$KOKORO_DIR`; `BG_TTS=espeak` skips it)):
```
cd tools
python3 gen_sprites.py     # SDF renders -> tools/spr (takes a few minutes)
python3 gen_hero.py        # Butch's faces and title bust
python3 gen_pack.py        # palette, textures, sprites -> res/d.bin + res/g/*.bin + src/Res.java + HUD/title PNGs
python3 gen_levels.py      # res/l1..l20.bin and the cutscene sets l101..l105 (+ map previews in tools/out)
python3 gen_audio.py       # episode 1 audio -> res/snd/*
python3 gen_audio2.py      # episode 2/3 + cutscene audio
python3 gen_audio3.py      # episode 4 audio
python3 gen_audio4.py      # episode 5 audio, and the full sounds.txt
```

The pictures in the manual are made by `tools/manual_maps.py` (the level maps, from the level builders) and
`tools/manual_art.py` (the sprite tiles, from `tools/spr`).
