"""Generate a compact English academic CV using public site data."""
from html import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import KeepTogether, PageBreak, Paragraph, SimpleDocTemplate
from site_data import EXPERTISE, PROJECTS, ROLES, STATUS

BLUE = colors.HexColor("#173b60")
MUTED = colors.HexColor("#455c72")

STYLES = {
    "name": ParagraphStyle("Name", fontName="Helvetica-Bold", fontSize=24, leading=28,
                           textColor=BLUE, spaceAfter=8),
    "section": ParagraphStyle("Section", fontName="Helvetica-Bold", fontSize=11, leading=14,
                              textColor=BLUE, spaceBefore=12, spaceAfter=5, keepWithNext=True),
    "text": ParagraphStyle("Text", fontName="Helvetica", fontSize=9.3, leading=12.7, spaceAfter=5),
    "small": ParagraphStyle("Small", fontName="Helvetica", fontSize=8.4, leading=11.4,
                            textColor=MUTED, spaceAfter=5),
}


def public_link(url, label):
    return f'<link href="{escape(url)}" color="#24587d">{escape(label)}</link>'


def build_cv(profile, papers, destination):
    story = []

    def p(text, style="text"):
        return Paragraph(text, STYLES[style])

    def add(text, style="text"):
        story.append(p(text, style))

    def section(title):
        add(escape(title), "section")

    add(escape(profile["name"]), "name")
    add(escape(f'{profile["role"][0]} · {profile["school"][0]}, {profile["university"][0]}'))
    links = [public_link("mailto:" + email, email) for email in profile["emails"]]
    links += [public_link(profile["site"], "Academic homepage"),
              public_link(profile["github"], "GitHub"), public_link(profile["orcid"], "ORCID")]
    add(" · ".join(links), "small")
    section("Research profile")
    add(escape(" ".join(paragraph[0] for paragraph in profile["hero"]["paragraphs"])))
    section("Education and industry experience")
    for item in profile["experience"]:
        details = escape(item["role"][0] + " · " + item["dates"][0])
        subtitle = ""
        if item.get("supervisor"):
            subtitle += " Supervisor: " + public_link(item["url"], item["supervisor"][0]) + "."
        if item["id"] == "wuhan":
            subtitle += " Expected graduation: " + escape(profile["graduation"][0]) + "."
        story.append(KeepTogether([
            p(f'<b>{escape(item["name"][0])}</b> · {details}'),
            p(escape(item["body"][0]) + subtitle, "small"),
        ]))
    section("Selected research")
    for project_id, label in [
        ("deep-laser-emat", "Laser–EMAT imaging of deep defects (ongoing)"),
        ("sparse-wavefields", "Physics-informed wavefield reconstruction"),
        ("am-topography", "Air-coupled 2.5-D topography of rough AM surfaces"),
        ("self-sensing-cleaning", "Process-integrated ultrasonic monitoring"),
    ]:
        project = PROJECTS.get(project_id)
        if not project:
            continue
        add(public_link(profile["site"] + "research.html#" + project_id, label)
            + " · " + escape(project["method"][0]), "small")

    section("Research and engineering skills")
    for title, description in EXPERTISE["expertise"][:3]:
        add(f"<b>{escape(title[0])}.</b> {escape(description[0])}", "small")

    section("Research projects and honours")
    add(escape(" · ".join(item[0] for item in profile["grants"])), "small")
    add(escape(" · ".join(item[0] for item in profile["honours"])), "small")
    add(escape(profile["presentation"][0]), "small")
    add(escape(profile["languages"][0]), "small")

    story.append(PageBreak())
    add("Selected academic record", "name")
    papers = [paper for paper in papers if paper["status"] in ("published", "accepted", "preprint")]
    published = [paper for paper in papers if paper["status"] == "published"]
    first = sum(paper["authors"][0] in (profile["name"], profile["chinese_name"]) for paper in published)
    section(f"Journal publications · {len(published)} published · {first} first-listed")
    for paper in papers:
        title = paper["translated_title"] + " [in Chinese]" if paper.get("in_chinese") else paper["title"]
        journal = paper.get("journal_en", paper["journal"])
        citation = f'<i>{escape(journal)}</i>'
        if paper.get("volume"):
            citation += " " + escape(paper["volume"])
        if paper.get("issue"):
            citation += f'({escape(paper["issue"])})'
        locator = paper.get("article_number") or paper.get("pages")
        if locator:
            citation += ", " + escape(locator)
        citation += f' ({paper["year"]})'
        if paper.get("online_year"):
            citation += f', first published online {paper["online_year"]}'
        if paper["status"] != "published":
            citation += " · " + STATUS[paper["status"]][0]
        citation += " · " + ROLES[paper["role"]][0]
        if paper.get("doi"):
            citation += " · " + public_link("https://doi.org/" + paper["doi"], paper["doi"])
        authors = paper.get("authors_latin", []) if paper.get("in_chinese") else paper["authors"]
        names = escape(", ".join(authors))
        author_line = f"{names}<br/>" if names else ""
        story.append(KeepTogether([
            p(f"<b>{escape(title)}</b>"),
            p(f"{author_line}{citation}", "small"),
        ]))
    section("Granted invention patents (translated titles)")
    for item in profile["patents"]:
        grant = public_link("https://patents.google.com/patent/" + item["id"] + "/zh", item["id"])
        add(f'{grant} · {escape(item["title"][0])} · {escape(item["role"][0])}.', "small")

    def footer(pdf, document):
        pdf.setStrokeColor(colors.HexColor("#ced8e4"))
        pdf.line(40, 32, A4[0] - 40, 32)
        pdf.setFont("Helvetica", 8)
        pdf.setFillColor(MUTED)
        pdf.drawString(40, 20, f'{profile["name"]} | Academic CV | {profile["cv"]["updated"]}')
        pdf.drawRightString(A4[0] - 40, 20, str(document.page))

    def reproducible_canvas(*args, **kwargs):
        kwargs["invariant"] = True
        return canvas.Canvas(*args, **kwargs)

    doc = SimpleDocTemplate(
        str(destination), pagesize=A4, leftMargin=40, rightMargin=40, topMargin=34,
        bottomMargin=43, title=f'{profile["name"]} - Academic CV', author=profile["name"],
    )
    doc.build(story, onFirstPage=footer, onLaterPages=footer, canvasmaker=reproducible_canvas)
