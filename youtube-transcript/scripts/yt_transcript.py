#!/usr/bin/env python3
"""
YouTube transcript extractor (youtube-transcript-api v1.x).

Usage:
    python yt_transcript.py <url_or_id> [options]

Options:
    --languages LANG1,LANG2   Preferred languages in priority order (default: en)
    --format FORMAT           Output format: text (default), timestamps, srt, json
    --output FILE             Save output to file instead of stdout
    --proxy URL               HTTP/HTTPS proxy URL (e.g., http://proxy:8080)

Batch mode (multiple URLs):
    python yt_transcript.py <url1> <url2> ... [options]
    --delay SECONDS           Delay between requests in batch mode (default: 2.0)

Examples:
    python yt_transcript.py "https://youtube.com/watch?v=dQw4w9WgXcQ"
    python yt_transcript.py dQw4w9WgXcQ --format timestamps
    python yt_transcript.py url1 url2 url3 --format srt --output transcripts/
    python yt_transcript.py <url> --proxy http://127.0.0.1:8080
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from typing import Optional, List, Dict

try:
    from youtube_transcript_api import (
        YouTubeTranscriptApi,
        TranscriptsDisabled,
        NoTranscriptFound,
        VideoUnavailable,
    )
    from youtube_transcript_api.formatters import TextFormatter, SRTFormatter
    from youtube_transcript_api.proxies import GenericProxyConfig
except ImportError:
    print("ERROR: youtube-transcript-api not installed.", file=sys.stderr)
    print("Run: pip install youtube-transcript-api", file=sys.stderr)
    sys.exit(1)


def extract_video_id(url: str) -> Optional[str]:
    """Extract video ID from any YouTube URL format."""
    patterns = [
        r'(?:youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})',
        r'(?:youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'(?:youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        r'(?:youtube\.com/shorts/)([a-zA-Z0-9_-]{11})',
        r'(?:youtube\.com/live/)([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url.strip()):
        return url.strip()
    return None


def build_api(proxy: Optional[str] = None) -> YouTubeTranscriptApi:
    """Create API instance, optionally with proxy."""
    if proxy:
        proxy_config = GenericProxyConfig(http_url=proxy, https_url=proxy)
        return YouTubeTranscriptApi(proxy_config=proxy_config)
    return YouTubeTranscriptApi()


def _find_best_transcript(transcript_list, languages: Optional[List[str]] = None):
    """
    Find the best transcript from a TranscriptList.

    If languages is provided, tries manual → auto-generated in that order.
    Always falls back to any available transcript as last resort.
    If languages is None or empty, skips language-specific search entirely.
    """
    if languages:
        # 1. Try manual transcripts in preferred languages
        for lang in languages:
            try:
                return transcript_list.find_manually_created_transcript([lang])
            except Exception:
                continue

        # 2. Fall back to auto-generated in preferred languages
        for lang in languages:
            try:
                return transcript_list.find_generated_transcript([lang])
            except Exception:
                continue

    # 3. Last resort — take whatever is available
    for t in transcript_list:
        return t

    return None


def get_transcript(video_id: str, languages: Optional[List[str]] = None, proxy: Optional[str] = None) -> Dict:
    """
    Fetch transcript for a YouTube video.

    Args:
        video_id: 11-char YouTube video ID
        languages: Preferred language codes in priority order (default: ['en']).
                   Pass an empty list to skip language preference and take any available.
        proxy: HTTP/HTTPS proxy URL

    Returns dict with: video_id, language, is_generated, segments, plain_text
    """
    if languages is None:
        languages = ['en']

    api = build_api(proxy)
    transcript_list = api.list(video_id)

    transcript = _find_best_transcript(transcript_list, languages)
    if transcript is None:
        raise ValueError(f"No transcripts available for video {video_id}")

    fetched = transcript.fetch()

    formatter = TextFormatter()
    plain_text = formatter.format_transcript(fetched)

    segments = []
    for snippet in fetched.snippets:
        segments.append({
            'start': snippet.start,
            'duration': snippet.duration,
            'text': snippet.text,
        })

    return {
        'video_id': video_id,
        'language': fetched.language_code,
        'is_generated': fetched.is_generated,
        'segments': segments,
        'plain_text': plain_text,
    }


def format_timestamps(segments: List[Dict]) -> str:
    """Format segments as [MM:SS] timestamped text."""
    lines = []
    for seg in segments:
        minutes = int(seg['start'] // 60)
        seconds = int(seg['start'] % 60)
        lines.append(f"[{minutes:02d}:{seconds:02d}] {seg['text']}")
    return '\n'.join(lines)


def get_srt(video_id: str, languages: Optional[List[str]] = None, proxy: Optional[str] = None) -> str:
    """Get transcript in SRT format."""
    if languages is None:
        languages = ['en']

    api = build_api(proxy)
    transcript_list = api.list(video_id)

    transcript = _find_best_transcript(transcript_list, languages)
    if transcript is None:
        raise ValueError(f"No transcripts available for video {video_id}")

    fetched = transcript.fetch()
    formatter = SRTFormatter()
    return formatter.format_transcript(fetched)


def process_single(url: str, languages: List[str], fmt: str, proxy: Optional[str] = None) -> Dict:
    """Process a single URL. Returns result dict with 'output' or 'error'."""
    video_id = extract_video_id(url)
    if not video_id:
        return {'url': url, 'error': f'Invalid YouTube URL: {url}'}

    try:
        if fmt == 'srt':
            output = get_srt(video_id, languages=languages, proxy=proxy)
            return {'url': url, 'video_id': video_id, 'output': output, 'format': 'srt'}

        result = get_transcript(video_id, languages=languages, proxy=proxy)

        if fmt == 'timestamps':
            output = format_timestamps(result['segments'])
        elif fmt == 'json':
            output = json.dumps(result, ensure_ascii=False, indent=2)
        else:
            output = result['plain_text']

        return {
            'url': url,
            'video_id': video_id,
            'language': result['language'],
            'is_generated': result['is_generated'],
            'output': output,
            'format': fmt,
            'char_count': len(result['plain_text']),
        }

    except TranscriptsDisabled:
        return {'url': url, 'video_id': video_id, 'error': 'Subtitles are disabled for this video'}
    except VideoUnavailable:
        return {'url': url, 'video_id': video_id, 'error': 'Video is unavailable (private, deleted, or geo-blocked)'}
    except NoTranscriptFound:
        # Retry without language filter — empty list skips language preference
        try:
            if fmt == 'srt':
                output = get_srt(video_id, languages=[], proxy=proxy)
                result = get_transcript(video_id, languages=[], proxy=proxy)
            else:
                result = get_transcript(video_id, languages=[], proxy=proxy)
                if fmt == 'timestamps':
                    output = format_timestamps(result['segments'])
                elif fmt == 'json':
                    output = json.dumps(result, ensure_ascii=False, indent=2)
                else:
                    output = result['plain_text']
            return {
                'url': url,
                'video_id': video_id,
                'language': result['language'],
                'is_generated': result['is_generated'],
                'output': output,
                'format': fmt,
                'char_count': len(result['plain_text']),
                'note': f'Requested languages not found, fell back to {result["language"]}',
            }
        except Exception as e2:
            return {'url': url, 'video_id': video_id, 'error': f'No transcripts found: {e2}'}
    except Exception as e:
        return {'url': url, 'video_id': video_id, 'error': str(e)}


def main():
    parser = argparse.ArgumentParser(description='Extract YouTube video transcripts')
    parser.add_argument('urls', nargs='+', help='YouTube URLs or video IDs')
    parser.add_argument('--languages', default='en', help='Comma-separated language codes (default: en)')
    parser.add_argument('--format', choices=['text', 'timestamps', 'srt', 'json'], default='text', help='Output format')
    parser.add_argument('--output', help='Output file or directory (for batch)')
    parser.add_argument('--proxy', help='HTTP/HTTPS proxy URL')
    parser.add_argument('--delay', type=float, default=2.0, help='Delay between batch requests (default: 2.0)')

    args = parser.parse_args()
    languages = [lang.strip() for lang in args.languages.split(',')]

    results = []
    for i, url in enumerate(args.urls):
        result = process_single(url, languages, args.format, proxy=args.proxy)
        results.append(result)

        if len(args.urls) > 1 and i < len(args.urls) - 1:
            time.sleep(args.delay)

    # Output handling
    if args.output and len(results) > 1:
        os.makedirs(args.output, exist_ok=True)
        for r in results:
            if 'error' in r:
                print(f"FAILED: {r['url']} — {r['error']}", file=sys.stderr)
                continue
            ext = {'text': 'txt', 'timestamps': 'txt', 'srt': 'srt', 'json': 'json'}[r['format']]
            filepath = os.path.join(args.output, f"{r['video_id']}.{ext}")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(r['output'])
            print(f"OK: {r['url']} -> {filepath} ({r.get('char_count', '?')} chars, {r.get('language', '?')})")
    elif args.output and len(results) == 1:
        r = results[0]
        if 'error' in r:
            print(f"ERROR: {r['error']}", file=sys.stderr)
            sys.exit(1)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(r['output'])
        print(f"Saved to {args.output} ({r.get('char_count', '?')} chars, {r.get('language', '?')})", file=sys.stderr)
    else:
        for r in results:
            if 'error' in r:
                print(f"ERROR [{r['url']}]: {r['error']}", file=sys.stderr)
            else:
                if len(results) > 1:
                    print(f"\n=== {r['url']} ({r.get('language', '?')}, {'auto' if r.get('is_generated') else 'manual'}) ===\n")
                print(r['output'])


if __name__ == '__main__':
    main()
