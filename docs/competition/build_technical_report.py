from __future__ import annotations

import re
from pathlib import Path

from PIL import Image
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_ALIGN_VERTICAL, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs" / "competition" / "无界手语-SignFlow-AI-赛题三参赛报告-2026-07-30.md"
OUTPUT = ROOT / "docs" / "competition" / "无界手语-SignFlow-AI-赛题三参赛报告-2026-07-30.docx"
ASSETS = ROOT / "docs" / "competition" / "report-assets-2026-07-30"
NORMALIZED_ASSETS = (
    ROOT / "docs" / "competition" / ".qa-2026-07-30" / "normalized-assets"
)

BRAND = "5B5BD6"
BRAND_DARK = "3636A8"
BLUE = "2E74B5"
NAVY = "14213D"
TEXT = "25324B"
MUTED = "667085"
PALE = "F2F3FF"
PALE_BLUE = "F4F7FB"
LINE = "D9DEEA"
WHITE = "FFFFFF"
SUCCESS = "0B7A53"
CONTENT_WIDTH_DXA = 9360

INTERFACE_FIGURES = {
    "4.2.1 产品首页": (
        (
            "01-home.png",
            "SignFlow AI 产品首页",
            "公共产品首页展示品牌定位、产品能力、应用场景、技术安全和真实导航入口。",
            "界面 4-1  产品首页：从无障碍价值进入产品能力与真实体验",
        ),
    ),
    "4.2.2 产品导览": (
        (
            "02-product-tour.png",
            "SignFlow AI 产品导览",
            "公开产品导览展示官方样例、场景化识别、双模型切换和完整沟通流程。",
            "界面 4-2  产品导览：无需账号体验多模态识别流程",
        ),
    ),
    "4.2.3 公开样例结果": (
        (
            "24-public-result-detail.png",
            "公开样例结果详情",
            "公开结果页展示演示数据标记、授权媒体、识别文字、边界框和标签时间线。",
            "界面 4-3  公开样例结果：演示数据、媒体与标签口径明确分离",
        ),
    ),
    "4.2.4 登录": (
        (
            "14-login.png",
            "SignFlow AI 网页端登录",
            "网页端登录包含账号、遮蔽密码、记住账号、注册、产品导览、隐私和服务状态入口。",
            "界面 4-4  登录：统一账户入口与安全会话说明",
        ),
    ),
    "4.2.5 注册": (
        (
            "15-register.png",
            "SignFlow AI 网页端注册",
            "注册页展示账号、邮箱、强密码、确认密码、隐私同意和返回登录入口。",
            "界面 4-5  注册：创建网页与手机端共享的统一账户",
        ),
    ),
    "4.2.6 隐私与数据保留": (
        (
            "03-privacy.png",
            "隐私与数据保留页面",
            "隐私页面公开说明数据处理目的、保留期限、训练边界、访问控制、导出与删除。",
            "界面 4-6  隐私与数据保留：把产品承诺变成可直接访问的政策页面",
        ),
    ),
    "4.2.7 页面未找到": (
        (
            "16-not-found.png",
            "SignFlow AI 页面未找到",
            "统一 404 页面提供品牌化错误说明和返回首页操作，不泄露调试信息。",
            "界面 4-7  页面未找到：错误路由仍有明确恢复路径",
        ),
    ),
    "4.3.1 运行概览": (
        (
            "04-overview.png",
            "SignFlow AI 运行概览",
            "概览展示今日任务、成功率、平均耗时、待确认数、趋势和服务在线状态。",
            "界面 4-8  运行概览：真实任务统计、趋势与快捷入口",
        ),
    ),
    "4.3.2 识别工作台": (
        (
            "22-workbench-video.png",
            "SignFlow AI 视频识别工作台",
            "工作台视频模式展示场景策略、CSL/ASL 模型、上传入口、样例、媒体预览和关键帧。",
            "界面 4-9  识别工作台：视频输入、模型选择与媒体预览",
        ),
    ),
    "4.3.3 结果中心": (
        (
            "08-results.png",
            "SignFlow AI 结果中心",
            "结果中心展示真实任务列表、输入类型、状态、模型、时间、置信度和筛选入口。",
            "界面 4-10  结果中心：跨图片、视频和实时任务的统一历史",
        ),
    ),
    "4.3.4 结果详情与证据追溯": (
        (
            "09-traceability-result.png",
            "识别结果详情",
            "结果详情显示授权原始媒体、识别文本、标签、模型版本、任务元数据和确认状态。",
            "界面 4-11  结果详情：原始媒体、标签与任务元数据共同呈现",
        ),
    ),
    "4.3.5 数据洞察": (
        (
            "07-analytics.png",
            "SignFlow AI 数据洞察",
            "数据洞察展示任务量、成功率、耗时、输入分布和模型使用趋势图。",
            "界面 4-12  数据洞察：真实统计口径与三张 ECharts 图表",
        ),
    ),
    "4.3.6 模型中心": (
        (
            "05-model-evaluation.png",
            "SignFlow AI 模型中心",
            "模型中心展示 CSL 和 ASL 的语言、类别、版本、状态、评测摘要与能力边界。",
            "界面 4-13  模型中心：双模型目录与可核验评测卡",
        ),
    ),
    "4.3.7 账户与设置": (
        (
            "17-settings.png",
            "SignFlow AI 账户与设置",
            "设置页面展示账户资料、会话安全、识别数据保留、密码权限和管理后台入口。",
            "界面 4-14  账户与设置：安全会话、数据保留与团队入口",
        ),
    ),
    "4.4.3 系统运行": (
        (
            "20-admin-system.png",
            "SignFlow AI 系统运行",
            "系统运行页面展示依赖就绪状态、API 环境、保留策略及账户、角色、模型数量。",
            "界面 4-17  系统运行：现场演示前的依赖与数据就绪检查",
        ),
    ),
    "4.5.1 手机端登录": (
        (
            "12-mobile-login-accessibility.png",
            "SignFlow AI 手机端登录",
            "390 像素宽手机端登录展示语义化输入、46 像素操作按钮和服务地址设置入口。",
            "界面 4-18  手机端登录：触控友好、可配置服务与密码不落盘",
        ),
    ),
    "4.5.2 手机端注册": (
        (
            "25-mobile-register.png",
            "SignFlow AI 手机端注册",
            "手机端注册展示账号、可选邮箱、十二位以上密码、确认密码和返回操作。",
            "界面 4-19  手机端注册：与网页端共享账户和结果",
        ),
    ),
    "4.5.5 手机端结果中心": (
        (
            "28-mobile-results-viewport.png",
            "SignFlow AI 手机端结果中心",
            "手机端结果中心以卡片展示输入类型、识别文字、模型版本、时间和任务置信度。",
            "界面 4-20  手机端结果中心：跨终端同步的任务卡片",
        ),
    ),
}


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_width(cell, width_dxa: int) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_w = tc_pr.find(qn("w:tcW"))
    if tc_w is None:
        tc_w = OxmlElement("w:tcW")
        tc_pr.append(tc_w)
    tc_w.set(qn("w:type"), "dxa")
    tc_w.set(qn("w:w"), str(width_dxa))


