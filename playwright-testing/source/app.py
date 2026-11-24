"""Playwright 课程本地练习站点。

启动：
    python app.py
访问：
    http://127.0.0.1:5011
"""
from __future__ import annotations

import time
from pathlib import Path

from flask import Flask, jsonify, request

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent

MOVIES = [
    ("星际穿越", 2014, 9.4, "科幻", "诺兰", 169),
    ("肖申克的救赎", 1994, 9.7, "剧情", "弗兰克·德拉邦特", 142),
    ("盗梦空间", 2010, 9.4, "科幻", "诺兰", 148),
    ("霸王别姬", 1993, 9.6, "剧情", "陈凯歌", 171),
    ("阿甘正传", 1994, 9.5, "剧情", "罗伯特·泽米吉斯", 142),
    ("千与千寻", 2001, 9.4, "动画", "宫崎骏", 125),
    ("泰坦尼克号", 1997, 9.5, "爱情", "卡梅隆", 194),
    ("这个杀手不太冷", 1994, 9.4, "剧情", "吕克·贝松", 110),
    ("楚门的世界", 1998, 9.4, "剧情", "彼特·威尔", 103),
    ("疯狂动物城", 2016, 9.2, "动画", "拜伦·霍华德", 109),
    ("教父", 1972, 9.3, "犯罪", "科波拉", 175),
    ("无间道", 2002, 9.3, "犯罪", "刘伟强", 101),
    ("大话西游", 1995, 9.2, "喜剧", "刘镇伟", 95),
    ("龙猫", 1988, 9.2, "动画", "宫崎骏", 86),
    ("天空之城", 1986, 9.2, "动画", "宫崎骏", 125),
    ("让子弹飞", 2010, 9.0, "喜剧", "姜文", 132),
    ("我不是药神", 2018, 9.0, "剧情", "文牧野", 117),
    ("流浪地球", 2019, 7.9, "科幻", "郭帆", 125),
    ("哪吒之魔童降世", 2019, 8.4, "动画", "饺子", 110),
    ("你好，李焕英", 2021, 7.7, "喜剧", "贾玲", 128),
    ("满江红", 2023, 7.0, "悬疑", "张艺谋", 159),
    ("奥本海默", 2023, 8.8, "传记", "诺兰", 180),
    ("沙丘", 2021, 7.7, "科幻", "维伦纽瓦", 155),
    ("蜘蛛侠：平行宇宙", 2018, 8.6, "动画", "鲍勃·佩尔西凯蒂", 117),
    ("寻梦环游记", 2017, 9.1, "动画", "李·昂克里奇", 105),
    ("摔跤吧！爸爸", 2016, 9.0, "传记", "涅提·蒂瓦里", 161),
    ("三傻大闹宝莱坞", 2009, 9.2, "喜剧", "拉库马·希拉尼", 171),
    ("海上钢琴师", 1998, 9.3, "剧情", "朱塞佩·托纳多雷", 165),
    ("忠犬八公的故事", 2009, 9.4, "剧情", "莱塞·霍尔斯道姆", 93),
    ("放牛班的春天", 2004, 9.3, "剧情", "克里斯托夫·巴拉蒂", 97),
]

