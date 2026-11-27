"""Shared site content and helpers for the static renderers."""
import json
from datetime import date
from html import escape as h
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    return json.loads((ROOT / "data" / f"{name}.json").read_text(encoding="utf-8-sig"))


PROFILE = load("profile")
def public_records(records):
    return {record["id"]: record for record in records if record.get("public", True)}


PAPERS = public_records(
    paper for paper in load("publications")
    if paper["status"] not in ("submitted", "revision") or paper.get("public") is True
)
RESEARCH = load("research")
PROJECTS = public_records(RESEARCH["projects"])
THEMES = public_records(RESEARCH["themes"])
SYSTEMS = public_records(load("systems"))
EXPERTISE = load("expertise")
RESOURCES = [resource for resource in load("resources")
             if resource.get("public", True) and resource["paper"] in PAPERS]
SITE = PROFILE["site"]
PORTRAIT = "assets/images/profile/baoding-wang.jpg"
PREVIEW = "assets/images/profile/social-preview.jpg"
CV = PROFILE["cv"]["file"]

STATUS = {
    "published": ("Published", "已发表"),
    "accepted": ("Accepted / In Press", "已录用／待刊"),
    "submitted": ("Submitted Manuscripts", "已投稿"),
    "revision": ("Manuscripts in Revision", "返修中"),
    "preprint": ("Preprints", "预印本"),
    "ongoing": ("Ongoing Research", "在研"),
    "preliminary": ("Preliminary Experiments", "初步实验"),
    "future": ("Research Direction", "拟开展方向"),
    "mixed": ("Published & Ongoing", "已发表及在研"),
    "independent": ("Independently Developed", "自主研发"),
    "collaborative": ("Collaboratively Developed", "合作研发"),
    "hands-on": ("Hands-on Experience", "实验操作经验"),
    "development": ("Under Development", "研发中"),
}

ROLES = {
    "first": ("First-listed author", "列名第一"),
    "cofirst": ("First-listed author · Equal contribution", "列名第一 · 共同贡献"),
    "equal": ("Equal contribution", "共同贡献"),
    "second": ("Second author", "第二作者"),
    "coauthor": ("Co-author", "共同作者"),
}


def bi(words):
    en, zh = words
    return f'<span class="en">{h(en)}</span><span class="zh" lang="zh-CN">{h(zh)}</span>'


def link(url, label, cls="", attrs=""):
    style = f' class="{h(cls)}"' if cls else ""
    return f'<a href="{h(url, quote=True)}"{style}{attrs}>{label}</a>'


def local(url, label, cls=""):
    return link(url, bi(label), cls)


def external(url, label):
    return link(url, label, attrs=' target="_blank" rel="noopener noreferrer"')


def links(items, cls="resource-links"):
    return f'<div class="{cls}">{"".join(items)}</div>' if items else ""


def paragraph(words, cls=""):
    style = f' class="{cls}"' if cls else ""
    return f"<p{style}>{bi(words)}</p>" if words else ""


def heading(words, level=2):
    return f"<h{level}>{bi(words)}</h{level}>"


def section(anchor, title, content):
    return (
        f'<section class="section" id="{anchor}" aria-labelledby="{anchor}-title">'
        f'<h2 id="{anchor}-title">{bi(title)}</h2>{content}</section>'
    )


def badge(status):
    return f'<span class="status status-{status}">{bi(STATUS[status])}</span>'


def list_items(items, cls=""):
    return f'<ul class="{cls}">' + "".join(f"<li>{item}</li>" for item in items) + "</ul>"


def definition_list(fields):
    return '<dl class="details-grid">' + "".join(
        f"<div><dt>{bi(label)}</dt><dd>{content}</dd></div>"
        for label, content in fields if content
    ) + "</dl>"


def figure(key):
    item = RESEARCH["figures"].get(key)
    if not item or not item.get("public") or not (ROOT / item["path"]).is_file():
        return ""
    path = h(item["path"])
    en, zh = map(h, item["alt"])
    with Image.open(ROOT / item["path"]) as image:
        width, height = image.size
    return f'''<figure class="research-visual">
      <a class="figure-link" href="{path}" data-figure>
        <img src="{path}" width="{width}" height="{height}" alt="{en}" data-alt-zh="{zh}" loading="lazy" decoding="async">
        <span class="figure-expand" aria-hidden="true">⤢</span>
      </a>
      <figcaption>{bi(item["caption"])}</figcaption>
    </figure>'''


def videos(items):
    output = []
    for video in items:
        if not video.get("public") or not (ROOT / video["path"]).is_file():
            continue
        poster = f' poster="{h(video["poster"])}"' if video.get("poster") else ""
        tracks = "".join(
            f'<track kind="captions" src="{h(track["path"])}" srclang="{h(track["lang"])}" label="{h(track["label"])}">'
            for track in video.get("captions", []) if (ROOT / track["path"]).is_file()
        )
        output.append(
            f'<figure class="research-visual"><video controls preload="none"{poster} '
            f'src="{h(video["path"])}">{tracks}</video><figcaption>{bi(video["caption"])}</figcaption></figure>'
        )
    return "".join(output)


def project_references(ids):
    items = [local(f"research.html#{key}", PROJECTS[key]["name"]) for key in ids if key in PROJECTS]
    return list_items(items, "reference-list") if items else ""


def academic_links():
    items = [external(PROFILE["github"], "GitHub ↗"), external(PROFILE["orcid"], "ORCID ↗")]
    if PROFILE.get("scholar"):
        items.append(external(PROFILE["scholar"], "Google Scholar ↗"))
    return items


def dates(value):
    day = date.fromisoformat(value)
    label = day.strftime("%B ") + str(day.day) + f", {day.year}"
    return f'<time datetime="{value}">{bi((label, f"{day.year} 年 {day.month} 月 {day.day} 日"))}</time>'


def download_cv(cls="button primary"):
    if not CV:
        return paragraph(("Academic CV download pending.", "学术简历下载文件待补充。"), "muted")
    return link(CV, bi(("Download Academic CV ↓", "下载学术简历 ↓")), cls, f' download="{h(CV)}"')