def set_cell_margins(cell, top=80, start=120, bottom=80, end=120) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for margin, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{margin}"))
        if node is None:
            node = OxmlElement(f"w:{margin}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_table_width(table, widths: list[int]) -> None:
    table.autofit = False
    tbl_pr = table._tbl.tblPr
    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:type"), "dxa")
    tbl_w.set(qn("w:w"), str(sum(widths)))
    tbl_ind = tbl_pr.find(qn("w:tblInd"))
    if tbl_ind is None:
        tbl_ind = OxmlElement("w:tblInd")
        tbl_pr.append(tbl_ind)
    tbl_ind.set(qn("w:type"), "dxa")
    tbl_ind.set(qn("w:w"), "120")
    grid_columns = table._tbl.tblGrid.gridCol_lst
    for index, width in enumerate(widths):
        if index < len(grid_columns):
            grid_columns[index].set(qn("w:w"), str(width))
    for row in table.rows:
        tr_pr = row._tr.get_or_add_trPr()
        if tr_pr.find(qn("w:cantSplit")) is None:
            tr_pr.append(OxmlElement("w:cantSplit"))
        for index, width in enumerate(widths):
            if index < len(row.cells):
                set_cell_width(row.cells[index], width)
                row.cells[index].width = Inches(width / 1440)
                set_cell_margins(row.cells[index])


def set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def set_table_borders(table, color=LINE, size=4) -> None:
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.first_child_found_in("w:tblBorders")
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = borders.find(qn(f"w:{edge}"))
        if tag is None:
            tag = OxmlElement(f"w:{edge}")
            borders.append(tag)
        tag.set(qn("w:val"), "single")
        tag.set(qn("w:sz"), str(size))
        tag.set(qn("w:space"), "0")
        tag.set(qn("w:color"), color)


def set_font(run, name="Calibri", east_asia="Microsoft YaHei", size=None, color=None, bold=None):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), east_asia)
    if size is not None:
        run.font.size = Pt(size)
    if color is not None:
        run.font.color.rgb = RGBColor.from_string(color)
    if bold is not None:
        run.bold = bold


def add_page_number(paragraph) -> None:
    paragraph.add_run("第 ")
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "1"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instr, separate, text, end])
    paragraph.add_run(" 页")


