#!/usr/bin/env python3
"""
Full Metadata Fetcher — Pulls all video metadata from a Douyin/TikTok creator account.
Covers both independent posts and collection/series content.
Output: all_videos.json (deduplicated complete list)

Usage:
  python3 fetch_all_metadata.py --sec_user_id "MS4wLjAB..." --output "metadata/all_videos.json"

Optional:
  --mix_ids "id1,id2"  Manually specify collection IDs (auto-detected if omitted)
  --tikhub_key "..."   TikHub API Key (defaults to env var TIKHUB_API_KEY)
  --proxy "http://your-proxy:port"  Proxy address (optional)
"""

import argparse
import json
import os
import sys
import time
import random
import urllib.request
import urllib.error
from datetime import datetime

TIKHUB_BASE = "https://api.tikhub.dev"
QPS_LIMIT = 10  # TikHub QPS limit


def make_request(url, headers=None, proxy=None, timeout=30):
    """Send HTTP request with optional proxy"""
    req = urllib.request.Request(url, headers=headers or {})
    
    handler_chain = [urllib.request.HTTPSHandler()]
    if proxy:
        handler_chain.append(urllib.request.ProxyHandler({
            'http': proxy,
            'https': proxy
        }))
    
    opener = urllib.request.build_opener(*handler_chain)
    
    for attempt in range(3):
        try:
            with opener.open(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except Exception as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
            else:
                raise


def extract_video_metadata(item):
    """Extract metadata from a single video item in TikHub response"""
    stats = item.get('statistics', {})
    author = item.get('author', {})
    
    # Extract collection info (may be in multiple locations)
    series_info = item.get('series_basic_info', {})
    mix_info = item.get('mix_info', {})
    
    mix_id = None
    if series_info and series_info.get('series_id'):
        mix_id = series_info['series_id']
    elif mix_info and mix_info.get('mix_id'):
        mix_id = mix_info['mix_id']
    
    # Episode number within a series
    series_play = item.get('series_play_info', {})
    episode = None
    if series_play and 'series_aweme_index' in series_play:
        episode = series_play['series_aweme_index']
    
    return {
        'aweme_id': item.get('aweme_id', ''),
        'desc': item.get('desc', ''),
        'digg_count': stats.get('digg_count', 0),
        'comment_count': stats.get('comment_count', 0),
        'share_count': stats.get('share_count', 0),
        'play_count': stats.get('play_count', 0),
        'create_time': item.get('create_time', 0),
        'duration': item.get('video', {}).get('duration', 0),
        'mix_id': mix_id,
        'episode': episode,
        'share_url': item.get('share_info', {}).get('share_url', ''),
        'source': 'independent',
    }


def fetch_independent_videos(sec_user_id, api_key, proxy=None):
    """Fetch all independent posts, paginate to end"""
    all_videos = []
    max_cursor = 0
    page = 0
    
    while True:
        page += 1
        url = (
            f"{TIKHUB_BASE}/api/v1/douyin/app/v3/fetch_user_post_videos"
            f"?sec_user_id={sec_user_id}"
            f"&count=20"
            f"&max_cursor={max_cursor}"
        )
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'User-Agent': 'curl/7.88.1'
        }
        
        print(f"  [Independent] Page {page}: cursor={max_cursor}")
        
        try:
            resp = make_request(url, headers=headers, proxy=proxy, timeout=60)
        except Exception as e:
            print(f"  ❌ Request failed: {e}")
            break
        
        code = resp.get('code', 0)
        if code != 200:
            print(f"  ❌ API error: code={code}, msg={resp.get('message', '')}")
            break
        
        data = resp.get('data', {})
        aweme_list = data.get('aweme_list', [])
        
        if not aweme_list:
            print(f"  ✓ Empty list, pagination complete")
            break
        
        for item in aweme_list:
            meta = extract_video_metadata(item)
            all_videos.append(meta)
        
        has_more = data.get('has_more', False)
        new_cursor = data.get('max_cursor', 0)
        
        print(f"    Got {len(aweme_list)}, total {len(all_videos)}, has_more={has_more}")
        
        if not has_more or new_cursor == max_cursor:
            break
        
        max_cursor = new_cursor
        time.sleep(random.uniform(0.2, 0.5))  # QPS control
    
    return all_videos


