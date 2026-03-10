# v1.3.0 - Audio Experience and Interactive Controls

## Added

- **Background audio** (`docs/assets/audio/`)
  - Two tracks: *Digital Bloom 1* and *Digital Bloom 2*
  - Automatic cycling with 2.5 s crossfade between tracks
  - Play / Pause, Previous / Next track controls
  - Seekable progress bar and volume slider

- **Audio visualiser**
  - 18-bar real-time FFT spectrum displayed in the audio strip

- **Audio Reactivity mode** (♪ Sync button)
  - Bass frequencies drive blob displacement amplitude in real-time
  - The blob "breathes" and pulses in sync with the music

- **Control panel** (right side)
  - Color A / Color B pickers — change gradient colours live in the GLSL shader
  - Noise Scale slider — tune blob shape from smooth to spiky
  - Animation Speed slider
  - Point Size slider
  - Bloom Intensity and Bloom Radius sliders
  - Screenshot button — saves the current frame as a PNG

- **Start overlay** — satisfies browser autoplay policy; click once to begin