def add_hyperlink(paragraph, text: str, url: str, color=BRAND) -> None:
    part = paragraph.part
    relationship_id = part.relate_to(
        url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True,
    )
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), relationship_id)
    run = OxmlElement("w:r")
    r_pr = OxmlElement("w:rPr")
    run.append(r_pr)
    color_node = OxmlElement("w:color")
    color_node.set(qn("w:val"), color)
    r_pr.append(color_node)
    underline = OxmlElement("w:u")
    underline.set(qn("w:val"), "single")
    r_pr.append(underline)
    fonts = OxmlElement("w:rFonts")
    fonts.set(qn("w:ascii"), "Calibri")
    fonts.set(qn("w:hAnsi"), "Calibri")
    fonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    r_pr.append(fonts)
    text_node = OxmlElement("w:t")
    text_node.text = text
    run.append(text_node)
    hyperlink.append(run)
    paragraph._p.append(hyperlink)


def add_inline_runs(paragraph, text: str) -> None:
    pattern = re.compile(r"(\*\*.+?\*\*|`.+?`|https?://[^\s`]+)")
    position = 0
    for match in pattern.finditer(text):
        if match.start() > position:
            set_font(paragraph.add_run(text[position : match.start()]), color=TEXT)
        token = match.group(0)
        if token.startswith("**"):
            run = paragraph.add_run(token[2:-2])
            set_font(run, color=NAVY, bold=True)
        elif token.startswith("`"):
            run = paragraph.add_run(token[1:-1])
            set_font(run, name="Consolas", east_asia="Microsoft YaHei", size=9.5, color=BRAND_DARK)
            run._element.get_or_add_rPr().append(_run_shading(PALE))
        else:
            add_hyperlink(paragraph, token, token)
        position = match.end()
    if position < len(text):
        set_font(paragraph.add_run(text[position:]), color=TEXT)


def _run_shading(fill: str):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    return shd


def set_alt_text(inline_shape, title: str, description: str) -> None:
    doc_pr = inline_shape._inline.docPr
    doc_pr.set("title", title)
    doc_pr.set("descr", description)


def normalized_jpeg(image_path: Path) -> Path:
    NORMALIZED_ASSETS.mkdir(parents=True, exist_ok=True)
    output_path = NORMALIZED_ASSETS / f"{image_path.stem}.jpg"
    with Image.open(image_path) as image:
        image.convert("RGB").save(output_path, format="JPEG", quality=92, optimize=True)
    return output_path


def add_picture(
    document,
    image_path: Path,
    title: str,
    description: str,
    caption: str,
    max_height: float = 4.85,
) -> None:
    normalized_path = normalized_jpeg(image_path)
    with Image.open(normalized_path) as image:
        width, height = image.size
    max_width = 6.5
    scale = min(max_width / width, max_height / height)
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_before = Pt(8)
    paragraph.paragraph_format.space_after = Pt(4)
    paragraph.paragraph_format.keep_with_next = True
    shape = paragraph.add_run().add_picture(
        str(normalized_path),
        width=Inches(width * scale),
        height=Inches(height * scale),
    )
    set_alt_text(shape, title, description)
    caption_paragraph = document.add_paragraph(style="Caption")
    caption_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption_paragraph.paragraph_format.keep_with_next = False
    set_font(caption_paragraph.add_run(caption), size=9, color=MUTED)


def style_document(document: Document) -> None:
    section = document.sections[0]
    configure_section(section, different_first_page=True)

    styles = document.styles
    normal = styles["Normal"]
    normal.font.name = "Calibri"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    normal.font.size = Pt(11)
    normal.font.color.rgb = RGBColor.from_string(TEXT)
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(8)
    normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    normal.paragraph_format.line_spacing = 1.333

    for name, size, color, before, after in (
        ("Heading 1", 16, BLUE, 18, 10),
        ("Heading 2", 13, BLUE, 12, 6),
        ("Heading 3", 12, "1F4D78", 8, 4),
    ):
        style = styles[name]
        style.font.name = "Calibri"
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(color)
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.keep_with_next = True

    for name in ("List Bullet", "List Number"):
        style = styles[name]
        style.font.name = "Calibri"
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
        style.font.size = Pt(10.5)
        style.paragraph_format.left_indent = Inches(0.375)
        style.paragraph_format.first_line_indent = Inches(-0.194)
        style.paragraph_format.space_after = Pt(4)
        style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
        style.paragraph_format.line_spacing = 1.208

    caption = styles["Caption"]
    caption.font.name = "Calibri"
    caption._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    caption.font.size = Pt(9)
    caption.font.italic = False
    caption.font.color.rgb = RGBColor.from_string(MUTED)

    for name, base, size, color, bold in (
        ("Kicker", "Normal", 9, BRAND, True),
        ("Cover Title", "Normal", 28, NAVY, True),
        ("Cover Subtitle", "Normal", 17, BRAND_DARK, True),
        ("Lead", "Normal", 12, TEXT, False),
        ("Callout", "Normal", 10.5, NAVY, False),
        ("Code Block", "Normal", 8.5, "344054", False),
    ):
        if name not in styles:
            style = styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        else:
            style = styles[name]
        style.base_style = styles[base]
        style.font.name = "Consolas" if name == "Code Block" else "Calibri"
        style._element.rPr.rFonts.set(
            qn("w:eastAsia"), "Microsoft YaHei" if name != "Code Block" else "Microsoft YaHei"
        )
        style.font.size = Pt(size)
        style.font.color.rgb = RGBColor.from_string(color)
        style.font.bold = bold

    styles["Kicker"].paragraph_format.space_after = Pt(12)
    styles["Cover Title"].paragraph_format.space_after = Pt(6)
    styles["Cover Title"].paragraph_format.line_spacing = 1.0
    styles["Cover Subtitle"].paragraph_format.space_after = Pt(14)
    styles["Lead"].paragraph_format.space_after = Pt(12)
    styles["Lead"].paragraph_format.line_spacing = 1.35
    styles["Callout"].paragraph_format.left_indent = Inches(0.2)
    styles["Callout"].paragraph_format.right_indent = Inches(0.2)
    styles["Callout"].paragraph_format.space_before = Pt(6)
    styles["Callout"].paragraph_format.space_after = Pt(8)
    styles["Code Block"].paragraph_format.left_indent = Inches(0.15)
    styles["Code Block"].paragraph_format.right_indent = Inches(0.15)
    styles["Code Block"].paragraph_format.space_before = Pt(4)
    styles["Code Block"].paragraph_format.space_after = Pt(6)
    styles["Code Block"].paragraph_format.line_spacing = 1.0


