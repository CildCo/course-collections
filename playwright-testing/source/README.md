# Python 自动化测试：Playwright 从入门到精通

这是《Python自动化测试：Playwright从入门到精通》的配套源码。  
9 节课从第一个浏览器脚本开始，依次完成定位、八种选择器、表单填写、弹窗处理、智能等待、多标签页/iframe、电影数据抓取和请求拦截。

课程自带一个本地练习站点，不依赖外网，断网也能跑。

## 安装

```bash
cd 码袋子/content/collections/playwright-testing/source
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

如果下载慢，可以加清华源安装 Python 包：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 启动练习站

```bash
python app.py
```

浏览器打开 <http://127.0.0.1:5011>。`run_all.py` 会自动启动和关闭站点，不需要单独开。

## 一键运行

```bash
python run_all.py
```

9 节课依次运行，截图保存到 `output/`，电影 CSV 保存到 `data/`。

## 逐课运行

```bash
python lesson01_first_script/main.py
python lesson02_locators/main.py
python lesson03_eight_locators/main.py
python lesson04_form_fill/main.py
python lesson05_dialogs/main.py
python lesson06_waiting/main.py
python lesson07_tabs_iframe/main.py
python lesson08_movie_scrape/main.py
python lesson09_network/main.py
```

## 课次与输出

| 课次 | 目录 | 主要内容 | 输出 |
|---|---|---|---|
| 第1课 | `lesson01_first_script/` | 启动 Chromium、访问页面、标题和截图 | `01_第一个脚本.png` |
| 第2课 | `lesson02_locators/` | locator、fill、click、inner_text、count、nth | `02_元素定位.png` |
| 第3课 | `lesson03_eight_locators/` | label、placeholder、role、text、testid、CSS、XPath、链式 | `03_八种定位.png` |
| 第4课 | `lesson04_form_fill/` | 文本框、下拉、单选、复选、日期、滑块、textarea | `04_表单填写.png` |
| 第5课 | `lesson05_dialogs/` | alert、confirm、prompt 的 accept/dismiss | `05_弹窗处理.png` |
| 第6课 | `lesson06_waiting/` | 元素可见等待、expect 断言、不用 time.sleep | `06_智能等待.png` |
| 第7课 | `lesson07_tabs_iframe/` | expect_page、frame_locator、iframe 内元素 | `07_iframe.png`、`07_新标签页.png` |
| 第8课 | `lesson08_movie_scrape/` | 分页抓取 30 部电影、导出 CSV | `08_电影数据.png`、`data/movies.csv` |
| 第9课 | `lesson09_network/` | route.abort、route.fulfill、请求统计 | `09_请求拦截.png`、`请求拦截报告.txt` |

## 目录说明

```text
playwright-testing/
├── collection.json
└── source/
    ├── app.py                    本地练习站（Flask）
    ├── common.py                 启动站点、浏览器、截图
    ├── run_all.py                一键运行
    ├── requirements.txt
    └── lesson01_first_script/    每课一个目录
        └── main.py
```

## 本地练习站页面

- `/`：搜索、文章卡片、排行榜、注册表单
- `/login`：八种定位方式练习
- `/form`：完整活动报名表单
- `/dialogs`：alert / confirm / prompt
- `/wait`：延迟 1.2 秒出现的慢内容
- `/tabs`：打开新标签页
- `/iframe`：iframe 内部页面
- `/movies`：30 部电影，每页 10 部
- `/network`：商品接口、慢接口、500 接口和埋点请求

## 三个容易踩的坑

1. **弹窗要先注册处理器**：`page.once("dialog", ...)` 要在点击之前写，否则 Playwright 会自动关闭弹窗。
2. **不要用 time.sleep**：等待元素可见用 `locator.wait_for(state="visible")` 或 `expect(...)`。
3. **请求拦截不要拦业务接口**：只拦埋点、广告和无关静态资源，否则 CI 里页面数据会缺。

## 关于 headless

默认以 headless 模式运行，适合服务器和 CI。想看着浏览器执行，设置：

```bash
set PLAYWRIGHT_HEADLESS=0
python lesson01_first_script/main.py
```