def fetch_mix_videos(mix_id, api_key, proxy=None):
    """Fetch all videos in a collection/series, paginate to end"""
    all_videos = []
    cursor = 0
    page = 0
    
    while True:
        page += 1
        url = (
            f"{TIKHUB_BASE}/api/v1/douyin/app/v3/fetch_video_mix_post_list"
            f"?mix_id={mix_id}"
            f"&count=20"
            f"&cursor={cursor}"
        )
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'User-Agent': 'curl/7.88.1'
        }
        
        print(f"  [Collection {mix_id}] Page {page}: cursor={cursor}")
        
        try:
            resp = make_request(url, headers=headers, proxy=proxy, timeout=60)
        except Exception as e:
            print(f"  ❌ Request failed: {e}")
            break
        
        code = resp.get('code', 0)
        if code != 200:
            print(f"  ❌ API error: code={code}, msg={resp.get('message', '')}")
            break
        
        data = resp.get('data', {})
        aweme_list = data.get('aweme_list', [])
        
        if not aweme_list:
            print(f"  ✓ Empty list, pagination complete")
            break
        
        for item in aweme_list:
            meta = extract_video_metadata(item)
            meta['source'] = f"mix:{mix_id}"
            all_videos.append(meta)
        
        has_more = data.get('has_more', False)
        new_cursor = data.get('cursor', 0)
        
        print(f"    Got {len(aweme_list)}, total {len(all_videos)}, has_more={has_more}")
        
        if not has_more or new_cursor == cursor:
            break
        
        cursor = new_cursor
        time.sleep(random.uniform(0.2, 0.5))
    
    return all_videos


def deduplicate(videos):
    """Deduplicate by aweme_id"""
    seen = set()
    result = []
    for v in videos:
        aid = v['aweme_id']
        if aid not in seen:
            seen.add(aid)
            result.append(v)
        else:
            # Merge source info
            for existing in result:
                if existing['aweme_id'] == aid:
                    if existing['source'] == 'independent' and v['source'].startswith('mix:'):
                        existing['source'] = f"independent+{v['source']}"
                    break
    return result


def main():
    parser = argparse.ArgumentParser(description='Fetch all video metadata from a creator account')
    parser.add_argument('--sec_user_id', required=True, help='Target account sec_user_id')
    parser.add_argument('--output', required=True, help='Output file path')
    parser.add_argument('--mix_ids', default='', help='Manually specify collection IDs, comma-separated')
    parser.add_argument('--tikhub_key', default='', help='TikHub API Key')
    parser.add_argument('--proxy', default='', help='Proxy address (e.g., http://your-proxy:port)')
    args = parser.parse_args()
    
    api_key = args.tikhub_key or os.environ.get('TIKHUB_API_KEY', '')
    if not api_key:
        print("❌ TikHub API Key required (--tikhub_key or env var TIKHUB_API_KEY)")
        sys.exit(1)
    
    proxy = args.proxy or None
    
    print("=" * 60)
    print("Phase 0: Full Metadata Fetch")
    print("=" * 60)
    
    # Step 1: Fetch independent posts
    print("\n📹 Step 1: Fetching independent posts...")
    independent = fetch_independent_videos(args.sec_user_id, api_key, proxy)
    print(f"\n  Independent posts: {len(independent)}")
    
    # Step 2: Discover collections
    all_mix_ids = set()
    for v in independent:
        if v.get('mix_id'):
            all_mix_ids.add(v['mix_id'])
    
    if args.mix_ids:
        for mid in args.mix_ids.split(','):
            mid = mid.strip()
            if mid:
                all_mix_ids.add(mid)
    
    print(f"\n📋 Step 2: Found {len(all_mix_ids)} collections: {all_mix_ids or 'none'}")
    
    # Step 3: Fetch collection posts
    mix_videos = []
    for mix_id in all_mix_ids:
        print(f"\n🎬 Step 3: Fetching collection {mix_id}...")
        vids = fetch_mix_videos(mix_id, api_key, proxy)
        mix_videos.extend(vids)
        print(f"  Collection {mix_id}: {len(vids)} videos")
    
    # Step 4: Merge & deduplicate
    print(f"\n🔄 Step 4: Merging & deduplicating...")
    combined = independent + mix_videos
    deduped = deduplicate(combined)
    deduped.sort(key=lambda x: x['create_time'], reverse=True)
    
    # Save
    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(deduped, f, ensure_ascii=False, indent=2)
    
    # Stats
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)
    print(f"Independent: {len(independent)}")
    print(f"Collections: {len(mix_videos)}")
    print(f"After dedup: {len(deduped)}")
    
    if deduped:
        digs = [v['digg_count'] for v in deduped]
        times = [v['create_time'] for v in deduped if v['create_time'] > 0]
        
        print(f"\nLikes range: {min(digs):,} ~ {max(digs):,}")
        if times:
            t_min = datetime.fromtimestamp(min(times)).strftime('%Y-%m-%d')
            t_max = datetime.fromtimestamp(max(times)).strftime('%Y-%m-%d')
            print(f"Time span: {t_min} ~ {t_max}")
        
        top10 = sorted(deduped, key=lambda x: x['digg_count'], reverse=True)[:10]
        print(f"\n=== TOP 10 by Likes ===")
        for i, v in enumerate(top10):
            dt = datetime.fromtimestamp(v['create_time']).strftime('%Y-%m-%d') if v['create_time'] else 'unknown'
            print(f"  {i+1:2d}. ❤️ {v['digg_count']:>10,} | 💬 {v['comment_count']:>8,} | {dt} | {v['desc'][:50]}")
    
    print(f"\n✅ Saved to: {args.output}")


if __name__ == '__main__':
    main()