def configure_section(section, different_first_page=False) -> None:
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    section.header_distance = Inches(0.492)
    section.footer_distance = Inches(0.492)
    section.different_first_page_header_footer = different_first_page


def add_header_footer(document: Document) -> None:
    section = document.sections[0]
    header = section.header
    paragraph = header.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    set_font(paragraph.add_run("无界手语 SignFlow AI  ·  赛题三参赛报告"), size=8.5, color=MUTED)
    footer = section.footer
    footer_paragraph = footer.paragraphs[0]
    footer_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer_paragraph.paragraph_format.space_before = Pt(2)
    set_font(footer_paragraph.add_run("AI+无障碍公共服务平台  ·  "), size=8, color=MUTED)
    add_page_number(footer_paragraph)
    for run in footer_paragraph.runs:
        set_font(run, size=8, color=MUTED)


def add_cover(document: Document) -> None:
    kicker = document.add_paragraph(style="Kicker")
    kicker.alignment = WD_ALIGN_PARAGRAPH.LEFT
    kicker.add_run("COMPETITION TECHNICAL REPORT  ·  2026")

    title = document.add_paragraph(style="Cover Title")
    title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    title.add_run("无界手语\nSignFlow AI")

    subtitle = document.add_paragraph(style="Cover Subtitle")
    subtitle.add_run("AI+无障碍公共服务平台")

    badge = document.add_table(rows=1, cols=1)
    badge.alignment = WD_ALIGN_PARAGRAPH.LEFT
    set_table_width(badge, [CONTENT_WIDTH_DXA])
    set_repeat_table_header(badge.rows[0])
    set_table_borders(badge, color=BRAND, size=6)
    cell = badge.cell(0, 0)
    set_cell_shading(cell, PALE)
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    paragraph = cell.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    paragraph.paragraph_format.space_after = Pt(0)
    set_font(
        paragraph.add_run("参赛方向  /  赛题三 · 面向科学、工程和社会科学的“AI+X”应用"),
        size=10.5,
        color=BRAND_DARK,
        bold=True,
    )

    lead = document.add_paragraph(style="Lead")
    lead.paragraph_format.space_before = Pt(12)
    lead.add_run(
        "把手语视觉识别连接到政务服务、医疗导诊与特殊教育沟通流程，"
        "形成从感知、理解到朗读、复制和协助的可运行产品闭环。"
    )

    image_path = normalized_jpeg(ASSETS / "01-home.png")
    with Image.open(image_path) as image:
        width, height = image.size
    shape = document.add_paragraph().add_run().add_picture(
        str(image_path),
        width=Inches(6.5),
        height=Inches(6.5 * height / width),
    )
    set_alt_text(
        shape,
        "无界手语产品首页",
        "商业化产品首页，展示无障碍公共服务价值、手语样例与真实评测入口。",
    )

    metadata = document.add_paragraph()
    metadata.paragraph_format.space_before = Pt(8)
    metadata.alignment = WD_ALIGN_PARAGRAPH.LEFT
    set_font(metadata.add_run("交叉领域  "), size=9, color=MUTED, bold=True)
    set_font(metadata.add_run("人工智能 × 无障碍公共服务 × 社会包容\n"), size=9, color=TEXT)
    set_font(metadata.add_run("版本日期  "), size=9, color=MUTED, bold=True)
    set_font(metadata.add_run("Submission 3.0 · 完整系统介绍版 · 2026-07-30"), size=9, color=TEXT)
    document.add_page_break()


