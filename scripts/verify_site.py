"""Check the built site's anchors, downloadable files and shared data without network access."""
from collections import Counter
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree

from PIL import Image
from site_data import (
    CV,
    CV_ZH,
    PAPERS,
    PREVIEW,
    PROFILE,
    PROJECTS,
    RESEARCH,
    ROOT,
    SITE,
    SYSTEMS,
    THEMES,
)


class Page(HTMLParser):
    def __init__(self, name):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.targets = set()
        self.images = []
        self.papers = {}
        self.headings = []
        self.read(name)

    def read(self, name):
        self.feed((ROOT / name).read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag in ("a", "link") and attrs.get("href"):
            self.targets.add(attrs["href"])
        if tag in ("img", "script", "video", "track") and attrs.get("src"):
            self.targets.add(attrs["src"])
        if tag == "img" and attrs.get("src"):
            self.images.append(attrs)
        if tag == "article" and "data-doi" in attrs:
            self.papers[attrs["id"]] = attrs
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.headings.append(int(tag[1]))


def validate():
    pages = {name: Page(name) for name in ("index.html", "research.html")}
    home = pages["index.html"]
    research = pages["research.html"]
    assert {
        "about", "research", "experimental-systems", "selected-research", "software-data",
        "capabilities", "experience", "publications", "publication-filters", "contact", "cv",
        "honors",
    }.issubset(home.ids)
    featured = list(PROJECTS)[:5]
    if "mode-conversion" in PROJECTS:
        assert "ongoing" in home.ids and "research.html#mode-conversion" in home.targets
    if "am-topography" in featured:
        assert "featured-tim-title" in home.ids
    assert {f"system-{key}" for key in SYSTEMS}.issubset(home.ids)
    assert {f"theme-{key}" for key in THEMES}.issubset(home.ids)
    assert set(PROJECTS).issubset(research.ids)
    assert all(extra["id"] in research.ids for extra in RESEARCH["extensions"]
               if extra.get("public", True) and extra["parent"] in PROJECTS)
    assert set(home.papers) == {f"paper-{key}" for key in PAPERS}
    assert len({p["doi"].lower() for p in PAPERS.values() if p.get("doi")}) == sum(
        bool(p.get("doi")) for p in PAPERS.values()
    )
    for key, paper in PAPERS.items():
        rendered = home.papers[f"paper-{key}"]
        assert rendered["data-status"] == paper["status"]
        assert rendered["data-doi"] == (paper.get("doi") or "")
        assert set(paper["themes"]).issubset(THEMES)
        for field in ("equal_authors", "corresponding_authors"):
            assert set(paper.get(field) or []).issubset(paper["authors"])
    images = set()
    checked_links = set()
    for name, page in pages.items():
        duplicate_ids = [key for key, occurrences in Counter(page.ids).items() if occurrences > 1]
        assert not duplicate_ids, (name, duplicate_ids)
        assert page.headings.count(1) == 1, (name, page.headings)
        assert all(nxt <= cur + 1 for cur, nxt in zip(page.headings, page.headings[1:])), (name, page.headings)
        for url in page.targets:
            target = urlsplit(url)
            if target.scheme or target.netloc:
                continue
            filename = unquote(target.path) or name
            assert (ROOT / filename).is_file(), (name, url)
            if target.fragment and filename in pages:
                assert unquote(target.fragment) in pages[filename].ids, (name, url)
            checked_links.add((name, url))
        for image in page.images:
            assert image.get("alt") and image.get("data-alt-zh"), (name, image)
            assert int(image["width"]) > 0 and int(image["height"]) > 0, (name, image)
            if "portrait" not in image.get("class", ""):
                assert image.get("loading") == "lazy", (name, image["src"])
            images.add(image["src"])
    for filename in images | {PREVIEW}:
        with Image.open(ROOT / filename) as image:
            image.verify()
    for cv_file in filter(None, (CV, CV_ZH)):
        assert cv_file in home.targets
        assert (ROOT / cv_file).read_bytes().startswith(b"%PDF-")
    if CV:
        pdf = (ROOT / CV).read_bytes()
        assert pdf.startswith(b"%PDF-") and pdf == (ROOT / "Baoding_Wang_CV.pdf").read_bytes()
    bibliography = (ROOT / "publications.bib").read_text(encoding="utf-8")
    assert bibliography.count("@article{") == len(PAPERS)
    assert all(p["doi"] in bibliography for p in PAPERS.values() if p.get("doi"))
    assert all(f'pages = {{{p["article_number"]}}}' in bibliography
               for p in PAPERS.values() if p.get("article_number") and not p.get("pages"))
    assert (ROOT / ".nojekyll").is_file()
    assert f"Sitemap: {SITE}sitemap.xml" in (ROOT / "robots.txt").read_text(encoding="utf-8")
    sitemap = ElementTree.parse(ROOT / "sitemap.xml")
    assert {node.text for node in sitemap.findall(".//{*}loc")} == {SITE, SITE + "research.html"}
    assert isinstance(PROFILE["csc"]["enabled"], bool)
    print(f"Validated {len(pages)} pages, {len(checked_links)} local link targets, "
          f"{len(images)} image files, {len(PAPERS)} articles and {len(PROJECTS)} project anchors.")


if __name__ == "__main__":
    validate()
