# Images, Sound, and Compression

Beyond numbers and text, computers routinely store images, audio, and video. Each type has its own encoding scheme—but all ultimately reduce to binary numbers stored in memory or on disk. This lesson explains exactly how those encodings work and why compression is indispensable.

## Images

### Pixels and the Raster Model

A digital image is a **raster** (grid of pixels). Each **pixel** (picture element) stores one color value. The image's **resolution** is described as width × height in pixels (e.g., 1920 × 1080 = Full HD).

### RGB Color Encoding

The most common color model represents each pixel as three numbers:

- **R** (Red intensity): 0–255
- **G** (Green intensity): 0–255
- **B** (Blue intensity): 0–255

That is 3 bytes (24 bits) per pixel. You can produce **256³ = 16,777,216** distinct colors—enough that the human eye cannot distinguish adjacent steps.

| Color | R | G | B | Hex code |
|-------|---|---|---|----------|
| White   | 255 | 255 | 255 | `#FFFFFF` |
| Black   |   0 |   0 |   0 | `#000000` |
| Pure red| 255 |   0 |   0 | `#FF0000` |
| Pure green |  0 | 255 |   0 | `#00FF00` |
| Pure blue  |  0 |   0 | 255 | `#0000FF` |
| Yellow  | 255 | 255 |   0 | `#FFFF00` |
| Sky blue | 135 | 206 | 235 | `#87CEEB` |

**Worked calculation:** How much space does a raw 1920 × 1080 RGB image require?
1,920 × 1,080 = 2,073,600 pixels × 3 bytes = **6,220,800 bytes ≈ 6 MB**

A 4K image (3840 × 2160) is 4× more pixels, so about **24 MB** uncompressed.

### Beyond RGB

- **RGBA** adds an **alpha (transparency)** channel: 4 bytes per pixel. Alpha=0 is fully transparent; alpha=255 is fully opaque. Used in PNG files for logos, icons, and UI elements that overlay other content.
- **Greyscale** uses a single byte per pixel (0 = black, 255 = white). Used in scientific imaging and some photographs.
- **RAW camera formats** use 12–16 bits per channel (instead of 8) to capture more dynamic range before processing.
- **Vector graphics** (SVG) describe shapes with mathematical formulas—lines, curves, fill colors—instead of pixels. Resolution-independent and often smaller for icons and logos; cannot represent photographs.

### How Color Mixing Works

RGB is an *additive* color model: mixing full R + full G + full B gives white (like mixing light beams). The opposite model, **CMYK** (Cyan, Magenta, Yellow, Black), is *subtractive* and is used in printing.

## Audio

### Analog vs Digital Sound

Sound is a pressure wave traveling through air. Your ear detects variations in air pressure; a microphone converts those variations to a continuously-varying electrical voltage. A computer cannot store a continuous signal—it must *sample* it.

### Analog-to-Digital Conversion (ADC)

**Sampling** takes snapshots of the voltage at regular intervals. The **sample rate** (measured in Hz = samples per second) determines how accurately rapid changes are captured.

The **Nyquist-Shannon theorem** states that to faithfully reproduce a signal of frequency *f*, you must sample at least at **2f**. Human hearing goes up to about 20 kHz, so 44,100 Hz (CD quality) comfortably captures all audible frequencies.

| Parameter | What it means | Typical values |
|-----------|--------------|----------------|
| **Sample rate** | Samples per second (Hz) | 8,000 Hz (phone), 44,100 Hz (CD), 48,000 Hz (video), 96,000 Hz (studio) |
| **Bit depth** | Bits per sample = dynamic range | 8-bit (256 levels), 16-bit (65,536 levels), 24-bit (studio) |
| **Channels** | Mono (1) or stereo (2) or surround (5.1) | 1–8 |

**Storage calculation: CD-quality stereo audio**

44,100 samples/sec × 16 bits × 2 channels = 1,411,200 bits/sec = 176,400 bytes/sec ≈ **10 MB per minute**

A 74-minute CD therefore holds about 740 MB of raw audio data.

### Quantisation Noise

Each sample is rounded to the nearest integer level. This rounding error introduces a subtle background hiss called **quantisation noise**. Higher bit depth means more levels and less audible noise—which is why professional audio uses 24-bit instead of 16-bit.

## Why Compression Is Essential

| Raw data | Size |
|----------|------|
| 1920×1080 RGB image | ~6 MB |
| 1 min CD-quality stereo audio | ~10 MB |
| 1 min Full HD video (30 fps) | 6 MB × 30 × 60 = **~10.8 GB** |

A 2-hour movie would require roughly **1.3 TB** uncompressed. Compression makes digital media practical.

## Lossless vs Lossy Compression