def add_executive_spread(document: Document) -> None:
    document.add_heading("执行摘要", level=1)
    paragraph = document.add_paragraph(style="Lead")
    paragraph.add_run(
        "无界手语将现有 CSL/ASL 本地视觉模型连接到政务、医疗导诊和特殊教育工作流，"
        "形成可上传、可推理、可朗读、可复制、可确认、可追溯的无障碍沟通产品。"
        "本次没有训练或改写模型权重，所有数据来自真实评测和完整工程验收。"
    )

    table = document.add_table(rows=1, cols=3)
    table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    widths = [3120, 3120, 3120]
    set_table_width(table, widths)
    set_repeat_table_header(table.rows[0])
    set_table_borders(table, color=WHITE, size=0)
    cards = (
        ("3", "输入方式", "图片 · 视频 · 摄像头"),
        ("2", "手语类型", "中国手语 CSL · 美国手语 ASL"),
        ("3", "服务场景", "政务 · 医疗 · 特殊教育"),
    )
    for index, (number, label, note) in enumerate(cards):
        cell = table.cell(0, index)
        set_cell_shading(cell, PALE if index != 1 else PALE_BLUE)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        paragraph = cell.paragraphs[0]
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.paragraph_format.space_after = Pt(0)
        set_font(paragraph.add_run(f"{number}\n"), size=20, color=BRAND_DARK, bold=True)
        set_font(paragraph.add_run(f"{label}\n"), size=10.5, color=NAVY, bold=True)
        set_font(paragraph.add_run(note), size=8.5, color=MUTED)

    callout_table = document.add_table(rows=1, cols=1)
    callout_table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_table_width(callout_table, [CONTENT_WIDTH_DXA])
    set_repeat_table_header(callout_table.rows[0])
    set_table_borders(callout_table, color=BRAND, size=6)
    cell = callout_table.cell(0, 0)
    set_cell_shading(cell, PALE)
    paragraph = cell.paragraphs[0]
    paragraph.style = "Callout"
    paragraph.paragraph_format.space_after = Pt(0)
    set_font(paragraph.add_run("评委可验证："), size=10.5, color=BRAND_DARK, bold=True)
    set_font(
        paragraph.add_run(
            " 当前版本已完成 42 项网页端测试、11 项手机端测试和 70 项后端测试；"
            "网页与手机端生产依赖审计均为 0 个已知漏洞。真实上传 CSL 图片后返回 92.6% 单次置信度，"
            "该数值只作为链路证据，不包装为总体准确率。"
        ),
        size=10.5,
        color=NAVY,
    )

    document.add_heading("产品证据一览", level=2)
    evidence = document.add_table(rows=1, cols=2)
    set_table_width(evidence, [2940, 6420])
    set_repeat_table_header(evidence.rows[0])
    set_table_borders(evidence)
    evidence.rows[0].cells[0].text = "证据类型"
    evidence.rows[0].cells[1].text = "可核验内容"
    for cell in evidence.rows[0].cells:
        set_cell_shading(cell, "E9ECF5")
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                set_font(run, size=9.5, color=NAVY, bold=True)
    for label, value in (
        ("产品", "24 个公共、Web、管理与手机端页面；三类输入与完整沟通闭环"),
        ("算法", "本地 Ultralytics YOLO 权重；CSL/ASL 双模型切换"),
        ("工程", "Vue 3 + uni-app + Django REST Framework + Channels；生产构建与自动化测试"),
        ("责任", "真实评测口径、双方确认、原始媒体与 SHA-256 追溯、医疗辅助边界"),
    ):
        cells = evidence.add_row().cells
        cells[0].text = label
        cells[1].text = value
        for cell in cells:
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_after = Pt(0)
                for run in paragraph.runs:
                    set_font(run, size=9.5, color=TEXT)
    set_table_width(evidence, [2940, 6420])
    document.add_page_break()


def add_markdown_table(document: Document, rows: list[list[str]]) -> None:
    column_count = max(len(row) for row in rows)
    table = document.add_table(rows=1, cols=column_count)
    table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    weights = []
    for column in range(column_count):
        max_length = max(len(row[column]) if column < len(row) else 0 for row in rows)
        weights.append(max(10, min(max_length, 42)))
    total_weight = sum(weights)
    widths = [round(CONTENT_WIDTH_DXA * weight / total_weight) for weight in weights]
    widths[-1] += CONTENT_WIDTH_DXA - sum(widths)
    set_table_width(table, widths)
    set_table_borders(table)
    set_repeat_table_header(table.rows[0])
    for column, text in enumerate(rows[0]):
        cell = table.rows[0].cells[column]
        set_cell_shading(cell, "E9ECF5")
        paragraph = cell.paragraphs[0]
        paragraph.paragraph_format.space_after = Pt(0)
        add_inline_runs(paragraph, text)
        for run in paragraph.runs:
            set_font(run, size=9, color=NAVY, bold=True)
    for row_index, data in enumerate(rows[1:]):
        cells = table.add_row().cells
        for column in range(column_count):
            text = data[column] if column < len(data) else ""
            cell = cells[column]
            if row_index % 2 == 1:
                set_cell_shading(cell, "FAFBFC")
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            paragraph = cell.paragraphs[0]
            paragraph.paragraph_format.space_after = Pt(0)
            add_inline_runs(paragraph, text)
            for run in paragraph.runs:
                if run.font.size is None or run.font.size.pt > 9:
                    run.font.size = Pt(9)
    set_table_width(table, widths)
    document.add_paragraph().paragraph_format.space_after = Pt(0)


