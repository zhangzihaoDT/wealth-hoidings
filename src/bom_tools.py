import datetime as dt
import html as html_lib
import json
import re
from typing import Any, Iterable

import requests


CategoryName = str


CATEGORIES: list[CategoryName] = [
    "电池系统",
    "电驱系统",
    "底盘系统",
    "车身系统",
    "智能座舱",
    "智能驾驶",
    "内外饰",
]


CATEGORY_KEYWORDS: list[tuple[CategoryName, tuple[str, ...]]] = [
    (
        "电池系统",
        (
            "电池",
            "电芯",
            "电池容量",
            "kwh",
            "bms",
            "热管理",
            "充电",
            "快充",
            "慢充",
            "换电",
            "电池预热",
            "续航",
            "能耗",
            "cltc",
            "wlpt",
            "nedc",
            "soc",
            "电量",
            "电池包",
        ),
    ),
    (
        "电驱系统",
        (
            "电动机",
            "驱动电机",
            "电机",
            "电控",
            "电驱",
            "电驱动",
            "变速箱",
            "减速器",
            "四驱",
            "两驱",
            "驱动方式",
            "功率",
            "扭矩",
            "最高车速",
            "0-100",
            "加速",
        ),
    ),
    (
        "底盘系统",
        (
            "底盘",
            "悬架",
            "悬挂",
            "转向",
            "制动",
            "刹车",
            "轮胎",
            "轮毂",
            "通过角",
            "离地间隙",
            "最小转弯半径",
            "前桥",
            "后桥",
            "差速",
            "转向助力",
        ),
    ),
    (
        "智能座舱",
        (
            "座舱",
            "车机",
            "中控",
            "仪表",
            "hud",
            "抬头显示",
            "语音",
            "导航",
            "carplay",
            "carlife",
            "hicar",
            "蓝牙",
            "wifi",
            "热点",
            "5g",
            "ota",
            "芯片",
            "音响",
            "扬声器",
            "屏幕",
            "车载",
            "车内",
            "手机互联",
        ),
    ),
    (
        "智能驾驶",
        (
            "智能驾驶",
            "辅助驾驶",
            "l2",
            "acc",
            "aeb",
            "lka",
            "tja",
            "noa",
            "自动泊车",
            "遥控泊车",
            "倒车",
            "车道",
            "盲区",
            "摄像头",
            "雷达",
            "毫米波",
            "激光雷达",
            "超声波",
            "dms",
            "cms",
        ),
    ),
    (
        "内外饰",
        (
            "内饰",
            "外饰",
            "座椅",
            "方向盘",
            "氛围灯",
            "材质",
            "皮质",
            "织物",
            "大灯",
            "尾灯",
            "车灯",
            "后视镜",
            "雨刷",
            "天窗",
            "电动门",
            "后备厢",
            "行李厢",
            "电吸门",
            "门把手",
            "车门",
            "空调",
            "香氛",
        ),
    ),
    (
        "车身系统",
        (
            "车身",
            "车长",
            "车宽",
            "车高",
            "轴距",
            "整备质量",
            "质量",
            "结构",
            "安全气囊",
            "安全带",
            "儿童座椅",
            "iso",
            "碰撞",
            "车身颜色",
            "轮距",
            "最小离地间隙",
            "风阻",
        ),
    ),
]


DEFAULT_HEADERS = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "accept-language": "zh-CN,zh;q=0.9",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def parse_car_ids_from_url(url: str) -> list[int]:
    m = re.search(r"params-carIds-([^/?#]+)", url)
    if m:
        ids = [int(x) for x in re.findall(r"\d+", m.group(1))]
        if ids:
            return ids
    if "params-carIds-" in url:
        tail = url.split("params-carIds-", 1)[1]
        return [int(x) for x in re.findall(r"\d+", tail)]
    return []


def fetch_html(url: str, timeout_s: int = 20, headers: dict[str, str] | None = None) -> str:
    r = requests.get(url, headers=headers or DEFAULT_HEADERS, timeout=timeout_s)
    r.raise_for_status()
    r.encoding = "utf-8"
    return r.text