BASE_CSS = """
:root { --navy:#1F3A5F; --teal:#16A085; --blue:#2E86C1; --bg:#F4F7FB; --muted:#7F8C8D; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:#243447; font-family:"Microsoft YaHei","PingFang SC",Arial,sans-serif; }
a { color:var(--teal); text-decoration:none; }
header { background:var(--navy); color:white; padding:18px 40px; display:flex; align-items:center; gap:24px; }
header .brand { font-size:20px; font-weight:700; }
header nav a { color:#D7E2EE; margin-right:18px; font-size:14px; }
header nav a:hover { color:white; }
.container { max-width:1100px; margin:30px auto; padding:0 24px; }
h1 { color:var(--navy); margin:0 0 8px; }
h2 { color:var(--navy); }
.sub { color:var(--muted); font-size:14px; }
.card { background:white; border:1px solid #E3EAF2; border-radius:14px; padding:22px; margin-bottom:18px; box-shadow:0 3px 12px rgba(31,58,95,.04); }
.row { display:flex; gap:18px; flex-wrap:wrap; }
.row > .card { flex:1; min-width:260px; }
label { display:block; margin:10px 0 5px; font-weight:600; font-size:13px; }
input, select, textarea { width:100%; padding:9px 11px; border:1px solid #D6E0EA; border-radius:8px; font-size:14px; }
button, .btn { background:var(--teal); color:white; border:none; border-radius:8px; padding:9px 16px; cursor:pointer; font-size:14px; }
button:hover, .btn:hover { background:#12876F; }
.btn-ghost { background:white; color:var(--navy); border:1px solid #D6E0EA; }
.grid { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; }
.article-card, .movie-card { background:white; border:1px solid #E3EAF2; border-radius:12px; padding:16px; }
.article-card h3, .movie-card h3 { margin:0 0 8px; color:var(--navy); font-size:16px; }
#search-results { display:none; margin-top:14px; padding:14px; background:#E8F6F2; border-radius:10px; }
#search-results.show { display:block; }
#pwd-hint, #login-result, #form-result, #dialog-output, #status-text { margin-top:12px; color:var(--teal); font-weight:600; }
#loading { display:none; color:var(--blue); }
table { width:100%; border-collapse:collapse; }
th, td { padding:9px; border-bottom:1px solid #EEF3F8; text-align:left; font-size:14px; }
th { background:#F1F6FA; color:var(--navy); }
.badge { display:inline-block; background:#E8F6F2; color:#12876F; border-radius:20px; padding:2px 9px; font-size:12px; }
.movie-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:12px; }
.meta { color:var(--muted); font-size:12px; }
.pagination { display:flex; gap:8px; align-items:center; margin-top:16px; }
.pagination a { padding:7px 12px; background:white; border:1px solid #D6E0EA; border-radius:7px; }
.pagination .active { background:var(--teal); color:white; border-color:var(--teal); }
iframe { width:100%; height:220px; border:1px solid #E3EAF2; border-radius:10px; background:white; }
.small { font-size:12px; color:var(--muted); }
"""