def add_code_block(document: Document, lines: list[str]) -> None:
    if any("→" in line for line in lines):
        table = document.add_table(rows=1, cols=1)
        set_table_width(table, [CONTENT_WIDTH_DXA])
        set_repeat_table_header(table.rows[0])
        set_table_borders(table, color=BRAND, size=6)
        cell = table.cell(0, 0)
        set_cell_shading(cell, PALE_BLUE)
        paragraph = cell.paragraphs[0]
        paragraph.style = "Code Block"
        paragraph.paragraph_format.space_after = Pt(0)
        for index, line in enumerate(lines):
            if index:
                paragraph.add_run().add_break()
            set_font(
                paragraph.add_run(line),
                name="Consolas",
                east_asia="Microsoft YaHei",
                size=9.5,
                color=BRAND_DARK,
                bold=index == 0,
            )
        return

    table = document.add_table(rows=1, cols=3)
    widths = [1700, 4700, 2960]
    set_table_width(table, widths)
    set_table_borders(table)
    for cell, text in zip(table.rows[0].cells, ("架构层", "核心组件", "作用")):
        set_cell_shading(cell, "E9ECF5")
        paragraph = cell.paragraphs[0]
        paragraph.paragraph_format.space_after = Pt(0)
        set_font(paragraph.add_run(text), size=9.5, color=NAVY, bold=True)
    architecture = (
        ("触点层", "响应式网页 · H5 · 微信小程序", "面向手语使用者与服务人员"),
        ("交互层", "Vue 3 · Vue Router · Element Plus", "多输入、双语与无障碍交互"),
        ("服务层", "Django REST Framework · Channels · WebSocket", "认证、任务、权限与实时会话"),
        ("智能层", "InferenceService · Ultralytics YOLO · CSL/ASL 权重", "模型缓存、推理与结果规范化"),
        ("数据层", "SQLite / MySQL · 本地媒体 / S3 兼容存储", "用户、模型、任务与结果追溯"),
    )
    for row_index, values in enumerate(architecture):
        cells = table.add_row().cells
        for cell, text in zip(cells, values):
            if row_index % 2 == 1:
                set_cell_shading(cell, "FAFBFC")
            paragraph = cell.paragraphs[0]
            paragraph.paragraph_format.space_after = Pt(0)
            set_font(paragraph.add_run(text), size=9, color=TEXT)
    set_table_width(table, widths)
    set_repeat_table_header(table.rows[0])


def add_section_image(document: Document, heading: str) -> None:
    if heading.startswith("6. "):
        add_picture(
            document,
            ASSETS / "06-model-metrics.png",
            "中文手语模型真实评测卡",
            "模型中心展示 CSL 模型 Precision、Recall、mAP、样本量、延迟、硬件和能力边界。",
            "图 1  模型评测卡：指标、数据集、硬件、日期与能力边界同时公开",
        )
    elif heading.startswith("7. "):
        add_picture(
            document,
            ASSETS / "11-workbench-real-inference.png",
            "中文手语图片真实识别完成态",
            "工作台显示上传的 you.jpg、边界框、你你的这个识别结果、92.6% 置信度和沟通动作。",
            "图 2  真实推理：上传 CSL 图片后完成识别、场景建议与双方确认",
        )
    elif heading.startswith("8. "):
        add_picture(
            document,
            ASSETS / "10-traceability-evidence.png",
            "识别结果参数与追溯证据",
            "结果详情显示 SHA-256、模型快照、置信度阈值、IoU 阈值和三个结果版本。",
            "图 3  可信结果：文件哈希、识别参数、模型快照与版本对比",
        )
    elif heading.startswith("9. "):
        add_picture(
            document,
            ASSETS / "13-web-responsive.png",
            "SignFlow AI 响应式网页",
            "390×844 响应式页面展示移动浏览器中的产品布局、可读字号和无横向溢出状态。",
            "图 4  响应式网页：390×844 视口无横向溢出和破图",
        )
    elif heading.startswith("10. "):
        add_picture(
            document,
            ASSETS / "04-overview.png",
            "SignFlow AI 运行概览",
            "登录后概览展示任务、成功率、平均耗时、待确认数和服务在线状态。",
            "图 5  运行概览：真实统计、趋势图与后端服务状态",
        )


def add_interface_images(document: Document, heading: str) -> None:
    figures = INTERFACE_FIGURES.get(heading)
    if not figures:
        return
    for filename, title, description, caption in figures:
        max_height = 4.05 if filename.startswith(("12-", "25-", "28-")) else 4.85
        add_picture(
            document,
            ASSETS / filename,
            title,
            description,
            caption,
            max_height=max_height,
        )


