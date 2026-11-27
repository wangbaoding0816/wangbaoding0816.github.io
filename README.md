# Baoding Wang · 王宝定

[Academic homepage](https://wangbaoding0816.github.io/) for research in Laser–EMAT, experimental instrumentation, non-contact ultrasonic inspection and physics-informed imaging.

## 本地预览

网页在 GitHub Pages 上以静态文件运行。只有在更新数据或重新生成公开英文 CV 时才需要 Python。

```powershell
python -m pip install -r requirements.txt
python scripts/build_academic.py
python scripts/verify_site.py
python -m http.server 8765 --bind 127.0.0.1
```

打开 [本地首页](http://127.0.0.1:8765/) 或 [本地研究档案](http://127.0.0.1:8765/research.html)。如已生成网页，可直接从启动本地服务器开始。用 `Ctrl+C` 结束预览。

## 内容维护

| 内容 | 修改位置 | 更新方式 |
| --- | --- | --- |
| 个人资料、教育和工业经历、联系方式、荣誉、科研项目、专利 | `data/profile.json` | 更新对应字段。中英文字段采用 `["English", "中文"]`。专利填写申请号、授权号、发明人排序和日期。 |
| 论文、作者、DOI、代码、数据、图片、状态 | `data/publications.json` | 新增唯一 `id`，填写原始标题、中文标题、完整作者顺序、期刊和年份。用 `equal_authors` 和 `corresponding_authors` 记录已核实的作者标注。文章编号填 `article_number`，页码填 `pages`。中文论文可填 `translated_title`、`authors_latin` 和 `journal_en` 供英文 CV 使用。 |
| 论文状态与公开范围 | `data/publications.json` | 支持 `published`、`accepted`、`submitted`、`revision` 和 `preprint`。在投和返修条目要求明确设置 `"public": true`。发布许可确认后再把稿件资料加入仓库。`"public": false` 只隐藏生成页面上的条目。 |
| 研究主线、科研档案和图片 | `data/research.json` | 在 `themes`、`projects` 或 `extensions` 新增中英文条目，以论文和系统 ID 关联。已发送的链接形如 `research.html#deep-laser-emat`，更新内容时保留原 ID。首页展示 `projects` 顺序中的前五项。 |
| 实验系统和仪器 | `data/systems.json` | 新增唯一 `id`、配置、贡献、测控、能力、结果和关联论文。系统状态可填 `independent`、`collaborative`、`hands-on` 或 `development`。 |
| 科研能力及流程图 | `data/expertise.json` | 更新 `expertise` 与 `workflow` 的双语文字和顺序。 |
| 开源软件和数据 | `data/resources.json` | 填写关联论文与研究 ID、仓库分支、双语说明和许可证。仓库与数据地址来自对应论文条目。 |
| CV、统计、CSC 模块 | `data/profile.json` | 更改 `cv.updated` 可更新 CV 日期。站点统计由已发表论文、作者顺序、专利与已配置开源资源计算。通过 `csc.enabled` 开启或关闭访问研究介绍。 |
| 页面文案与样式 | `scripts/`、`assets/academic.css`、`assets/academic.js` | 固定标签随渲染器维护。更新内容后运行构建和验证。 |

论文、研究主线、项目、在研子项目、系统和软件条目均支持 `"public": false`。该字段控制网页呈现，GitHub 仓库及静态站根目录仍可访问已提交的源文件。

更新论文时以期刊的作者顺序、共同贡献脚注和正式出版信息为准。书目和站内论文详情会从统一数据生成。首位作者有共同贡献标记时填写 `role: "cofirst"`，并列出 `equal_authors`。列名第二的共同贡献作者可用 `role: "equal"`。

### 替换图片或增加视频

把有公开许可的清晰原图放入 `assets/images/<研究方向>/`。在 `research.json` 的 `figures` 写入路径、双语 `alt` 和 `caption`，并在确认公开许可后设为 `"public": true`。把图的 ID 赋给项目的 `figure`，或加入系统的 `figures`。系统封面使用 `cover`。缺少文件时，构建会呈现可用的文字和论文链接。图中轴名、单位和颜色条应完整保留。

实验或研究条目支持可选 `videos` 列表。每项填写 `"public": true`、`path`、双语 `caption`，可加 `poster`，以及带有 `path`、`lang` 和 `label` 的 `captions`。视频和 WebVTT 字幕可放在 `assets/videos/`。

### 更新英文 CV

默认由 `scripts/public_cv.py` 从公开数据生成 `Baoding_Wang_Academic_CV.pdf`，并更新旧下载路径 `Baoding_Wang_CV.pdf`。若已有可公开的新版英文 PDF，把它放在根目录，设置 `cv.file`、`cv.updated` 和 `"generate": false` 后重新构建。清空 `cv.file` 时，页面显示待补充文字。仓库根目录的文件随 GitHub Pages 静态站一起提供，因此应将内部简历和未公开材料留在仓库之外。

## GitHub Pages 发布

当前站点使用 GitHub Pages 的 **Settings → Pages → Deploy from a branch**，发布分支为 `main`，目录为 `/ (root)`。`.nojekyll` 让 Pages 直接使用静态输出。发布前本地运行构建和验证。获准发布后，将审核过的分支合入配置的发布分支并推送，再检查首页、研究直达地址及两个 CV 下载路径。原页面的 `#about`、`#research`、`#publications` 和 `#paper-…` 等锚点仍可使用。
