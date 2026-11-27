"""Build the bilingual GitHub Pages site and downloadable public CV."""
import json
from html import escape as h

from PIL import Image
from public_cv import build_cv
from publications import bibtex, publications_section
from research import (
    expertise_section,
    project_page,
    selected_section,
    systems_section,
    themes_section,
)
from site_data import (
    CV,
    PAPERS,
    PORTRAIT,
    PREVIEW,
    PROFILE,
    PROJECTS,
    RESOURCES,
    ROOT,
    SITE,
    academic_links,
    bi,
    dates,
    download_cv,
    external,
    figure,
    heading,
    link,
    links,
    list_items,
    local,
    paragraph,
    section,
)

NAV = [
    ("about", ("Home", "首页")), ("research", ("Research", "科学研究")),
    ("experimental-systems", ("Experimental Systems", "实验系统")), ("publications", ("Publications", "学术成果")),
    ("software-data", ("Software & Data", "软件与数据")), ("experience", ("Experience", "个人经历")),
    ("cv", ("CV", "学术简历")), ("contact", ("Contact", "联系合作")),
]

TITLE = (
    "Baoding Wang | Laser–EMAT, Ultrasonics & NDE | Wuhan University",
    "王宝定 | 激光–电磁超声与无损评价 | 武汉大学",
)
DESCRIPTION = (
    "Baoding Wang (王宝定), PhD student at Wuhan University. Laser–EMAT systems, "
    "non-contact ultrasonic inspection, physics-informed imaging, publications and open research software."
)


def header(is_research):
    prefix = "index.html" if is_research else ""
    navigation = "".join(
        local(f"{prefix}#{key}", name) if not (is_research and key == "research")
        else local("#research", name)
        for key, name in NAV
    )
    return f'''<a class="skip" href="#main">{bi(("Skip to content", "跳转到正文"))}</a>
    <header class="topbar">
      <div class="topbar-inner">
        {local(prefix + "#about", (PROFILE["name"], PROFILE["chinese_name"]), "wordmark")}
        <nav class="topnav" id="site-nav" aria-label="Main navigation" data-label-zh="主导航">{navigation}</nav>
        <div class="topbar-controls">
          <button id="menu-toggle" type="button" aria-controls="site-nav" aria-expanded="false" hidden>{bi(("Menu", "菜单"))}</button>
          <button id="language" type="button" lang="zh-CN" hidden>中文</button>
        </div>
      </div>
    </header>'''


def shell(body, is_research=False):
    path = "research.html" if is_research else ""
    title = ("Research Portfolio | Baoding Wang", "科研档案 | 王宝定") if is_research else TITLE
    desc = (
        "Research portfolio of Baoding Wang. Laser–EMAT, ultrasonic experimental systems, air-coupled measurements "
        "and physics-informed ultrasonic imaging." if is_research else DESCRIPTION
    )
    user = f"{PROFILE['name']} ({PROFILE['chinese_name']})"
    profiles = [PROFILE["github"], PROFILE["orcid"]]
    if PROFILE.get("scholar"):
        profiles.append(PROFILE["scholar"])
    schema = {
        "@context": "https://schema.org", "@type": "Person", "@id": SITE + "#baoding-wang",
        "name": PROFILE["name"], "alternateName": PROFILE["chinese_name"], "url": SITE,
        "image": SITE + PORTRAIT, "jobTitle": PROFILE["role"][0], "email": "mailto:" + PROFILE["emails"][0],
        "affiliation": {
            "@type": "CollegeOrUniversity", "name": PROFILE["university"][0], "url": "https://en.whu.edu.cn/",
        },
        "sameAs": profiles, "knowsAbout": PROFILE["interests"],
    }
    metadata = json.dumps(schema, ensure_ascii=False).replace("<", "\\u003c")
    return f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<title>{h(title[0])}</title>
<meta name="description" content="{h(desc)}">
<link rel="canonical" href="{SITE + path}"><link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<meta property="og:type" content="{"website" if is_research else "profile"}">
<meta property="og:title" content="{h(title[0])}"><meta property="og:description" content="{h(desc)}">
<meta property="og:url" content="{SITE + path}"><meta property="og:image" content="{SITE + PREVIEW}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{h(user)} at Wuhan University">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{metadata}</script>
<link rel="stylesheet" href="assets/academic.css">
<script src="assets/academic.js" defer></script>
</head><body data-title-en="{h(title[0])}" data-title-zh="{h(title[1])}">
{header(is_research)}<main id="main" tabindex="-1">{body}</main>
<footer class="footer"><div class="wrap footer-inner">
  <span>{h(user)}</span>
  {local(("index.html" if is_research else "") + "#contact", ("Contact", "联系合作"))}