def parse_markdown(document: Document) -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    start = next(index for index, line in enumerate(lines) if line.startswith("## 1."))
    lines = lines[start:]
    index = 0
    page_break_sections = ("6. ", "7. ", "11. ")
    while index < len(lines):
        raw = lines[index].rstrip()
        stripped = raw.strip()
        if not stripped or stripped == "---":
            index += 1
            continue
        if stripped.startswith("```"):
            code_lines: list[str] = []
            index += 1
            while index < len(lines) and not lines[index].strip().startswith("```"):
                code_lines.append(lines[index].rstrip())
                index += 1
            add_code_block(document, code_lines)
            index += 1
            continue
        if stripped.startswith("|"):
            table_rows: list[list[str]] = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                row = [cell.strip() for cell in lines[index].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{3,}:?", cell) for cell in row):
                    table_rows.append(row)
                index += 1
            if len(table_rows) >= 2:
                add_markdown_table(document, table_rows)
            continue
        if stripped.startswith("## "):
            heading = stripped[3:].strip()
            if heading.startswith("12. "):
                break
            if heading.startswith("9. "):
                section = document.add_section(WD_SECTION.NEW_PAGE)
                configure_section(section, different_first_page=False)
            elif heading.startswith(page_break_sections):
                document.add_page_break()
            document.add_heading(heading, level=1)
            add_section_image(document, heading)
            index += 1
            continue
        if stripped.startswith("### "):
            heading = stripped[4:].strip()
            if heading.startswith(("4.3 ", "4.4 ", "4.5 ")):
                document.add_page_break()
            document.add_heading(heading, level=2)
            index += 1
            continue
        if stripped.startswith("#### "):
            heading = stripped[5:].strip()
            document.add_heading(heading, level=3)
            add_interface_images(document, heading)
            index += 1
            continue
        if stripped.startswith("> "):
            table = document.add_table(rows=1, cols=1)
            set_table_width(table, [CONTENT_WIDTH_DXA])
            set_repeat_table_header(table.rows[0])
            set_table_borders(table, color=BRAND, size=6)
            cell = table.cell(0, 0)
            set_cell_shading(cell, PALE)
            paragraph = cell.paragraphs[0]
            paragraph.style = "Callout"
            paragraph.paragraph_format.space_after = Pt(0)
            add_inline_runs(paragraph, stripped[2:])
            index += 1
            continue
        if re.match(r"^\d+\.\s+", stripped) or stripped.startswith("- "):
            numbered = bool(re.match(r"^\d+\.\s+", stripped))
            items: list[str] = []
            while index < len(lines):
                candidate = lines[index].strip()
                if numbered and re.match(r"^\d+\.\s+", candidate):
                    items.append(re.sub(r"^\d+\.\s+", "", candidate))
                    index += 1
                elif not numbered and candidate.startswith("- "):
                    items.append(candidate[2:])
                    index += 1
                else:
                    break
            for item_index, item in enumerate(items, start=1):
                if numbered:
                    paragraph = document.add_paragraph()
                    paragraph.paragraph_format.left_indent = Inches(0.375)
                    paragraph.paragraph_format.first_line_indent = Inches(-0.194)
                    paragraph.paragraph_format.space_after = Pt(4)
                    paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
                    paragraph.paragraph_format.line_spacing = 1.208
                    add_inline_runs(paragraph, f"{item_index}.  {item}")
                else:
                    paragraph = document.add_paragraph(style="List Bullet")
                    add_inline_runs(paragraph, f"\u00a0{item}")
            continue

        paragraph_lines = [stripped]
        index += 1
        while index < len(lines):
            next_line = lines[index].strip()
            if (
                not next_line
                or next_line == "---"
                or next_line.startswith(("#", "|", "```", "> ", "- "))
                or re.match(r"^\d+\.\s+", next_line)
            ):
                break
            paragraph_lines.append(next_line)
            index += 1
        paragraph = document.add_paragraph()
        add_inline_runs(paragraph, " ".join(paragraph_lines))


def add_final_handoff(document: Document) -> None:
    document.add_page_break()
    document.add_heading("12. 现场演示与提交说明", level=1)
    paragraph = document.add_paragraph(style="Lead")
    paragraph.add_run(
        "建议按照“产品首页 → 产品导览 → 真实识别 → 结果追溯 → 模型评测卡”的顺序展示。"
        "运行界面保持商业产品表达，赛题映射只在参赛报告中说明。"
    )
    document.add_heading("90 秒演示节奏", level=2)
    script_table = document.add_table(rows=1, cols=3)
    set_table_width(script_table, [1400, 2700, 5260])
    set_table_borders(script_table)
    for cell, text in zip(script_table.rows[0].cells, ("时间", "演示动作", "讲解重点")):
        set_cell_shading(cell, "E9ECF5")
        paragraph = cell.paragraphs[0]
        paragraph.paragraph_format.space_after = Pt(0)
        set_font(paragraph.add_run(text), size=9.5, color=NAVY, bold=True)
    for timing, action, message in (
        ("0—15 秒", "产品首页", "说明目标：让手语沟通自然进入每一次服务。"),
        ("15—30 秒", "产品导览", "展示多模态、双模型、三种公共服务场景和可信闭环。"),
        ("30—55 秒", "真实识别", "上传 CSL 图片，展示标签、置信度、耗时、模型版本与真实任务标记。"),
        ("55—72 秒", "沟通行动", "演示朗读、复制、协助卡和双方确认，强调模型不直接替代最终判断。"),
        ("72—84 秒", "结果追溯", "展示原始媒体、SHA-256、识别参数和结果版本对比。"),
        ("84—90 秒", "工程证据", "42 项网页、11 项手机端、70 项后端测试；依赖审计无已知漏洞。"),
    ):
        cells = script_table.add_row().cells
        for cell, text in zip(cells, (timing, action, message)):
            paragraph = cell.paragraphs[0]
            paragraph.paragraph_format.space_after = Pt(0)
            set_font(paragraph.add_run(text), size=9, color=TEXT)
    set_table_width(script_table, [1400, 2700, 5260])
    set_repeat_table_header(script_table.rows[0])

    document.add_heading("运行入口", level=2)
    links = (
        ("产品首页", "http://127.0.0.1:8080/"),
        ("产品导览", "http://127.0.0.1:8080/product-tour"),
        ("识别工作台", "http://127.0.0.1:8080/app/workbench"),
        ("模型中心", "http://127.0.0.1:8080/app/models"),
        ("结果中心", "http://127.0.0.1:8080/app/results"),
        ("后端健康检查", "http://127.0.0.1:8001/health/ready"),
    )
    table = document.add_table(rows=1, cols=2)
    set_table_width(table, [3000, 6360])
    set_repeat_table_header(table.rows[0])
    set_table_borders(table)
    for cell, text in zip(table.rows[0].cells, ("入口", "地址")):
        set_cell_shading(cell, "E9ECF5")
        paragraph = cell.paragraphs[0]
        paragraph.paragraph_format.space_after = Pt(0)
        set_font(paragraph.add_run(text), size=9.5, color=NAVY, bold=True)
    for label, url in links:
        cells = table.add_row().cells
        first = cells[0].paragraphs[0]
        first.paragraph_format.space_after = Pt(0)
        set_font(first.add_run(label), size=9.5, color=TEXT, bold=True)
        second = cells[1].paragraphs[0]
        second.paragraph_format.space_after = Pt(0)
        add_hyperlink(second, f"打开{label}", url)
        set_font(second.add_run(f"  ·  {url}"), size=8.5, color=MUTED)
    set_table_width(table, [3000, 6360])

    document.add_heading("提交前检查", level=2)
    for item in (
        "现场电脑使用固定浏览器并提前授权摄像头；准备仓库内 CSL 图片和短视频作为备用输入。",
        "演示开始前确认前端 8080、后端 8001 健康检查均可访问。",
        "将单次 92.6% 置信度表述为链路证据；总体能力以模型评测卡的 Precision、Recall 和 mAP 为准。",
        "明确 ASL 指标来自训练期间可见验证集，CSL test split 仍缺少采集主体完全独立的证明。",
        "医疗场景仅用于沟通辅助，不替代诊断、医嘱或专业手语翻译。",
    ):
        paragraph = document.add_paragraph(style="List Bullet")
        add_inline_runs(paragraph, item)

    closing = document.add_table(rows=1, cols=1)
    set_table_width(closing, [CONTENT_WIDTH_DXA])
    set_repeat_table_header(closing.rows[0])
    set_table_borders(closing, color=BRAND, size=8)
    cell = closing.cell(0, 0)
    set_cell_shading(cell, PALE)
    paragraph = cell.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_after = Pt(0)
    set_font(paragraph.add_run("让手语被看见，让公共服务真正抵达每一个人。"), size=15, color=BRAND_DARK, bold=True)


def set_core_properties(document: Document) -> None:
    properties = document.core_properties
    properties.title = "无界手语 SignFlow AI——AI+无障碍公共服务平台参赛报告"
    properties.subject = "赛题三：面向科学、工程和社会科学的 AI+X 应用"
    properties.author = "无界手语 SignFlow AI 项目组"
    properties.keywords = "AI+X, 手语识别, 无障碍, 公共服务, CSL, ASL, YOLO"
    properties.comments = "Submission 3.0 · Complete interface guide · Verified 2026-07-30"


def main() -> None:
    document = Document()
    style_document(document)
    add_header_footer(document)
    set_core_properties(document)
    add_cover(document)
    add_executive_spread(document)
    parse_markdown(document)
    add_final_handoff(document)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
