# -*- coding: utf-8 -*-
"""
生成HTML格式的字幕提取报告（含AI处理状态）
用法: python generate_report.py eps.json ./字幕 [-o report.html]
"""
import json, os, sys, time, re as _re

def parse_duration(sec):
    h, r = divmod(sec, 3600)
    m, s = divmod(r, 60)
    if h: return f'{h}时{m}分{s}秒'
    if m: return f'{m}分{s}秒'
    return f'{s}秒'

def safe(name):
    return _re.sub(r'[\\/:*?"<>|]', '_', name).strip()

def main():
    if len(sys.argv) < 3:
        print('用法: python generate_report.py eps.json ./字幕 [-o report.html]')
        sys.exit(1)
    eps = json.load(open(sys.argv[1], encoding='utf-8'))
    sub_dir = sys.argv[2]
    out = '提取报告.html'
    if '-o' in sys.argv:
        i = sys.argv.index('-o')
        if i + 1 < len(sys.argv): out = sys.argv[i+1]
    # 检查AI输出目录
    ai_sub_dir = os.path.join(os.path.dirname(sub_dir), 'AI排版字幕') if os.path.basename(sub_dir) in ('SRT','TXT','VTT','ASS','JSON') else os.path.join(sub_dir, '..', 'AI排版字幕')
    ai_sub_dir = os.path.abspath(ai_sub_dir)
    ai_art_dir = os.path.abspath(os.path.join(os.path.dirname(sub_dir), 'AI精炼文章') if os.path.basename(sub_dir) in ('SRT','TXT','VTT','ASS','JSON') else os.path.join(sub_dir, '..', 'AI精炼文章'))
    has_ai_sub = os.path.exists(ai_sub_dir) and len(os.listdir(ai_sub_dir)) > 0
    has_ai_art = os.path.exists(ai_art_dir) and len(os.listdir(ai_art_dir)) > 0

    ok, no_sub, fail = 0, 0, 0
    rows = []
    for ep in eps:
        name = safe(f"{ep['idx']:02d}_{ep['title']}")
        srt = os.path.join(sub_dir, name + '.srt')
        if not os.path.exists(srt):
            # 尝试分文件夹
            srt = os.path.join(sub_dir, 'SRT', name + '.srt')
        if os.path.exists(srt):
            with open(srt, encoding='utf-8') as f:
                count = f.read().count('\n\n') // 2
            ok += 1
            ai_tag = ''
            if has_ai_sub:
                ai_sub_file = os.path.join(ai_sub_dir, name + '.txt')
                if os.path.exists(ai_sub_file):
                    ai_tag = ' ✓AI'
            rows.append(f'<tr><td>{ep["idx"]}</td><td>{ep["title"]}</td><td><span class="b o">OK{ai_tag}</span></td><td>{count}</td></tr>')
        else:
            no_sub += 1
            rows.append(f'<tr><td>{ep["idx"]}</td><td>{ep["title"]}</td><td><span class="b x">无字幕</span></td><td>-</td></tr>')

    total_dur = sum(ep.get('duration', 0) for ep in eps)
    now = time.strftime('%Y-%m-%d %H:%M:%S')

    # AI处理状态
    ai_status = ''
    if has_ai_sub or has_ai_art:
        ai_status = f'''
<div class="s"><h2>AI知识精炼</h2>
<table>
<tr><td>AI排版字幕</td><td>{'✓ 已完成' if has_ai_sub else '— 未处理'}</td></tr>
<tr><td>AI精炼文章</td><td>{'✓ 已完成' if has_ai_art else '— 未处理'}</td></tr>
</table></div>'''

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BiliContent AI - 提取报告</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,'Microsoft YaHei',sans-serif;background:#f5f7fa;color:#333}}
.hd{{background:linear-gradient(135deg,#00a1d6,#2196F3);color:#fff;padding:40px;text-align:center}}
.hd h1{{font-size:28px;margin-bottom:8px}}
.hd p{{opacity:.8;font-size:14px}}
.hd .tag{{display:inline-block;background:rgba(255,255,255,.2);padding:2px 12px;border-radius:20px;font-size:12px;margin-top:8px}}
.c{{max-width:960px;margin:0 auto;padding:20px}}
.sg{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:16px;margin-bottom:30px}}
.sc{{background:#fff;border-radius:12px;padding:20px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,.06)}}
.sc .n{{font-size:32px;font-weight:700;color:#00a1d6}}
.sc .l{{font-size:13px;color:#888;margin-top:4px}}
.sc.g .n{{color:#4caf50}}
.sc.r .n{{color:#f44336}}
.sc.p .n{{color:#9c27b0}}
.s{{background:#fff;border-radius:12px;padding:24px;margin-bottom:20px;box-shadow:0 2px 8px rgba(0,0,0,.06)}}
.s h2{{font-size:18px;margin-bottom:16px;color:#00a1d6;border-bottom:2px solid #e8f4fd;padding-bottom:10px}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
th,td{{padding:10px 12px;text-align:left;border-bottom:1px solid #f0f0f0}}
th{{background:#fafafa;font-weight:600;color:#666}}
tr:hover{{background:#f8faff}}
.b{{display:inline-block;padding:2px 10px;border-radius:20px;font-size:12px;font-weight:500}}
.o{{background:#e8f5e9;color:#2e7d32}}
.x{{background:#e0e0e0;color:#616161}}
.ft{{text-align:center;padding:20px;color:#999;font-size:12px}}
</style></head>
<body>
<div class="hd">
<h1>BiliContent AI</h1>
<p>B站内容智能提取与知识精炼报告</p>
<span class="tag">生成: {now}</span>
</div>
<div class="c">
<div class="sg">
<div class="sc"><div class="n">{len(eps)}</div><div class="l">视频总数</div></div>
<div class="sc g"><div class="n">{ok}</div><div class="l">字幕提取</div></div>
<div class="sc p"><div class="n">{'✓' if has_ai_sub or has_ai_art else '—'}</div><div class="l">AI精炼</div></div>
<div class="sc r"><div class="n">{no_sub}</div><div class="l">无字幕</div></div>
</div>
<div class="s"><h2>统计信息</h2>
<table>
<tr><td>视频总时长</td><td>{parse_duration(total_dur)}</td></tr>
<tr><td>输出格式</td><td>SRT / TXT / VTT / ASS / JSON</td></tr>
</table></div>
{ai_status}
<div class="s"><h2>字幕详情</h2>
<table><tr><th>序号</th><th>标题</th><th>状态</th><th>条数</th></tr>
{''.join(rows)}
</table></div>
</div>
<div class="ft">BiliContent AI · 视频内容到知识资产</div>
</body></html>'''
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'报告已生成: {out}')

if __name__ == '__main__':
    main()