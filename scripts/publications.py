"""Render the bibliography, filters and patent records."""
from html import escape as h

from site_data import (
    PAPERS,
    PROFILE,
    ROLES,
    STATUS,
    THEMES,
    badge,
    bi,
    definition_list,
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

STATUS_ORDER = ("published", "accepted", "submitted", "revision", "preprint")


def publication_title(paper):
    en = paper["translated_title"] if paper.get("in_chinese") else paper["title"]
    return en, paper["title_zh"]


def resource_links(paper):
    items = []
    if paper.get("pdf"):
        items.append(link(paper["pdf"], h("PDF ↗")))
    if paper.get("code"):
        items.append(external(paper["code"], bi(("Code ↗", "代码 ↗"))))
    if paper.get("data"):
        items.append(external(paper["data"], bi(("Dataset ↗", "数据 ↗"))))
    return items


def doi_link(paper):
    return external("https://doi.org/" + paper["doi"], "DOI ↗") if paper.get("doi") else ""


def paper_references(ids, prefix=""):
    items = [
        link(f"{prefix}#paper-{paper_id}", bi(publication_title(PAPERS[paper_id])))
        for paper_id in ids if paper_id in PAPERS
    ]
    return list_items(items, "reference-list") if items else ""


def authors(paper):
    rendered = []
    for name in paper["authors"]:
        label = h(name)
        if name in (PROFILE["name"], PROFILE["chinese_name"]):
            label = f"<strong>{label}</strong>"
        if name in paper.get("equal_authors", []):
            label += "<sup>†</sup>"
        if name in (paper.get("corresponding_authors") or []):
            label += "<sup>*</sup>"
        rendered.append(label)
    return ", ".join(rendered)


def venue(paper):
    citation = f'<em>{h(paper["journal"])}</em>'
    if paper.get("volume"):
        citation += " " + h(paper["volume"])
    if paper.get("issue"):
        citation += f'({h(paper["issue"])})'
    if paper.get("article_number"):
        citation += ", " + bi((
            f'Art. no. {paper["article_number"]}', f'文章编号 {paper["article_number"]}',
        ))
    if paper.get("pages"):
        citation += ", " + h(paper["pages"])
    return citation + f' ({paper["year"]}).'


def bibtex(paper):
    names = []
    for name in paper["authors"]:
        given, sep, family = name.rpartition(" ")
        names.append(f"{family}, {given}" if sep else name)
    fields = [
        ("title", "{" + paper["title"] + "}"),
        ("author", " and ".join(names)),
        ("journal", paper["journal"]),
        ("year", str(paper["year"])),
        ("volume", paper.get("volume")),
        ("number", paper.get("issue")),
        ("pages", (paper.get("pages") or paper.get("article_number") or "").replace("–", "--")),
        ("eid", paper.get("article_number")),
        ("doi", paper.get("doi")),
        ("note", STATUS[paper["status"]][0] if paper["status"] != "published" else None),
    ]
    key = f'Wang{paper["year"]}{paper["id"].replace("-", "")}'
    rows = "\n".join(f"  {field} = {{{value}}}," for field, value in fields if value)
    return f"@article{{{key},\n{rows}\n}}"


def publication(paper):
    paper_id = paper["id"]
    status = paper["status"]
    online = ""
    if paper.get("online_year"):
        year = paper["online_year"]
        online = paragraph((f"First published online in {year}.", f"于 {year} 年首次在线发表。"), "muted")
    if paper.get("published_en"):
        online = paragraph((paper["published_en"], paper["published_zh"]), "muted")
    citation = (
        f'<details class="bibtex"><summary>{bi(("BibTeX citation", "BibTeX 引文"))}</summary>'
        f'<button class="button copy-button" type="button" data-copy="bib-{paper_id}" hidden>'
        f'<span data-copy-label>{bi(("Copy BibTeX", "复制 BibTeX"))}</span>'
        f'<span data-copy-confirmation hidden>{bi(("Copied", "已复制"))}</span></button>'
        f'<pre id="bib-{paper_id}" tabindex="0">{h(bibtex(paper))}</pre></details>'
    )
    original = h(paper["title"])
    alternate = f'<p class="paper-translation zh" lang="en">{original}</p>'
    if paper.get("in_chinese"):
        alternate = f'<p class="paper-translation en" lang="zh-CN">{original}</p>'
    themes = " ".join(paper["themes"])
    role = paper["role"]
    status_label = badge(status) if status != "published" else ""
    contribution = (paper["contribution_en"], paper["contribution_zh"])
    return f'''<article class="publication" id="paper-{paper_id}" data-doi="{h(paper.get("doi") or "")}"
      data-year="{paper["year"]}" data-status="{status}" data-themes="{themes}" data-role="{role}">
      <h4>{bi(publication_title(paper))}</h4>{alternate}
      <p class="authors">{authors(paper)}</p><p class="journal">{venue(paper)}</p>{online}
      <div class="pub-meta"><span class="role">{bi(ROLES[role])}</span>{status_label}
        {doi_link(paper)}{"".join(resource_links(paper))}</div>
      <details><summary>{bi(("Summary & my contribution", "研究概述与个人贡献"))}</summary>
        {paragraph((paper["summary_en"], paper["summary_zh"]))}
        {definition_list([(("My contribution", "个人贡献"), bi(contribution))])}
        {figure(paper.get("figure"))}
      </details>{citation}</article>'''


def select(field, label, items, selected=""):
    options = []
    for key, name in items:
        is_selected = " selected" if key == selected else ""
        options.append(
            f'<option value="{h(str(key))}" data-en="{h(name[0])}" data-zh="{h(name[1])}"{is_selected}>{h(name[0])}</option>'
        )
    return (
        f'<label for="filter-{field}">{bi(label)}<select id="filter-{field}" name="{field}">'
        f'{"".join(options)}</select></label>'
    )


def filters(statuses):
    years = sorted({p["year"] for p in PAPERS.values()}, reverse=True)
    all_items = [("", ("All", "全部"))]
    statuses = [("", ("All statuses", "全部状态"))] + [(key, STATUS[key]) for key in statuses]
    roles = all_items + [
        ("listed-first", ("First-listed author", "列名第一")),
        ("equal", ("Equal contribution", "共同贡献")),
        ("second", ROLES["second"]),
        ("coauthor", ROLES["coauthor"]),
    ]
    return f'''<form class="filters" id="publication-filters" role="search"
      aria-label="Publication filters" data-label-zh="论文筛选" hidden>
      <label class="search-field" for="filter-query">{bi(("Search publications", "搜索论文"))}
        <input type="search" id="filter-query" name="query"
          data-placeholder-en="Title, author or DOI" data-placeholder-zh="标题、作者或 DOI" placeholder="Title, author or DOI">
      </label>
      {select("year", ("Year", "年份"), all_items + [(year, (str(year), str(year))) for year in years])}
      {select("theme", ("Research theme", "研究方向"), all_items + [(key, theme["name"]) for key, theme in THEMES.items()])}
      {select("status", ("Status", "发表状态"), statuses, "published" if any(key == "published" for key, _ in statuses) else "")}
      {select("role", ("Author role", "作者身份"), roles)}
    </form>'''


def patents():
    cards = []
    for patent in PROFILE["patents"]:
        title = heading(patent["title"], 4)
        grant = external(f'https://patents.google.com/patent/{patent["id"]}/zh', h(patent["id"]))
        application = bi(("Application", "申请号"))
        cards.append(
            f'<article class="card patent">{title}<p>{grant} · {bi(patent["role"])}</p>'
            f'<p class="muted">{application} {h(patent["application"])} · {h(patent["granted"])}</p></article>'
        )
    return (
        heading(("Granted Invention Patents", "授权发明专利"), 3)
        + paragraph(("English patent titles are translations.", "英文专利名称为译名。"), "muted")
        + f'<div class="card-grid">{"".join(cards)}</div>'
    )


def publications_section():
    groups = []
    available_statuses = []
    for status in STATUS_ORDER:
        papers = sorted((p for p in PAPERS.values() if p["status"] == status), key=lambda p: p["year"], reverse=True)
        if not papers:
            continue
        available_statuses.append(status)
        label = ("Published Journal Articles", "已发表期刊论文") if status == "published" else STATUS[status]
        groups.append(
            f'<div class="publication-group" data-publication-group>{heading(label, 3)}'
            f'{"".join(publication(paper) for paper in papers)}</div>'
        )
    return section("publications", ("Publications & Patents", "学术论文与专利"),
        links([local("publications.bib", ("Download all BibTeX ↓", "下载全部 BibTeX ↓"), "button")])
        + paragraph(("† Equal contribution. * Corresponding author.", "† 共同贡献。* 通讯作者。"), "muted")
        + filters(available_statuses)
        + '<p class="muted" id="publication-count" role="status" hidden></p>'
        + f'<p id="publication-empty" hidden>{bi(("No publications match these filters.", "没有符合筛选条件的论文。"))}</p>'
        + "".join(groups) + patents())
