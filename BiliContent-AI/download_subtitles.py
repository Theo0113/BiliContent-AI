# -*- coding: utf-8 -*-
"""
B站字幕下载器 — 从 sub_urls.txt 下载字幕并转换为多种格式

用法: python download_subtitles.py eps.json sub_urls.txt [-o ./字幕] [--config bili_config.json]
"""
import json, re, os, sys, time, requests

def fmt_ts(sec):
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'

def fmt_ts_vtt(sec):
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f'{h:02d}:{m:02d}:{s:02d}.{ms:03d}'

def safe(name):
    return re.sub(r'[\\/:*?"<>|]', '_', name).strip()

def quality_check(body):
    """质量检测与修复"""
    if not body:
        return body
    for i in range(len(body) - 1):
        t = float(body[i].get('to', 0))
        ns = float(body[i + 1].get('from', 0))
        if t > ns:
            body[i]['to'] = ns - 0.01
    merged = []
    for it in body:
        if merged and merged[-1].get('content','').strip() == it.get('content','').strip():
            gap = float(it.get('from',0)) - float(merged[-1].get('to',0))
            if gap <= 0.5:
                merged[-1]['to'] = it['to']
                continue
        merged.append(it)
    while merged and not merged[-1].get('content','').strip():
        merged.pop()
    return merged

def download_one(api_url, bvid, idx, title, out_dir, sub_dir, timeout=30):
    full_url = 'https:' + api_url if api_url.startswith('//') else api_url
    name = safe(f"{idx:02d}_{title}")
    srt_path = os.path.join(sub_dir, name + '.srt')
    if os.path.exists(srt_path):
        return f'{idx:02d} SKIP(已存在) {title}'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': f'https://www.bilibili.com/video/{bvid}',
        'Origin': 'https://www.bilibili.com',
    }
    r = requests.get(full_url, headers=headers, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    body = quality_check(data.get('body') or [])
    if not body:
        return f'{idx:02d} EMPTY(空) {title}'

    # 生成多格式
    srt_lines, txt_lines, vtt_lines, ass_lines = [], [], [], []
    ass_lines.append('[Script Info]\nTitle: %s\nScriptType: v4.00+\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Microsoft YaHei,28,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text' % name)
    vtt_lines.append('WEBVTT\n')
    json_subtitles = []

    for i, it in enumerate(body, 1):
        s = float(it.get('from', 0)); t = float(it.get('to', 0))
        content = it.get('content', '')
        srt_lines.append(f'{i}\n{fmt_ts(s)} --> {fmt_ts(t)}\n{content}\n')
        txt_lines.append(f'[{fmt_ts(s)[:8]}] {content}')
        vtt_lines.append(f'{fmt_ts_vtt(s)} --> {fmt_ts_vtt(t)}\n{content}\n')
        sa = f'0:{int(s//60):02d}:{s%60:05.2f}'; ta = f'0:{int(t//60):02d}:{t%60:05.2f}'
        ass_lines.append(f'Dialogue: 0,{sa},{ta},Default,,0,0,0,,{content}')
        json_subtitles.append({'index':i,'from':round(s,3),'to':round(t,3),'content':content,'duration':round(t-s,3)})

    with open(os.path.join(sub_dir, name + '.srt'), 'w', encoding='utf-8') as f: f.write('\n'.join(srt_lines))
    with open(os.path.join(sub_dir, name + '.txt'), 'w', encoding='utf-8') as f: f.write('\n'.join(txt_lines))
    with open(os.path.join(sub_dir, name + '.vtt'), 'w', encoding='utf-8') as f: f.write('\n'.join(vtt_lines))
    with open(os.path.join(sub_dir, name + '.ass'), 'w', encoding='utf-8') as f: f.write('\n'.join(ass_lines))
    with open(os.path.join(sub_dir, name + '.json'), 'w', encoding='utf-8') as f:
        json.dump({'info':{'aid':data.get('aid',''),'bvid':bvid,'title':title},'subtitles':json_subtitles,'count':len(body)}, f, ensure_ascii=False, indent=2)

    # 副本：纯文本到根目录，方便AI处理
    txt_copy = os.path.join(out_dir, name + '.txt')
    if not os.path.exists(txt_copy):
        with open(txt_copy, 'w', encoding='utf-8') as f:
            f.write('\n'.join(txt_lines))

    return f'{idx:02d} OK ({len(body)}条) {title}'

def main():
    if len(sys.argv) < 3:
        print('用法: python download_subtitles.py eps.json sub_urls.txt [-o ./字幕] [--config bili_config.json]')
        sys.exit(1)
    eps_file, urls_file = sys.argv[1], sys.argv[2]
    out_dir = './字幕'
    if '-o' in sys.argv:
        i = sys.argv.index('-o')
        if i + 1 < len(sys.argv): out_dir = sys.argv[i+1]

    # 读取配置
    config = {'separate_folders': True}
    if '--config' in sys.argv:
        i = sys.argv.index('--config')
        if i + 1 < len(sys.argv) and os.path.exists(sys.argv[i+1]):
            config.update(json.load(open(sys.argv[i+1], encoding='utf-8')))

    os.makedirs(out_dir, exist_ok=True)
    sub_dir = out_dir  # 如果分文件夹就用子目录

    episodes = json.load(open(eps_file, encoding='utf-8'))
    url_map = {}
    for line in open(urls_file, encoding='utf-8'):
        parts = line.strip().split(' ')
        if len(parts) >= 2: url_map[int(parts[0])] = parts[1]

    report = []
    for ep in episodes:
        aid = ep['aid']; url = url_map.get(aid, '')
        if not url or url == 'NOSUBS':
            report.append(f"{ep['idx']:02d} SKIP(无字幕) {ep['title']}")
            continue
        if url.startswith('FAIL'):
            report.append(f"{ep['idx']:02d} SKIP(失败) {ep['title']}")
            continue
        try:
            result = download_one(url, ep.get('bvid',''), ep['idx'], ep['title'], out_dir, sub_dir)
            report.append(result)
        except Exception as e:
            report.append(f"{ep['idx']:02d} ERROR {type(e).__name__} {ep['title']}")
        time.sleep(0.5)

    print('\n'.join(report))
    ok = sum(1 for r in report if ' OK ' in r)
    print(f'\n总计: {ok}/{len(episodes)} 成功')

if __name__ == '__main__':
    main()