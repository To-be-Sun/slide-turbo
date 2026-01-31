from typing import List
from app.services.google_slides_parser import SlideElement, extract_slide_elements


def convert_presentation_to_html(presentation: dict) -> str:
    """Google Slidesプレゼンテーション全体をHTMLに変換"""
    slides = presentation.get("slides", [])
    if not slides:
        return ""
    
    slides_html = []
    for index, slide in enumerate(slides):
        elements = extract_slide_elements(slide)
        slides_html.append(convert_slide_to_html(elements, index))
    
    title = presentation.get("title", "Untitled")
    return generate_full_presentation_html(slides_html, title)


def convert_slide_to_html(elements: List[SlideElement], slide_index: int) -> str:
    """単一スライドをHTMLに変換"""
    # 要素を位置でソート（上から下、左から右）
    sorted_elements = sorted(
        elements,
        key=lambda el: (
            el.position["y"] if el.position else 0,
            el.position["x"] if el.position else 0,
        ),
    )
    
    # タイトル要素を特定（通常は最初の大きなテキスト要素）
    title_element = None
    for el in sorted_elements:
        if el.type == "text" and el.style and el.style.get("fontSize", 0) > 24:
            title_element = el
            break
    
    # 本文要素
    text_elements = [el for el in sorted_elements if el.type == "text" and el != title_element]
    
    # 画像要素
    image_elements = [el for el in sorted_elements if el.type == "image"]
    
    # その他の要素
    other_elements = [
        el
        for el in sorted_elements
        if el.type not in ["text", "image", "group"] and el != title_element
    ]
    
    # グループ要素
    group_elements = [el for el in sorted_elements if el.type == "group"]
    
    return f"""
<div class="slide" data-slide-index="{slide_index}">
  <div class="slide-content">
    {render_element(title_element, "title") if title_element else ""}
    {"".join([render_element(el, "text") for el in text_elements])}
    {"".join([render_element(el, "image") for el in image_elements])}
    {"".join([render_element(el, "other") for el in other_elements])}
    {"".join([render_element(el, "group") for el in group_elements])}
  </div>
</div>
"""


def render_element(element: SlideElement, context: str) -> str:
    """要素をHTMLにレンダリング"""
    if not element:
        return ""
    
    position_style = ""
    if element.position:
        x = element.position["x"]
        y = element.position["y"]
        width = element.position["width"]
        height = element.position["height"]
        position_style = f"position: absolute; left: {x}px; top: {y}px; width: {width}px; height: {height}px;"
    
    style_attr = position_style
    if element.style:
        style_attr += " " + build_style_string(element.style)
    
    style_attr = f'style="{style_attr}"' if style_attr.strip() else ""
    
    if element.type == "text":
        tag = "h1" if context == "title" else "p"
        class_name = "slide-title" if context == "title" else "slide-text"
        content = escape_html(element.content or "")
        return f'<{tag} class="{class_name}" data-element-id="{element.id}" {style_attr}>{content}</{tag}>'
    
    elif element.type == "image":
        image_url = element.image_url or "/placeholder.svg"
        return f'<div class="slide-image" data-element-id="{element.id}" {style_attr}><img src="{image_url}" alt="Slide image" /></div>'
    
    elif element.type == "table":
        content = escape_html(element.content or "")
        return f'<div class="slide-table" data-element-id="{element.id}" {style_attr}><pre>{content}</pre></div>'
    
    elif element.type == "group":
        children_html = "".join([render_element(child, "other") for child in element.children])
        return f'<div class="slide-group" data-element-id="{element.id}" {style_attr}>{children_html}</div>'
    
    else:
        return f'<div class="slide-element" data-element-id="{element.id}" data-type="{element.type}" {style_attr}></div>'


def build_style_string(style: dict) -> str:
    """スタイルオブジェクトをCSS文字列に変換"""
    styles = []
    
    if style.get("fontSize"):
        styles.append(f"font-size: {style['fontSize']}px")
    if style.get("fontFamily"):
        styles.append(f"font-family: {style['fontFamily']}")
    if style.get("color"):
        styles.append(f"color: {style['color']}")
    if style.get("bold"):
        styles.append("font-weight: bold")
    if style.get("italic"):
        styles.append("font-style: italic")
    if style.get("alignment"):
        styles.append(f"text-align: {style['alignment']}")
    
    return "; ".join(styles)


def escape_html(text: str) -> str:
    """HTMLエスケープ"""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#039;")
    )


def generate_full_presentation_html(slides_html: List[str], title: str) -> str:
    """完全なプレゼンテーションHTMLを生成"""
    return f"""
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape_html(title)}</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: #0a0a0a;
      color: #ffffff;
    }}
    .slides-container {{
      display: flex;
      flex-direction: column;
      gap: 40px;
      padding: 40px;
    }}
    .slide {{
      width: 100%;
      max-width: 1920px;
      margin: 0 auto;
      aspect-ratio: 16 / 9;
      background: white;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
      position: relative;
    }}
    .slide-content {{
      width: 100%;
      height: 100%;
      padding: 60px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      position: relative;
    }}
    .slide-title {{
      font-size: 3rem;
      font-weight: bold;
      margin-bottom: 2rem;
      line-height: 1.2;
    }}
    .slide-text {{
      font-size: 1.5rem;
      line-height: 1.8;
      margin-bottom: 1.5rem;
    }}
    .slide-image {{
      margin: 2rem 0;
    }}
    .slide-image img {{
      width: 100%;
      height: auto;
      border-radius: 8px;
      max-width: 600px;
    }}
    .slide-table {{
      margin: 2rem 0;
    }}
    .slide-table pre {{
      background: rgba(255,255,255,0.1);
      padding: 1rem;
      border-radius: 8px;
      font-size: 1rem;
      white-space: pre-wrap;
    }}
    .slide-group {{
      position: relative;
    }}
    .slide-element {{
      background: rgba(255,255,255,0.1);
      border-radius: 4px;
    }}
  </style>
</head>
<body>
  <div class="slides-container">
    {"".join(slides_html)}
  </div>
</body>
</html>
"""

