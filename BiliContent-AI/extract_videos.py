# -*- coding: utf-8 -*-
"""
视频列表提取器 — 支持三种来源：
  --source single     从单个视频页面提取
  --source collection 从合集页面提取
  --source space     从UP主空间页面提取

用法:
  python extract_videos.py --source collection --html page.html -o eps.json
  python extract_videos.py --source single --html page.html -o eps.json
  python extract_videos.py --source space --html page.html -o eps.json
"""
import json, re, sys

def parse_html(html):
    """提取 __INITIAL_STATE__ 的通用方法"""
    m = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});\s*\(function', html, re.DOTALL)
    if not m:
        m = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', html, re.DOTALL)
    if not m:
        return None
    return json.loads(m.group(1))

def extract_single(html):
    """从单个视频页面提取"""
    state = parse_html(html)
    if not state:
        raise ValueError('未找到视频信息')
    vd = state.get('videoData') or state.get('videoInfo') or {}
    if not vd.get('aid'):
        raise ValueError('未找到视频数据')
    return [{
        'idx': 1,
        'aid': vd.get('aid'),
        'cid': vd.get('cid'),
        'bvid': vd.get('bvid', ''),
        'title': vd.get('title', ''),
        'duration': vd.get('duration', 0),
    }]

def extract_collection(html):
    """从合集页面提取"""
    state = parse_html(html)
    if not state:
        raise ValueError('未找到合集信息')
    sections = state.get('sectionsInfo', {}).get('sections', [])
    if not sections:
        raise ValueError('未找到合集内容')
    eps = []
    for sec in sections:
        for ep in sec.get('episodes', []):
            eps.append({
                'idx': len(eps) + 1,
                'aid': ep.get('aid'),
                'cid': ep.get('cid'),
                'bvid': ep.get('bvid', ''),
                'title': ep.get('title', ''),
                'duration': ep.get('duration', 0),
            })
    return eps

def extract_space(html):
    """从UP主空间页面提取视频列表"""
    state = parse_html(html)
    if not state:
        raise ValueError('未找到空间信息')
    # 尝试多种可能的字段名
    videos = []
    for key in ['videoList', 'videos', 'list', 'mediaList']:
        vlist = state.get(key, [])
        if vlist:
            videos = vlist
            break
    if not videos:
        # 从 spaceData 里找
        sd = state.get('spaceData', {}) or {}
        for key in ['videoList', 'videos', 'list', 'archive']:
            vlist = sd.get(key, [])
            if vlist:
                videos = vlist
                break
    if not videos:
        raise ValueError('未找到空间视频列表')
    eps = []
    for v in videos:
        aid = v.get('aid') or v.get('id')
        if not aid:
            continue
        eps.append({
            'idx': len(eps) + 1,
            'aid': aid,
            'cid': v.get('cid', 0),
            'bvid': v.get('bvid', ''),
            'title': v.get('title', ''),
            'duration': v.get('duration', v.get('length', 0)),
        })
    return eps

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description='提取B站视频列表')
    p.add_argument('--source', required=True, choices=['single', 'collection', 'space'],
                   help='来源类型: single(单个视频) / collection(合集) / space(UP主空间)')
    p.add_argument('--html', required=True, help='页面HTML文件路径')
    p.add_argument('-o', '--output', default='eps.json', help='输出文件路径')
    args = p.parse_args()

    with open(args.html, encoding='utf-8') as f:
        html = f.read()

    if args.source == 'single':
        eps = extract_single(html)
    elif args.source == 'collection':
        eps = extract_collection(html)
    else:
        eps = extract_space(html)

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(eps, f, ensure_ascii=False, indent=1)
    print(f'[{args.source}] 提取 {len(eps)} 个视频 -> {args.output}')