</div></footer>
<dialog id="figure-dialog" aria-labelledby="figure-caption">
  <div class="dialog-toolbar">
    <a id="figure-original" target="_blank" rel="noopener noreferrer">{bi(("Open full-resolution image ↗", "打开原图 ↗"))}</a>
    <button id="figure-close" class="button" type="button">{bi(("Close", "关闭"))}</button>
  </div>
  <figure><img id="figure-full" alt=""><figcaption id="figure-caption"></figcaption></figure>
</dialog>
<p class="sr-only" id="feedback" role="status"></p>
</body></html>
'''


def hero():
    published = [p for p in PAPERS.values() if p["status"] == "published"]
    first = sum(p["authors"][0] in (PROFILE["name"], PROFILE["chinese_name"]) for p in published)
    stats = [
        (len(published), ("Published Journal Articles", "已发表期刊论文"), "#publications"),
        (first, ("First-Listed Author Articles", "列名第一论文"), "#publications"),
        (len(PROFILE["patents"]), ("Granted Invention Patents", "授权发明专利"), "#publications"),
        (len(RESOURCES), ("Open-Source Research Projects", "开源科研项目"), "#software-data"),
    ]
    metrics = "".join(
        f'<li>{link(url, f"<strong>{number}</strong>{bi(label)}")}</li>' for number, label, url in stats
    )
    buttons = [
        download_cv(), local("#experimental-systems", ("Experimental Systems", "实验系统"), "button"),
        local("research.html", ("Explore My Research →", "浏览科研档案 →"), "button"),
    ]
    profile_links = academic_links() + [local("#contact", ("Contact Me", "与我联系"))]
    with Image.open(ROOT / PORTRAIT) as image:
        width, height = image.size
    affiliation = (f'{PROFILE["school"][0]}, Wuhan University, China', f'中国武汉大学{PROFILE["school"][1]}')
    dates_label = (
        f'{PROFILE["phd_start"][0]} – Present · Expected graduation {PROFILE["graduation"][0]}',
        f'{PROFILE["phd_start"][1]}至今 · 预计{PROFILE["graduation"][1]}毕业',
    )
    return f'''<section class="hero" id="about" aria-labelledby="hero-title">
      <div class="wrap">
        <div class="hero-layout">
          <div class="hero-intro">
            <p class="identity">{bi((PROFILE["name"], PROFILE["chinese_name"]))}
              <span class="identity-alt en" lang="zh-CN">{h(PROFILE["chinese_name"])}</span>
              <span class="identity-alt zh" lang="en">{h(PROFILE["name"])}</span>
            </p>
            <p class="profile-role">{bi(PROFILE["role"])} · {bi(PROFILE["university"])}</p>
          </div>
          <div class="hero-copy">
            <h1 id="hero-title">{bi(PROFILE["hero"]["title"])}</h1>
            {paragraph(PROFILE["hero"]["subtitle"], "subtitle")}
            <div class="hero-prose">{"".join(paragraph(p) for p in PROFILE["hero"]["paragraphs"])}</div>
            {links(buttons, "hero-actions")}{links(profile_links)}
          </div>
          <aside class="profile-panel">
            <img class="portrait" src="{PORTRAIT}" width="{width}" height="{height}" fetchpriority="high"
              alt="Portrait of Baoding Wang" data-alt-zh="王宝定的个人照片">
            <div class="profile-detail">{paragraph(affiliation)}
              <p class="muted">{bi(("Supervisor", "导师"))} · {external(PROFILE["supervisor_url"], bi(PROFILE["supervisor"]))}</p>
              {paragraph(dates_label, "muted")}
            </div>
          </aside>
        </div>
        <ul class="facts">{metrics}</ul>
      </div>
    </section>'''


def software_section():
    cards = []
    for resource in RESOURCES:
        paper = PAPERS[resource["paper"]]
        repo = paper["code"]
        readme = f'{repo}/blob/{resource["branch"]}/README.md'
        actions = [external(repo, "GitHub ↗"), external(readme, "README ↗")]
        if paper.get("data"):
            actions.append(external(paper["data"], bi(("Dataset ↗", "数据 ↗"))))
        actions.append(local(f'#paper-{paper["id"]}', ("Associated Publication", "关联论文")))
        if resource["project"] in PROJECTS:
            actions.append(local(f'research.html#{resource["project"]}', ("Research results", "代表性结果")))
        cards.append(f'''<article class="card">
          <p class="muted">{bi(("Public repository", "公开代码仓库"))} · {h(resource["license"])}</p>
          {heading(resource["title"], 3)}{paragraph(resource["description"])}
          <p class="muted">{h(resource["stack"])}</p>{figure(resource["figure"])}{links(actions)}
        </article>''')
    return section("software-data", ("Open Science & Software", "开源科研软件与数据"),
        f'<div class="card-grid">{"".join(cards)}</div>')


def experience_section():
    timeline = []
    for entry in PROFILE["experience"]:
        supervisor = ""
        if entry.get("supervisor"):
            supervisor = (
                f'<p class="muted">{bi(("Supervisor", "导师"))} · '
                f'{external(entry["url"], bi(entry["supervisor"]))}</p>'
            )
        graduation = ""
        if entry["id"] == "wuhan":
            graduation = f'<p class="muted">{bi(("Expected graduation", "预计毕业"))} · {bi(PROFILE["graduation"])}</p>'
        timeline.append(f'''<li class="timeline-item">
          <p class="timeline-date">{bi(entry["dates"])}</p>
          <div>{heading(entry["name"], 3)}{paragraph(entry["role"], "timeline-role")}
          {paragraph(entry["body"])}{supervisor}{graduation}</div></li>''')
    return section("experience", ("Education & Industry Experience", "教育背景与工业经历"),
        paragraph(("Mechanical Design → Laser-Ultrasonic Research → Software Engineering → Advanced Ultrasonics and Intelligent Imaging",
                   "机械设计 → 激光超声科研 → 软件工程 → 先进超声与智能成像"), "subtitle")
        + f'<ol class="timeline">{"".join(timeline)}</ol>')


def honours_section():
    return section("honors", ("Research Projects & Honours", "科研项目与荣誉奖励"),
        '<div class="card-grid">'
        f'<article class="card">{heading(("Research Project Participation", "参与科研项目"), 3)}'
        f'{list_items(map(bi, PROFILE["grants"]))}</article>'
        f'<article class="card">{heading(("Honours & Academic Communication", "荣誉与学术交流"), 3)}'
        f'{list_items(map(bi, [*PROFILE["honours"], PROFILE["presentation"]]))}'
        f'{paragraph(PROFILE["languages"], "muted")}</article></div>')


def cv_section():
    return section("cv", ("Academic CV", "学术简历"),
        f'<div class="cv-panel"><div>{paragraph(("Public academic CV · English PDF", "公开版学术简历 · 英文 PDF"))}'
        f'<p class="muted">{bi(("Updated", "更新于"))} {dates(PROFILE["cv"]["updated"])}</p></div>{download_cv()}</div>')


def contact_section():
    csc = PROFILE["csc"]
    csc_html = ""
    if csc["enabled"]:
        en, zh = csc["start"]
        months = csc["months"]
        csc_html = f'''<aside class="csc">
          {heading(("Visiting PhD Research", "博士联合培养访问研究"), 3)}
          {paragraph((f"I am seeking a {months}-month visiting PhD opportunity starting in {en} through the China Scholarship Council (CSC) joint doctoral training programme, subject to funding and host-institution approval.",
                       f"我正在准备国家留学基金委（CSC）联合培养博士项目，计划于{zh}开始为期 {months} 个月的访问研究，具体安排以资助及外方院校批准为准。"))}
        </aside>'''
    contacts = [link(f"mailto:{email}", h(email)) for email in PROFILE["emails"]]
    contacts += academic_links()
    return section("contact", ("Research Collaboration & Contact", "科研合作与联系方式"),
        paragraph(("I welcome research collaboration in advanced ultrasonics, non-contact nondestructive evaluation, quantitative defect characterisation, experimental system development and physics-informed computational imaging.",
                   "欢迎就先进超声、非接触无损评价、缺陷定量表征、实验系统研发及物理信息计算成像开展合作。"))
        + paragraph(("I am interested in combining a host team’s experimental facilities and expertise with my experience in Laser–EMAT, automated instrumentation, scientific software and intelligent imaging.",
                     "希望将合作团队的实验设施与科研积累，同我在 Laser–EMAT、自动化测控、科研软件和智能成像方面的经验结合。"))
        + links(contacts) + csc_html)


def write(name, content):
    (ROOT / name).write_text("\n".join(line.rstrip() for line in content.splitlines()) + "\n", encoding="utf-8")


def main():
    if CV:
        if PROFILE["cv"].get("generate", True):
            build_cv(PROFILE, PAPERS.values(), ROOT / CV)
        if CV != "Baoding_Wang_CV.pdf":
            (ROOT / "Baoding_Wang_CV.pdf").write_bytes((ROOT / CV).read_bytes())
    body = (
        hero() + '<div class="wrap main-sections">' + themes_section() + systems_section()
        + selected_section() + expertise_section() + publications_section()
        + software_section() + experience_section() + honours_section() + cv_section() + contact_section() + "</div>"
    )
    write("index.html", shell(body))
    write("research.html", shell(project_page(), is_research=True))
    write("publications.bib", "\n\n".join(map(bibtex, PAPERS.values())) + "\n")
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE}sitemap.xml\n")
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          f'  <url><loc>{SITE}</loc></url>\n  <url><loc>{SITE}research.html</loc></url>\n</urlset>\n')
    print(f"Built both pages, bibliography, SEO files and CV for {len(PAPERS)} public articles.")


if __name__ == "__main__":
    main()