| Type | What it does | Use case | Example formats |
|------|-------------|---------|-----------------|
| **Lossless** | Exact bit-for-bit reconstruction; no data lost | Documents, source code, archives, medical images | PNG, FLAC, ZIP, GZIP |
| **Lossy** | Permanently discards data humans cannot easily perceive; much smaller files | Photos, music, video for distribution | JPEG, MP3, AAC, H.264 |

The choice depends on the use case. A medical X-ray must be lossless; a streaming music file does not.

## Run-Length Encoding (Simple Lossless Technique)

**Idea:** instead of storing every value individually, record *runs* of the same value.

```
Raw pixels:    W W W W W W B B B W W W W
RLE encoding:  6W 3B 4W
```

13 values compressed to 6 characters. Works well for images with large areas of solid color (logos, icons, screenshots). This is the core idea behind GIF and classic fax compression.

For photographic images with smooth gradients, there are few long runs, so RLE is not effective.

## How JPEG Works (Conceptually)

JPEG exploits two facts about human vision:
1. The eye is more sensitive to **luminance** (brightness) differences than **chrominance** (color) differences.
2. Smooth gradients are more visually important than fine high-frequency detail.

JPEG compression steps:
1. **Color space conversion** — convert RGB to YCbCr (luminance + two color channels).
2. **Chrominance downsampling** — reduce color information by 2× (the eye barely notices).
3. **Block division** — split image into 8×8 pixel blocks.
4. **DCT (Discrete Cosine Transform)** — transform each block from pixel values to frequency components. The result separates "smooth" low frequencies (important) from "fine" high frequencies (less important).
5. **Quantization** — divide frequency coefficients by a quality-dependent table, rounding small values to zero. **This is where data is permanently lost.**
6. **Entropy coding (Huffman)** — losslessly compress the quantized values.

A higher JPEG "quality" setting uses finer quantization steps, preserving more detail at the cost of a larger file. At very low quality, the 8×8 block structure becomes visible—this is called *blocking artifact*.

## How MP3 Works (Conceptually)

MP3 uses **psychoacoustics**—models of human auditory perception—to remove audio information that is inaudible:

1. **Masking** — a loud sound makes nearby quieter sounds inaudible. MP3 reduces or removes those masked sounds.
2. **Absolute hearing threshold** — some frequencies require high volume before humans can hear them; sounds below this threshold are discarded.
3. **Frequency band splitting** — the audio is split into 32 sub-bands; each is quantized independently based on perceptual importance.
4. **Huffman coding** — lossless final compression.

Result: MP3 achieves roughly **10:1 compression** (from ~10 MB/min to ~1 MB/min) with little perceptible quality loss at typical bit rates.

## Choosing the Right Format

| Use case | Recommended format | Why |
|----------|-------------------|-----|
| Web photograph | JPEG | Lossy, small, good for smooth gradients |
| Logo / icon with transparency | PNG | Lossless, supports alpha channel |
| Screenshot / diagram | PNG | Sharp edges; JPEG creates visible artifacts |
| Music archive | FLAC | Lossless, preserves original quality |
| Music for streaming | AAC or MP3 | Lossy but good quality-to-size ratio |
| Video streaming | H.264 or H.265 | Efficient lossy video codec |
| Archiving files | ZIP or GZIP | Lossless general-purpose compression |

## Common Misconceptions

**"PNG is always better than JPEG."**
PNG is lossless and is better for images with text, sharp edges, and transparency. JPEG is better for photographs with smooth color gradients where tiny losses are imperceptible. Using PNG for a photograph produces a much larger file with no visible quality improvement.

**"Compressing a file multiple times makes it smaller each time."**
Lossless compression has a limit; compressing a ZIP file again produces no gain and may slightly increase size (the compressed data looks random, not compressible). Lossy compression applied repeatedly degrades quality each time—this is called *generation loss*.

**"Higher bit depth = better photo."**
Bit depth affects dynamic range (the difference between the darkest and brightest representable tones), not sharpness. Increasing bit depth from 8 to 16 helps with dark-room editing but is imperceptible in a finished photo viewed on a standard screen.

## Key Takeaways

- A pixel is typically 3 bytes (RGB); a 1920×1080 image requires ~6 MB raw.
- Audio is sampled thousands of times per second (44,100 Hz for CD quality); bit depth determines dynamic range.
- **Lossless compression** (PNG, FLAC, ZIP) preserves every bit; **lossy compression** (JPEG, MP3) discards imperceptible data for much smaller files.
- JPEG exploits limits in human color sensitivity and uses DCT + quantization; MP3 exploits auditory masking.
- Choose PNG for sharp/transparent images, JPEG for photos; FLAC for archiving audio, MP3/AAC for streaming.
