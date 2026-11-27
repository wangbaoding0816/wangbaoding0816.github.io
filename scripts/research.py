"""Render research themes, laboratory systems and the linkable project archive."""
from publications import doi_link, paper_references, resource_links
from site_data import (
    EXPERTISE,
    PAPERS,
    PROJECTS,
    RESEARCH,
    SYSTEMS,
    THEMES,
    badge,
    bi,
    definition_list,
    figure,
    heading,
    link,
    links,
    list_items,
    local,
    paragraph,
    project_references,
    section,
    videos,
)

ALL_RESEARCH = ("View All Research →", "查看全部研究 →")


def themes_section():
    cards = []
    for theme in THEMES.values():
        related = [PROJECTS[key] for key in theme["projects"] if key in PROJECTS]
        media = next((rendered for project in related if (rendered := figure(project["figure"]))), "")
        papers = list(dict.fromkeys(paper_id for project in related for paper_id in project["papers"]))
        fields = [
            (("Research question", "科学问题"), bi(theme["question"])),
            (("Methods", "研究技术"), bi(theme["methods"])),
            (("Related work", "代表性研究"), project_references(theme["projects"])),
        ]
        if papers:
            fields.append((("Related publications", "关联论文"), paper_references(papers)))
        cards.append(f'''<article class="card theme" id="theme-{theme["id"]}">
          <div class="card-heading">{badge(theme["status"])}{heading(theme["name"], 3)}</div>
          {paragraph(theme["background"])}
          <details><summary>{bi(("Questions, methods & related work", "科学问题、方法与成果"))}</summary>
          {definition_list(fields)}{media}</details></article>''')
    return section("research", ("Research Themes", "核心研究方向"),
        links([local("research.html", ALL_RESEARCH, "button")])
        + f'<div class="card-grid">{"".join(cards)}</div>')


def system_card(system):
    system_id = system["id"]
    media = "".join(figure(item) for item in system["figures"])
    featured = f'<div class="media-grid">{media}</div>' if media else ""
    fields = [
        (("Hardware configuration", "硬件配置"), bi(system["hardware"])),
        (("Control & acquisition", "测控与采集"), bi(system["control"])),
        (("Experimental capabilities", "实验能力"), bi(system["capabilities"])),
        (("Representative results", "代表性结果"), bi(system["results"]) if system["results"] else ""),
        (("Related publications", "关联论文"), paper_references(system["papers"])),
        (("Related research", "关联研究"), project_references(system["projects"])),
    ]
    return f'''<article class="card system-card" id="system-{system_id}">
      <div class="card-heading">{badge(system["status"])}{heading(system["name"], 3)}</div>
      {paragraph(system["overview"])}
      {definition_list([(("My contribution", "个人贡献"), bi(system["contribution"]))])}
      {figure(system.get("cover"))}
      <details>
        <summary>{bi(("Configuration, capabilities & evidence", "配置、能力与研究证据"))}</summary>
        {definition_list(fields)}{featured}{videos(system.get("videos", []))}
      </details>
    </article>'''


def systems_section():
    return section("experimental-systems", ("Experimental Systems & Instrumentation", "实验系统与仪器平台"),
        paragraph(("Platforms, control software and instruments used in my ultrasonic research.",
                   "超声研究中使用的实验平台、测控软件与仪器。"), "section-description")
        + f'<div class="card-grid">{"".join(map(system_card, SYSTEMS.values()))}</div>')