def strip_html(s: str) -> str:
    s = re.sub(r"<script[\s\S]*?</script>", "", s, flags=re.I)
    s = re.sub(r"<style[\s\S]*?</style>", "", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html_lib.unescape(s)
    s = s.replace("\xa0", " ")
    return re.sub(r"\s+", " ", s).strip()


def iter_div_blocks(html: str, marker: str) -> Iterable[str]:
    start = 0
    while True:
        idx = html.find(marker, start)
        if idx < 0:
            return
        div_start = html.rfind("<div", 0, idx)
        if div_start < 0:
            start = idx + len(marker)
            continue

        depth = 0
        i = div_start
        while i < len(html):
            next_open = html.find("<div", i)
            next_close = html.find("</div>", i)
            if next_close < 0:
                return
            if 0 <= next_open < next_close:
                depth += 1
                i = next_open + 4
                continue

            depth -= 1
            i = next_close + 6
            if depth == 0:
                yield html[div_start:i]
                start = i
                break


def extract_row_label(row_html: str) -> str | None:
    m = re.search(r'<label class="cell_label__\w+">(.*?)</label>', row_html)
    if not m:
        return None
    label = strip_html(m.group(1))
    return label or None


def extract_row_values(row_html: str) -> list[str]:
    values: list[str] = []
    for m in re.finditer(r'<div class="cell_[^"]+">(.*?)</div>', row_html):
        t = strip_html(m.group(1))
        if t:
            values.append(t)
    return values


def extract_param_rows(html: str) -> list[tuple[str, list[str]]]:
    rows: list[tuple[str, list[str]]] = []
    for row in iter_div_blocks(html, 'class="table_row__'):
        label = extract_row_label(row)
        if not label:
            continue
        values = extract_row_values(row)
        if not values:
            continue
        rows.append((label, values))
    return rows


def categorize_param_name(name: str) -> CategoryName:
    normalized = name.lower()
    for category, keywords in CATEGORY_KEYWORDS:
        for kw in keywords:
            if kw in normalized:
                return category
    return "内外饰"


def rows_to_categorized_kv_from_dom(rows: list[tuple[str, list[str]]]) -> dict[CategoryName, dict[str, Any]]:
    out: dict[CategoryName, dict[str, Any]] = {k: {} for k in CATEGORIES}
    for name, values in rows:
        category = categorize_param_name(name)
        value: Any = values[0] if len(values) == 1 else values
        if name in out[category]:
            existing = out[category][name]
            if isinstance(existing, list):
                existing.append(value)
            else:
                out[category][name] = [existing, value]
        else:
            out[category][name] = value
    return out


def _extract_next_data_json(html: str) -> dict[str, Any] | None:
    m = re.search(r'<script[^>]+id="__NEXT_DATA__"[^>]*>([\s\S]*?)</script>', html)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except Exception:
        return None


def _norm(s: str | None) -> str:
    return (s or "").strip().lower()


def _match_any(text: str, keywords: tuple[str, ...]) -> bool:
    t = _norm(text)
    return any(k in t for k in keywords)


def _format_info_value(info_value: Any) -> str | None:
    if info_value is None:
        return None
    if isinstance(info_value, dict):
        v = info_value.get("value")
        if v is None:
            return None
        s = str(v).strip()
        if not s or s in {"-", "—"}:
            return None
        price = str(info_value.get("config_price") or "").strip()
        if price:
            s = f"{s} {price}".strip()
        return s
    s = str(info_value).strip()
    if not s or s in {"-", "—"}:
        return None
    return s


def _extract_values_for_key(car_info: list[dict[str, Any]], key: str) -> Any | None:
    values: dict[str, str] = {}
    for car in car_info:
        name = str(car.get("car_name") or car.get("car_id") or "").strip() or "car"
        info = car.get("info") or {}
        if not isinstance(info, dict):
            continue
        formatted = _format_info_value(info.get(key))
        if formatted is None:
            continue
        values[name] = formatted
    if not values:
        return None
    if len(values) == 1:
        return next(iter(values.values()))
    return values


def _categorize_from_context(section: str, group: str, label: str, key: str) -> CategoryName:
    section_k = _norm(section)
    group_k = _norm(group)
    label_k = _norm(label)
    key_k = _norm(key)
    detail_text = " ".join([group_k, label_k, key_k])

    if "电池/充电" in section_k or _match_any(detail_text, ("battery", "电池", "充电", "快充", "慢充", "续航", "能耗")):
        return "电池系统"
    if _match_any(section_k, ("电动机", "发动机", "变速箱")) or _match_any(detail_text, ("电机", "扭矩", "功率", "变速箱", "减速器", "四驱", "两驱")):
        return "电驱系统"
    if _match_any(section_k, ("车身", "基本信息")) or _match_any(detail_text, ("车长", "车宽", "车高", "轴距", "整备质量", "结构", "碰撞")):
        return "车身系统"

    if _match_any(detail_text, ("安全气囊", "安全带", "儿童座椅", "isofix", "被动安全")):
        return "车身系统"
    if _match_any(detail_text, ("车道", "碰撞", "预警", "aeb", "acc", "tja", "lka", "noa", "泊车", "影像", "雷达", "摄像头", "激光雷达", "毫米波", "超声波", "dms", "cms", "辅助驾驶", "巡航")):
        return "智能驾驶"
    if _match_any(detail_text, ("中控", "仪表", "hud", "屏幕", "车机", "语音", "导航", "车载智能", "蓝牙", "wifi", "app", "ota", "音响", "扬声器")):
        return "智能座舱"
    if _match_any(detail_text, ("座椅", "方向盘", "氛围灯", "后视镜", "遮阳帘", "车窗", "车门", "尾门", "后备厢", "天窗", "雨刷", "空调", "冰箱", "香氛", "脚踏板")):
        return "内外饰"

    if "智能化配置" in section_k:
        return "智能座舱"
    if _match_any(section_k, ("底盘/转向", "车轮/制动")) or _match_any(detail_text, ("悬架", "转向", "制动", "轮胎", "轮毂", "差速", "驻车制动", "空气悬挂")):
        return "底盘系统"
    if _match_any(section_k, ("车轮/制动",)):
        return "底盘系统"
    return "内外饰"


def _extract_bom_from_next_data(html: str) -> tuple[dict[str, Any], dict[CategoryName, dict[str, Any]]] | None:
    data = _extract_next_data_json(html)
    if not data:
        return None
    raw = data.get("props", {}).get("pageProps", {}).get("rawData", {})
    properties = raw.get("properties") or []
    car_info = raw.get("car_info") or []
    if not isinstance(car_info, list):
        car_info = []

    out: dict[CategoryName, dict[str, Any]] = {k: {} for k in CATEGORIES}
    section = ""
    group = ""
    seen_keys: set[str] = set()

    def key_exists(k: str) -> bool:
        if not k:
            return False
        for car in car_info:
            info = car.get("info") or {}
            if isinstance(info, dict) and k in info:
                return True
        return False

    def add_param(sec: str, grp: str, lab: str, k: str) -> None:
        nonlocal out, seen_keys
        if not k or k in seen_keys:
            return
        seen_keys.add(k)
        value = _extract_values_for_key(car_info, k)
        if value is None:
            return
        category = _categorize_from_context(sec, grp, lab, k)
        out[category][lab] = value

    for p in properties:
        t = p.get("type")
        if t == 0:
            section = str(p.get("text") or "")
            group = ""
            continue
        if t == 3:
            group = str(p.get("text") or "")
            k = str(p.get("key") or "")
            if key_exists(k):
                add_param(section, group, group, k)
                continue
            for sub in p.get("sub_list") or []:
                if isinstance(sub, dict):
                    sub_key = str(sub.get("key") or "")
                    if key_exists(sub_key):
                        add_param(section, group, str(sub.get("text") or ""), sub_key)
            continue
        if t == 1:
            add_param(section, group, str(p.get("text") or ""), str(p.get("key") or ""))

    car_ids = [int(c.get("car_id")) for c in car_info if str(c.get("car_id") or "").isdigit()]
    meta = {
        "car_ids": car_ids,
        "car_names": [c.get("car_name") for c in car_info if c.get("car_name")],
        "row_count": sum(len(v) for v in out.values()),
    }
    return meta, out


def build_bom_json(url: str, timeout_s: int = 20, headers: dict[str, str] | None = None) -> dict[str, Any]:
    html = fetch_html(url, timeout_s=timeout_s, headers=headers)
    extracted = _extract_bom_from_next_data(html)
    if extracted:
        meta_extra, data = extracted
        return {
            "meta": {
                "source_url": url,
                "car_ids": meta_extra.get("car_ids") or parse_car_ids_from_url(url),
                "car_names": meta_extra.get("car_names") or [],
                "fetched_at": dt.datetime.now(tz=dt.timezone.utc).isoformat(),
                "row_count": meta_extra.get("row_count") or 0,
            },
            "data": data,
        }

    rows_dom = extract_param_rows(html)
    return {
        "meta": {
            "source_url": url,
            "car_ids": parse_car_ids_from_url(url),
            "fetched_at": dt.datetime.now(tz=dt.timezone.utc).isoformat(),
            "row_count": len(rows_dom),
        },
        "data": rows_to_categorized_kv_from_dom(rows_dom),
    }