def layout(title: str, body: str, script: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title><style>{BASE_CSS}</style></head>
<body><header><div class="brand">Playwright 练习站</div>
<nav><a href="/">首页</a><a href="/login">登录</a><a href="/form">表单</a><a href="/dialogs">弹窗</a>
<a href="/wait">等待</a><a href="/tabs">标签页</a><a href="/iframe">iframe</a><a href="/movies">电影</a>
<a href="/network">网络</a></nav></header><div class="container">{body}</div>
<script>{script}</script></body></html>"""


@app.route("/health")
def health():
    return jsonify({"ok": True})


@app.route("/")
def home():
    body = """
    <h1>Playwright 自动化练习场</h1>
    <p class="sub">本地页面，无需登录，专门用来练习定位、输入、点击、等待、弹窗和请求拦截。</p>
    <div class="card">
      <h2>文章搜索</h2>
      <label for="search-input">搜索关键词</label>
      <input id="search-input" name="keyword" placeholder="请输入关键词" value="">
      <button id="btn-search" style="margin-top:10px;">搜索</button>
      <div id="search-results"><strong id="result-header"></strong><div id="result-list"></div></div>
    </div>
    <div class="row">
      <div class="card"><h2>热门文章</h2>
        <div class="article-card"><h3 class="card-title" id="title-1">Playwright 自动等待机制</h3>
          <p class="meta" id="caption-1">从元素可见到可点击，Playwright 会替你等待。</p>
          <a class="card-link" href="/wait">查看详情</a></div>
        <div class="article-card"><h3 class="card-title" id="title-2">八种元素定位方式</h3>
          <p class="meta" id="caption-2">CSS、XPath、Role、Label、Placeholder 怎么选。</p>
          <a class="card-link" href="/login">查看详情</a></div>
        <div class="article-card"><h3 class="card-title" id="title-3">弹窗处理实战</h3>
          <p class="meta" id="caption-3">alert、confirm、prompt 的正确处理顺序。</p>
          <a class="card-link" href="/dialogs">查看详情</a></div>
      </div>
      <div class="card"><h2>文章排行榜</h2>
        <table id="rank-table"><thead><tr><th>排名</th><th>标题</th><th>阅读</th></tr></thead>
        <tbody><tr><td>1</td><td>Playwright 自动等待</td><td>12,800</td></tr>
        <tr><td>2</td><td>八种定位方式</td><td>9,600</td></tr>
        <tr><td>3</td><td>表单填写</td><td>8,200</td></tr>
        <tr><td>4</td><td>弹窗处理</td><td>7,500</td></tr>
        <tr><td>5</td><td>多标签页与 iframe</td><td>6,900</td></tr></tbody></table>
      </div>
    </div>
    <div class="card">
      <h2>注册表单</h2>
      <label for="username">用户名</label><input id="username" placeholder="请输入用户名">
      <label for="email">邮箱</label><input id="email" type="email" placeholder="name@example.com">
      <label for="password">密码</label><input id="password" type="password" placeholder="至少 6 位">
      <button id="btn-submit" style="margin-top:12px;">提交</button>
      <div id="pwd-hint"></div>
    </div>
    """
    script = """
    const articles = [
      ["Playwright 自动等待机制", "从元素可见到可点击，Playwright 会替你等待。"],
      ["八种元素定位方式", "CSS、XPath、Role、Label、Placeholder 怎么选。"],
      ["弹窗处理实战", "alert、confirm、prompt 的正确处理顺序。"]
    ];
    document.getElementById('btn-search').addEventListener('click', () => {
      const keyword = document.getElementById('search-input').value.trim();
      const matched = articles.filter(item => item[0].includes(keyword) || item[1].includes(keyword));
      document.getElementById('result-header').textContent =
        `搜索 "${keyword}"，在 3 篇文章中找到 ${matched.length} 条相关结果`;
      document.getElementById('result-list').innerHTML = matched.length
        ? matched.map(item => `<p><strong>${item[0]}</strong>：${item[1]}</p>`).join('')
        : '<p>没有找到相关文章。</p>';
      document.getElementById('search-results').classList.add('show');
    });
    document.getElementById('btn-submit').addEventListener('click', () => {
      const password = document.getElementById('password').value;
      document.getElementById('pwd-hint').textContent =
        password.length >= 6 ? '提交成功，密码长度符合要求。' : '密码至少需要 6 位。';
    });
    """
    return layout("Playwright 练习站", body, script)


@app.route("/login")
def login():
    body = """
    <h1>登录表单</h1><p class="sub">练习 get_by_label、get_by_placeholder、get_by_role 和 data-testid。</p>
    <div class="card" style="max-width:460px;">
      <form id="login-form" onsubmit="return false;">
        <label for="username">用户名</label>
        <input id="username" placeholder="请输入用户名或邮箱" data-testid="username-input">
        <label for="email">邮箱</label>
        <input id="email" type="email" placeholder="name@example.com">
        <label for="password">密码</label>
        <input id="password" type="password" placeholder="请输入密码">
        <label style="display:flex;align-items:center;gap:8px;font-weight:400;">
          <input id="remember" type="checkbox" style="width:auto;">记住我
        </label>
        <a href="/" id="forgot-link">忘记密码</a>
        <button id="login-btn" type="button" style="margin-top:12px;">登 录</button>
        <div id="login-result"></div>
      </form>
    </div>
    """
    script = """
    document.getElementById('login-btn').addEventListener('click', () => {
      const user = document.getElementById('username').value;
      const remember = document.getElementById('remember').checked;
      document.getElementById('login-result').textContent =
        user ? `欢迎 ${user}${remember ? '，已记住登录状态' : ''}` : '请输入用户名';
    });
    """
    return layout("登录表单", body, script)


@app.route("/form")
def form_page():
    body = """
    <h1>活动报名表</h1><p class="sub">文本框、下拉框、单选框、复选框、日期、滑块和多行文本。</p>
    <div class="card" style="max-width:720px;">
      <label for="name">姓名</label><input id="name" placeholder="请输入姓名">
      <label for="phone">手机号</label><input id="phone" placeholder="11 位手机号">
      <label for="city">城市</label>
      <select id="city"><option>北京</option><option>上海</option><option>广州</option><option>深圳</option></select>
      <label>参会方式</label>
      <label style="font-weight:400;"><input type="radio" name="mode" value="线下" checked style="width:auto;"> 线下</label>
      <label style="font-weight:400;"><input type="radio" name="mode" value="线上" style="width:auto;"> 线上</label>
      <label style="font-weight:400;"><input id="agree" type="checkbox" style="width:auto;"> 同意活动须知</label>
      <label for="date">参加日期</label><input id="date" type="date" value="2026-06-18">
      <label for="level">兴趣程度</label><input id="level" type="range" min="0" max="10" value="8">
      <label for="note">备注</label><textarea id="note" rows="3" placeholder="有什么想提前说明的"></textarea>
      <button id="submit-form" style="margin-top:12px;">提交报名</button>
      <div id="form-result"></div>
    </div>
    """
    script = """
    document.getElementById('submit-form').addEventListener('click', () => {
      const mode = document.querySelector('input[name="mode"]:checked').value;
      const name = document.getElementById('name').value;
      const city = document.getElementById('city').value;
      document.getElementById('form-result').textContent =
        `已提交：${name || '未填写姓名'} · ${city} · ${mode} · 兴趣 ${document.getElementById('level').value}`;
    });
    """
    return layout("活动报名表", body, script)


@app.route("/dialogs")
def dialogs():
    body = """
    <h1>原生弹窗</h1><p class="sub">Playwright 需要先注册 dialog 处理器，再触发弹窗。</p>
    <div class="card">
      <button id="btn-alert">alert 提示</button>
      <button id="btn-confirm">confirm 确认</button>
      <button id="btn-prompt">prompt 输入</button>
      <div id="dialog-output">还没有操作弹窗</div>
    </div>
    """
    script = """
    document.getElementById('btn-alert').addEventListener('click', () => {
      alert('这是一条普通提示');
      document.getElementById('dialog-output').textContent = 'alert 已关闭';
    });
    document.getElementById('btn-confirm').addEventListener('click', () => {
      const ok = confirm('确定要提交吗？');
      document.getElementById('dialog-output').textContent = ok ? 'confirm：用户点了确定' : 'confirm：用户点了取消';
    });
    document.getElementById('btn-prompt').addEventListener('click', () => {
      const value = prompt('请输入你的名字', '小李');
      document.getElementById('dialog-output').textContent = value ? `prompt：你好，${value}` : 'prompt：用户取消';
    });
    """
    return layout("原生弹窗", body, script)


@app.route("/wait")
def wait_page():
    body = """
    <h1>智能等待</h1><p class="sub">点击按钮后，内容会在 1.2 秒后出现。不要写 time.sleep，直接等元素可见。</p>
    <div class="card">
      <button id="btn-load">加载慢数据</button>
      <div id="loading">正在加载，请稍候...</div>
      <div id="slow-content" style="display:none;margin-top:14px;padding:16px;background:#E8F6F2;border-radius:10px;">
        <strong id="slow-title">数据加载完成</strong>
        <p id="slow-text">这是延迟返回的业务数据。</p>
      </div>
      <div id="status-text">状态：未开始</div>
    </div>
    """
    script = """
    document.getElementById('btn-load').addEventListener('click', () => {
      document.getElementById('loading').style.display = 'block';
      document.getElementById('status-text').textContent = '状态：加载中';
      setTimeout(() => {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('slow-content').style.display = 'block';
        document.getElementById('slow-title').textContent = '数据加载完成';
        document.getElementById('slow-text').textContent = `共 128 条记录，更新于 ${new Date().toLocaleTimeString()}`;
        document.getElementById('status-text').textContent = '状态：完成';
      }, 1200);
    });
    """
    return layout("智能等待", body, script)


@app.route("/tabs")
def tabs():
    body = """
    <h1>多标签页</h1><p class="sub">点击链接会打开新标签页；Playwright 可以从 context.pages 拿到新页面。</p>
    <div class="card">
      <a id="open-tab" href="/tabs/child" target="_blank">打开新标签页</a>
      <p class="small">也可以用 page.expect_popup() 等待新页面。</p>
    </div>
    """
    return layout("多标签页", body)


@app.route("/tabs/child")
def tab_child():
    return layout(
        "子页面",
        """<h1 id="child-title">这是新标签页</h1>
        <p class="sub">父页面通过 expect_popup 捕获了这个页面。</p>
        <button id="child-btn" onclick="document.getElementById('child-result').textContent='子页面按钮已点击'">点我</button>
        <div id="child-result"></div>""",
    )


@app.route("/iframe")
def iframe_page():
    body = """
    <h1>iframe 操作</h1><p class="sub">先定位 iframe，再用 frame_locator 进入内部页面。</p>
    <div class="card">
      <iframe id="demo-frame" src="/iframe/inner" title="演示 iframe"></iframe>
      <div id="frame-result"></div>
    </div>
    """
    return layout("iframe 操作", body)


@app.route("/iframe/inner")
def iframe_inner():
    return """<!DOCTYPE html><html><head><meta charset="utf-8"><style>
    body{font-family:"Microsoft YaHei";padding:18px;background:#F8FBFD;color:#1F3A5F}
    button{background:#16A085;color:white;border:none;border-radius:8px;padding:8px 14px}
    </style></head><body>
    <h3 id="inner-title">iframe 内部页面</h3>
    <p id="inner-text">这里的元素需要用 frame_locator 定位。</p>
    <button id="inner-btn" onclick="document.getElementById('inner-result').textContent='iframe 内部按钮已点击'">内部按钮</button>
    <div id="inner-result"></div></body></html>"""


@app.route("/movies")
def movies():
    page = max(1, int(request.args.get("page", 1)))
    page_size = 10
    start = (page - 1) * page_size
    page_movies = MOVIES[start : start + page_size]
    cards = "".join(
        f"""<div class="movie-card"><h3 class="movie-title">{title}</h3>
        <p class="meta">年份：<span class="movie-year">{year}</span> · 类型：<span class="movie-genre">{genre}</span></p>
        <p class="meta">导演：<span class="movie-director">{director}</span> · 时长：<span class="movie-duration">{duration}</span> 分钟</p>
        <p><span class="badge movie-rating">{rating}</span></p></div>"""
        for title, year, rating, genre, director, duration in page_movies
    )
    pages = (len(MOVIES) + page_size - 1) // page_size
    pagination = "".join(
        f'<a class="{"active" if number == page else ""}" href="/movies?page={number}">{number}</a>'
        for number in range(1, pages + 1)
    )
    body = f"""<h1>电影榜单</h1><p class="sub">共 {len(MOVIES)} 部电影，每页 10 部，适合练习列表抓取和分页。</p>
    <div id="movie-grid" class="movie-grid">{cards}</div>
    <div class="pagination">{pagination}</div>
    <p class="small" id="page-info">第 {page} / {pages} 页</p>"""
    return layout("电影榜单", body)


@app.route("/network")
def network():
    body = """
    <h1>请求拦截与接口等待</h1><p class="sub">练习 page.expect_response、route.abort 和 route.fulfill。</p>
    <div class="card">
      <button id="btn-products">加载商品</button>
      <button id="btn-slow">加载慢接口</button>
      <button id="btn-fail">触发 500</button>
      <div id="status-text">状态：等待操作</div>
      <div id="product-list"></div>
    </div>
    <script src="/tracking.js"></script>
    """
    script = """
    async function loadProducts() {
      document.getElementById('status-text').textContent = '状态：加载商品';
      const response = await fetch('/api/products');
      const data = await response.json();
      document.getElementById('product-list').innerHTML = data.items.map(
        item => `<p><strong>${item.name}</strong> · ¥${item.price}</p>`
      ).join('');
      document.getElementById('status-text').textContent = '状态：商品加载完成';
    }
    document.getElementById('btn-products').addEventListener('click', loadProducts);
    document.getElementById('btn-slow').addEventListener('click', async () => {
      document.getElementById('status-text').textContent = '状态：等待慢接口';
      const response = await fetch('/api/slow');
      const data = await response.json();
      document.getElementById('status-text').textContent = `状态：${data.message}`;
    });
    document.getElementById('btn-fail').addEventListener('click', async () => {
      const response = await fetch('/api/fail');
      document.getElementById('status-text').textContent = `状态：接口返回 ${response.status}`;
    });
    """
    return layout("请求拦截", body, script)


@app.route("/tracking.js")
def tracking():
    return "fetch('/api/analytics').catch(() => {});", 200, {"Content-Type": "application/javascript"}


@app.route("/api/analytics")
def analytics():
    return jsonify({"ok": True})


@app.route("/api/products")
def products():
    return jsonify(
        {
            "items": [
                {"id": 1, "name": "机械键盘", "price": 399},
                {"id": 2, "name": "人体工学椅", "price": 1299},
                {"id": 3, "name": "降噪耳机", "price": 899},
            ]
        }
    )


@app.route("/api/slow")
def slow():
    time.sleep(2)
    return jsonify({"message": "慢接口返回成功"})


@app.route("/api/fail")
def fail():
    return jsonify({"error": "internal error"}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5011, debug=False, use_reloader=False)