def selected_section():
    summaries = []
    for project in list(PROJECTS.values())[:5]:
        project_id = project["id"]
        media = figure(project["figure"])
        cls = "selected wide" if project_id == "deep-laser-emat" else "selected"
        title = local(f"research.html#{project_id}", project["name"])
        anchor = ' id="featured-tim-title"' if project_id == "am-topography" else ""
        evidence_link = local(f"research.html#{project_id}", ("Research details →", "查看研究详情 →"))
        publications = [doi_link(PAPERS[pid]) for pid in project["papers"] if pid in PAPERS]
        # Each full research entry identifies every associated paper.
        primary_doi = publications[:1] if len(publications) == 1 else []
        summaries.append(f'''<article class="card {cls}">
          <div class="card-heading">{badge(project["status"])}<h3{anchor}>{title}</h3></div>
          {paragraph(project["findings"] if project["status"] == "published" else project["method"])}
          {media}{links([evidence_link, *primary_doi])}
        </article>''')
    actions = [local("research.html", ALL_RESEARCH, "button")]
    if "mode-conversion" in PROJECTS:
        actions.append(link("research.html#mode-conversion",
                            bi(("Ongoing research on mode conversion in 316L →", "316L 模式转换在研工作 →")),
                            attrs=' id="ongoing"'))
    return section("selected-research", ("Selected Research", "代表性科研成果"),
        f'<div class="card-grid">{"".join(summaries)}</div>' + links(actions))


def expertise_section():
    cards = "".join(
        f'<article class="card expertise">{heading(title, 3)}{paragraph(body)}</article>'
        for title, body in EXPERTISE["expertise"]
    )
    flow = "".join(f'<li>{bi(stage)}</li>' for stage in EXPERTISE["workflow"])
    support = (
        ("Research Resource Integration and Problem Solving", "科研资源整合与问题解决"),
        ("I adapt existing laboratory instruments, software and expertise to design new experiments, extend system capabilities and validate methods.",
         "结合实验室现有仪器、软件与技术积累，通过复用和二次开发设计新实验、拓展系统能力并验证方法。"),
    )
    subtitle = ("AI-assisted development and research resource integration support every stage.",
                "AI 辅助科研开发与实验室资源整合贯穿全流程。")
    return section("capabilities", ("Technical Expertise", "科研与工程能力"),
        f'<div class="card-grid expertise-grid">{cards}</div>'
        f'<div class="workflow">{heading(("Research Development Workflow", "科研研发流程"), 3)}'
        f'<ol>{flow}</ol>{paragraph(subtitle, "workflow-support")}</div>'
        f'<div class="resource-integration">{heading(support[0], 3)}{paragraph(support[1])}</div>')


def project_page():
    cards = []
    for project in PROJECTS.values():
        project_id = project["id"]
        system = SYSTEMS.get(project["system"])
        publications = paper_references(project["papers"], "index.html")
        resources = [item for pid in project["papers"] if pid in PAPERS for item in resource_links(PAPERS[pid])]
        details = [
            (("Motivation", "研究动机"), bi(project["motivation"])),
            (("Methodology", "研究方法"), bi(project["method"])),
            (("Experimental system", "实验系统"),
             local(f'index.html#system-{system["id"]}', system["name"]) if system else ""),
            (("My contribution", "个人贡献"), bi(project["contribution"])),
            (("Key findings", "主要结果"), bi(project["findings"]) if project["findings"] else ""),
            (("Publications", "关联论文"), publications),
            (("Code & data", "代码与数据"), links(resources)),
        ]
        extensions = "".join(
            f'<aside class="csc" id="{extra["id"]}">{badge("ongoing")}'
            f'{heading(extra["name"], 3)}{paragraph(extra["text"])}</aside>'
            for extra in RESEARCH["extensions"] if extra["parent"] == project_id and extra.get("public", True)
        )
        media = figure(project["figure"])
        cards.append(f'''<article class="project" id="{project_id}">
          <div class="card-heading">{badge(project["status"])}{heading(project["name"])}</div>
          {paragraph(project["question"], "research-question")}
          <div class="project-content{"" if media else " no-figure"}">{definition_list(details)}{media}</div>
          {videos(project.get("videos", []))}{extensions}
        </article>''')
    contents = list_items([local("#" + p["id"], p["name"]) for p in PROJECTS.values()], "project-index")
    return f'''<div class="wrap archive" id="research">
      <header class="archive-header">
        {local("index.html#research", ("← Research Themes", "← 核心研究方向"))}
        {heading(("Research Portfolio", "科研档案"), 1)}
        {contents}
      </header>
      <div class="project-list" id="ongoing">{"".join(cards)}</div>
    </div>'''
