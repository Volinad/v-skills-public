---
name: youtube-transcript
description: >
  Extract subtitles and transcripts from YouTube videos by URL. Works with manual
  and auto-generated captions in any language. No API keys or subscriptions required.

  Use this skill whenever the user wants to get text from a YouTube video — whether
  they want to read it, summarize it, analyze it, search for something in it, or
  process it in any way. Trigger on: YouTube URLs (youtube.com, youtu.be), requests
  for transcripts/subtitles/captions, or when the user mentions "видео", "ролик",
  "субтитры", "транскрипт" in the context of extracting text from video content.

  Also trigger when the user provides a YouTube link and asks ANY question about
  the video's content — the transcript is the fastest way to answer without watching.
  Even if the user doesn't explicitly say "transcript", if they say things like
  "what does this video talk about", "summarize this YouTube video", or "find where
  they mention X in this video", use this skill to get the text first.
---

# YouTube Transcript Extraction

Extract transcripts from YouTube videos. In Claude Code (with Bash), uses a bundled
Python script. In environments without Bash (Claude.ai, Claude desktop app), falls
back to browser tools or guides the user to copy the transcript manually.

**Pick your path based on available tools:**

1. **Bash available** (Claude Code) → use the bundled script (fastest, most reliable)
2. **Browser MCP tools available** (Claude in Chrome, etc.) → open YouTube and extract
   transcript from the page
3. **Neither available** (Claude.ai chat) → ask the user to paste the transcript

## Prerequisites

Install the dependency (once):

```bash
pip install youtube-transcript-api
```

On macOS with system Python you may need `--break-system-packages`. Omit if using
a virtualenv.

If the import fails at runtime, install it automatically before retrying.

## Quick Start

The script lives at `scripts/yt_transcript.py` (relative to this skill's directory).

### Single video — plain text (most common)

```bash
python <skill-path>/scripts/yt_transcript.py "https://youtube.com/watch?v=VIDEO_ID"
```

This prints the full transcript to stdout. Capture it for further processing
(summarization, analysis, search).

### Single video — with timestamps

```bash
python <skill-path>/scripts/yt_transcript.py "URL" --format timestamps
```

Output: `[MM:SS] text` lines — useful when the user wants to reference specific
moments in the video.

### Save to file

```bash
python <skill-path>/scripts/yt_transcript.py "URL" --format srt --output subtitle.srt
```

Formats: `text` (default), `timestamps`, `srt`, `json`.

### Multiple videos (batch)

```bash
python <skill-path>/scripts/yt_transcript.py URL1 URL2 URL3 --output ./transcripts/
```

The script adds a 2-second delay between requests to avoid rate limiting.
Adjust with `--delay 5` for longer pauses.

### Language selection

```bash
python <skill-path>/scripts/yt_transcript.py "URL" --languages ru,en,es
```

Default languages: `en`. The script tries languages in order: first manual
captions, then auto-generated, then falls back to whatever is available.

### Using a proxy

```bash
python <skill-path>/scripts/yt_transcript.py "URL" --proxy http://127.0.0.1:8080
```

Useful if YouTube rate-limits the IP or for geo-restricted content.

### Fallback: yt-dlp (when the script fails)

If the bundled script fails (library breakage after a YouTube change, persistent blocks)
and `yt-dlp` is installed, use it as the second tier before falling back to the browser:

```bash
yt-dlp --skip-download --write-subs --write-auto-subs \
  --sub-langs "en.*" --sub-format json3 -o "out.%(ext)s" "URL"
```

Hard-won rules for this path:
- **Always `json3`, never VTT/SRT** — auto-generated VTT repeats every line twice (rolling
  captions); json3 is the only clean source. Flatten `events[].segs[].utf8` to text.
- **429 / "Sign in to confirm you're not a bot" = the IP is flagged. STOP.** Do not retry
  in a loop — it makes the flag worse. Switch to a proxy or the browser path.
- On the first failure only, try `yt-dlp -U` (YouTube changes break old versions), retry
  once, then stop and move to the next tier.

## Workflow Patterns

### "Summarize this YouTube video"

1. Extract transcript: `python ... "URL"` → capture plain text
2. If text is under ~30k chars, pass it directly to the conversation for summarization
3. If longer, summarize in stages (chunk by timestamps, summarize each, then combine)

### "What does the video say about X?"

1. Extract with timestamps: `--format timestamps`
2. Search through the timestamped text for relevant sections
3. Quote the relevant parts with timestamps so the user can jump to them

### "Get subtitles from these 5 videos"

1. Use batch mode with `--output ./transcripts/`
2. Report success/failure per video
3. Errors for individual videos don't stop the batch

### "Compare what two videos say about X"

1. Extract both transcripts
2. Analyze each for mentions of the topic
3. Present a comparison

## Error Handling

The script handles these errors gracefully:

| Error | Meaning | What happens |
|-------|---------|--------------|
| TranscriptsDisabled | Video owner turned off captions | Script reports it, nothing to extract |
| NoTranscriptFound | No captions in requested language | Auto-retries with any available language |
| VideoUnavailable | Private, deleted, or geo-blocked | Script reports it |
| Import error | youtube-transcript-api not installed | Script tells you to pip install |

## Without Bash (Claude.ai / Claude desktop app)

The bundled Python script requires Bash. If Bash is not available, use these
fallbacks in order:

### Option A: Browser MCP tools

If you have access to browser automation tools (Claude in Chrome, etc.):

1. Navigate to the YouTube video URL
2. Wait for the page to load
3. Click the "..." (More) button below the video
4. Click "Show transcript" (or "Показать расшифровку" in Russian UI)
5. Read the transcript panel text using `get_page_text` or `read_page`
6. Process the extracted text as needed

### Option B: Ask the user to paste

If no browser tools are available either, guide the user:

1. Tell the user: "I can't access YouTube directly in this environment.
   Could you open the video and copy the transcript for me?"
2. Explain how: "On the YouTube video page, click '...' below the video →
   'Show transcript'. Then select all the text and paste it here."
3. Once pasted, process the text (summarize, analyze, search, etc.)

This fallback loses timestamps and language selection, but still lets you
work with the video's content.

## Limitations

- Only works on videos that have captions (manual or auto-generated)
- Auto-generated captions can contain errors, especially for non-English audio
- Live streams in progress may not have transcripts yet
- Age-restricted videos may require cookies (not supported in basic setup)
- Very new videos (< 1 hour old) may not have auto-captions generated yet
- YouTube may rate-limit after ~100 requests/day from the same IP — use `--proxy` or spread requests over time
