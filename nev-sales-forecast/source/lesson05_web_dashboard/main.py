"""第 5 课：离线预测 + Flask/ECharts 可视化大屏。"""
import json
import sys

import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common import OUTPUT_DIR, PROCESSED_DIR, brand_rank, ensure_data, load_json, model_rank, setup_plot, yearly_sales

TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>新能源汽车销售预测驾驶舱</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
<style>
  :root { --bg:#061826; --panel:#0B2438; --line:#173B57; --teal:#1ABC9C; --blue:#3498DB; --gold:#D4AC0D; --text:#E8F1F8; --muted:#8BA6BC; }
  * { box-sizing:border-box; }
  body { margin:0; background:radial-gradient(circle at 20% 0%,#0D3550 0%,var(--bg) 45%); color:var(--text); font-family:"Microsoft YaHei","PingFang SC",sans-serif; }
  header { padding:24px 32px 10px; display:flex; justify-content:space-between; align-items:flex-end; border-bottom:1px solid var(--line); }
  h1 { margin:0; font-size:24px; letter-spacing:2px; }
  .sub { color:var(--muted); font-size:12px; margin-top:6px; }
  .badge { color:var(--teal); border:1px solid var(--teal); padding:6px 12px; border-radius:20px; font-size:12px; }
  .kpis { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; padding:20px 32px; }
  .kpi { background:linear-gradient(145deg,#0B2438,#0A1E30); border:1px solid var(--line); border-radius:14px; padding:18px 20px; }
  .kpi span { color:var(--muted); font-size:12px; }
  .kpi b { display:block; font-size:28px; margin-top:8px; color:var(--teal); }
  .grid { display:grid; grid-template-columns:1fr 1fr; gap:16px; padding:0 32px 26px; }
  .panel { background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:10px; min-height:330px; }
  .panel.wide { grid-column:1 / -1; min-height:380px; }
  .chart { width:100%; height:310px; }
  .panel.wide .chart { height:360px; }
  footer { color:var(--muted); font-size:12px; padding:0 32px 28px; }
  @media (max-width:900px) { .kpis,.grid { grid-template-columns:1fr 1fr; } .panel.wide { grid-column:1 / -1; } }
  @media (max-width:600px) { .kpis,.grid { grid-template-columns:1fr; } header { flex-direction:column; gap:12px; align-items:flex-start; } }
</style>
</head>
<body>
<header>
  <div>
    <h1>新能源汽车销售预测驾驶舱</h1>
    <div class="sub">数据区间 __RANGE__ · 离线预测 · Top 5 品牌</div>
  </div>
  <div class="badge">模型：季节趋势 + 梯度提升融合</div>
</header>
<div class="kpis">
  <div class="kpi"><span>2025 年销量</span><b>__KPI_2025__</b></div>
  <div class="kpi"><span>2026 年预测（Top 5）</span><b>__KPI_FORECAST__</b></div>
  <div class="kpi"><span>累计第一品牌</span><b>__KPI_BRAND__</b></div>
  <div class="kpi"><span>覆盖品牌 / 车型</span><b>__KPI_COVER__</b></div>
</div>
<div class="grid">
  <div class="panel"><div id="yearly" class="chart"></div></div>
  <div class="panel"><div id="brands" class="chart"></div></div>
  <div class="panel"><div id="models" class="chart"></div></div>
  <div class="panel"><div id="share" class="chart"></div></div>
  <div class="panel wide"><div id="forecast" class="chart"></div></div>
</div>
<footer>数据为课程示例数据，不构成投资或经营建议。ECharts 从 CDN 加载，首次打开需要联网。</footer>
<script>
const DATA = __DATA__;
const dark = { textStyle:{ color:'#C9DCEA' }, axisLine:{ lineStyle:{ color:'#2A4F6B' } }, splitLine:{ lineStyle:{ color:'#12344E' } } };
function chart(id) { return echarts.init(document.getElementById(id), null, { renderer:'canvas' }); }
const yearly = chart('yearly');
yearly.setOption({
  backgroundColor:'transparent', title:{ text:'年度销量趋势', left:8, textStyle:{ color:'#E8F1F8', fontSize:14 } },
  grid:{ left:52, right:24, top:52, bottom:32 }, tooltip:{ trigger:'axis' },
  xAxis:{ type:'category', data:DATA.years, axisLabel:{ color:'#8BA6BC' }, axisLine:dark.axisLine },
  yAxis:{ type:'value', ...dark, axisLabel:{ color:'#8BA6BC', formatter:v=>v/10000+'万' } },
  series:[{ type:'line', smooth:true, data:DATA.sales, symbolSize:7, lineStyle:{ width:3, color:'#1ABC9C' }, itemStyle:{ color:'#1ABC9C' }, areaStyle:{ color:'rgba(26,188,156,.18)' } }]
});
const brands = chart('brands');
brands.setOption({
  backgroundColor:'transparent', title:{ text:'品牌累计销量 Top 6', left:8, textStyle:{ color:'#E8F1F8', fontSize:14 } },
  grid:{ left:100, right:32, top:52, bottom:24 }, tooltip:{ trigger:'axis' },
  xAxis:{ type:'value', ...dark, axisLabel:{ color:'#8BA6BC', formatter:v=>v/10000+'万' } },
  yAxis:{ type:'category', inverse:true, data:DATA.brandNames, axisLabel:{ color:'#C9DCEA' }, axisLine:dark.axisLine },
  series:[{ type:'bar', data:DATA.brandSales, barWidth:14, itemStyle:{ borderRadius:[0,7,7,0], color:new echarts.graphic.LinearGradient(0,0,1,0,[{offset:0,color:'#0E6655'},{offset:1,color:'#1ABC9C'}]) } }]
});
const models = chart('models');
models.setOption({
  backgroundColor:'transparent', title:{ text:'历史爆款车型 Top 10', left:8, textStyle:{ color:'#E8F1F8', fontSize:14 } },
  grid:{ left:130, right:32, top:52, bottom:24 }, tooltip:{ trigger:'axis' },
  xAxis:{ type:'value', ...dark, axisLabel:{ color:'#8BA6BC', formatter:v=>v/10000+'万' } },
  yAxis:{ type:'category', inverse:true, data:DATA.modelNames, axisLabel:{ color:'#C9DCEA', fontSize:10 }, axisLine:dark.axisLine },
  series:[{ type:'bar', data:DATA.modelSales, barWidth:12, itemStyle:{ borderRadius:[0,6,6,0], color:new echarts.graphic.LinearGradient(0,0,1,0,[{offset:0,color:'#1F618D'},{offset:1,color:'#3498DB'}]) } }]
});
const share = chart('share');
share.setOption({
  backgroundColor:'transparent', title:{ text:'2026 年品牌份额预测', left:8, textStyle:{ color:'#E8F1F8', fontSize:14 } },
  tooltip:{ trigger:'item', valueFormatter:v=>v+'%' }, legend:{ bottom:0, textStyle:{ color:'#8BA6BC' } },
  series:[{ type:'pie', radius:['42%','66%'], center:['50%','48%'], label:{ color:'#C9DCEA', formatter:'{b}\n{d}%' },
    data:DATA.share.map((v,i)=>({ name:DATA.brandNames[i], value:v, itemStyle:{ color:DATA.colors[i] } })) }]
});
const forecast = chart('forecast');
forecast.setOption({
  backgroundColor:'transparent', title:{ text:'2026 年 5-12 月销量预测', left:8, textStyle:{ color:'#E8F1F8', fontSize:14 } },
  grid:{ left:56, right:28, top:58, bottom:48 }, tooltip:{ trigger:'axis' }, legend:{ bottom:0, textStyle:{ color:'#8BA6BC' } },
  xAxis:{ type:'category', data:DATA.forecastDates, axisLabel:{ color:'#8BA6BC' }, axisLine:dark.axisLine },
  yAxis:{ type:'value', ...dark, axisLabel:{ color:'#8BA6BC', formatter:v=>v/10000+'万' } },
  series:DATA.forecastSeries
});
window.addEventListener('resize', () => [yearly,brands,models,share,forecast].forEach(c=>c.resize()));
</script>
</body>
</html>
"""


def main() -> None:
    setup_plot()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    dashboard_dir = Path(__file__).resolve().parent.parent / "dashboard"
    dashboard_dir.mkdir(parents=True, exist_ok=True)

    data = ensure_data()
    yearly = yearly_sales(data)
    brands = brand_rank(data, 6)
    models = model_rank(data, 10)
    forecast = pd.read_csv(PROCESSED_DIR / "forecast_2026.csv", parse_dates=["统计月份"])
    metrics = load_json(PROCESSED_DIR / "forecast_metrics.json")

    last_year = int(yearly["年份"].max())
    last_year_sales = int(yearly.loc[yearly["年份"] == last_year, "销量"].iloc[0])
    forecast_total = int(metrics["forecast_2026_total"])
    top_brand = brands.iloc[0]["品牌/厂商"]
    future_dates = sorted(forecast["统计月份"].dt.strftime("%Y-%m").unique().tolist())
    forecast_series = []
    for brand in metrics["brands"]:
        part = forecast[forecast["品牌/厂商"] == brand]
        forecast_series.append(
            {"name": brand, "type": "line", "smooth": True, "symbolSize": 5, "data": part["融合预测"].tolist()}
        )
    share_total = sum(
        int(forecast[forecast["品牌/厂商"] == brand]["融合预测"].sum()) for brand in metrics["brands"]
    )
    share = [
        round(int(forecast[forecast["品牌/厂商"] == brand]["融合预测"].sum()) / share_total * 100, 1)
        for brand in metrics["brands"]
    ]
    payload = {
        "years": yearly["年份"].astype(str).tolist(),
        "sales": yearly["销量"].tolist(),
        "brandNames": brands["品牌/厂商"].tolist(),
        "brandSales": brands["销量"].tolist(),
        "modelNames": models["车型"].tolist(),
        "modelSales": models["销量"].tolist(),
        "forecastDates": future_dates,
        "forecastSeries": forecast_series,
        "share": share,
        "colors": ["#1ABC9C", "#3498DB", "#D4AC0D", "#E74C3C", "#8E44AD"],
    }
    data_json = json.dumps(payload, ensure_ascii=False)
    (dashboard_dir / "data.json").write_text(data_json, encoding="utf-8")

    html = (
        TEMPLATE.replace("__RANGE__", f"{data['统计月份'].min():%Y-%m} 至 {data['统计月份'].max():%Y-%m}")
        .replace("__KPI_2025__", f"{last_year_sales / 10000:.0f} 万辆")
        .replace("__KPI_FORECAST__", f"{forecast_total / 10000:.1f} 万辆")
        .replace("__KPI_BRAND__", top_brand)
        .replace("__KPI_COVER__", f"{data['品牌/厂商'].nunique()} / {data['车型'].nunique()}")
        .replace("__DATA__", data_json)
    )
    (dashboard_dir / "index.html").write_text(html, encoding="utf-8")
    print(f"大屏已生成：{dashboard_dir / 'index.html'}")
    print("启动服务：python dashboard_app.py，然后打开 http://127.0.0.1:5000")


if __name__ == "__main__":
    main()
