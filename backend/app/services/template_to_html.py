from typing import List, Optional
from app.config.gemini import get_available_model
from app.types import Template, FilledSlot, StorySection


async def generate_html_from_template(
    template: Template,
    slots: List[FilledSlot],
    story: Optional[List[StorySection]] = None,
) -> str:
    """テンプレートとスロットデータからHTMLを生成"""
    model = get_available_model()
    
    # スライドごとにスロットをグループ化
    slides_data: dict[int, List[dict]] = {}
    for slot in template.slots:
        if slot.slide_index not in slides_data:
            slides_data[slot.slide_index] = []
        
        filled_slot = next((s for s in slots if s.slot_id == slot.id), None)
        slides_data[slot.slide_index].append({
            **slot.dict(),
            "value": filled_slot.value if filled_slot else "",
            "status": filled_slot.status if filled_slot else "empty",
        })
    
    # 各スライドのHTMLを生成
    slides_html = []
    for slide_index, slide_slots in slides_data.items():
        html = await generate_slide_html(slide_index, slide_slots, story)
        slides_html.append(html)
    
    # 全体のHTML構造を生成
    return generate_full_html(slides_html, template)


async def generate_slide_html(
    slide_index: int,
    slots: List[dict],
    story: Optional[List[StorySection]] = None,
) -> str:
    """単一スライドのHTMLを生成"""
    model = get_available_model()
    
    story_context = None
    if story:
        story_context = next(
            (s for s in story if slide_index in s.slide_indices), None
        )
    
    # ストーリーコンテキストを構築
    story_context_text = ""
    if story_context:
        story_context_text = f"タイトル: {story_context.title}\n内容: {story_context.content}"
    else:
        story_context_text = "なし"
    
    # スロット情報を構築
    slot_info_lines = []
    for slot in slots:
        slot_value = slot.get('value') or slot.get('placeholder', '')
        slot_status = slot.get('status', 'empty')
        slot_info_lines.append(f"- {slot['name']} ({slot['type']}): {slot_value}\n  状態: {slot_status}")
    slot_info_text = "\n".join(slot_info_lines)
    
    prompt = f"""
以下の情報から、プレゼンテーションスライドのHTMLを生成してください。

スライド番号: {slide_index + 1}

ストーリーコンテキスト:
{story_context_text}

スロット情報:
{slot_info_text}

要件:
1. モダンでプロフェッショナルなデザイン
2. レスポンシブ対応（16:9のアスペクト比）
3. タイトルスロットは大きく目立つように
4. テキストスロットは読みやすく配置
5. リストスロットは箇条書きで表示
6. 画像/アイコンスロットはプレースホルダーを表示
7. チャートスロットはデータ可視化の準備を
8. 空のスロットは点線の枠で表示

HTMLのみを返してください（<style>タグを含む完全なHTML）。
"""
    
    try:
        response = model.generate_content(prompt)
        html = response.text
        
        # HTMLの開始・終了タグを確認
        if "<html" not in html:
            html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>スライド {slide_index + 1}</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }}
  </style>
</head>
<body>
{html}
</body>
</html>"""
        
        return html
    except Exception as e:
        print(f"Error generating slide HTML: {e}")
        # フォールバック: シンプルなHTMLを生成
        return generate_fallback_slide_html(slide_index, slots)


def generate_fallback_slide_html(slide_index: int, slots: List[dict]) -> str:
    """フォールバック: シンプルなHTMLを生成"""
    title_slot = next((s for s in slots if s["type"] == "title"), None)
    text_slots = [s for s in slots if s["type"] == "text"]
    list_slot = next((s for s in slots if s["type"] == "list"), None)
    image_slot = next((s for s in slots if s["type"] in ["image", "icon"]), None)
    
    title_html = ""
    if title_slot:
        empty_class = "empty" if title_slot.get("status") == "empty" else ""
        value = title_slot.get("value") or title_slot.get("placeholder", "")
        title_html = f'<h1 class="slide-title {empty_class}">{value}</h1>'
    
    text_html = "".join([
        f'<p class="slide-text {"empty" if slot.get("status") == "empty" else ""}">{slot.get("value") or slot.get("placeholder", "")}</p>'
        for slot in text_slots
    ])
    
    list_html = ""
    if list_slot:
        empty_class = "empty" if list_slot.get("status") == "empty" else ""
        value = list_slot.get("value", "")
        items = [item for item in value.split("\n") if item.strip()] if value else []
        items_html = "".join([f"<li>{item}</li>" for item in items]) if items else f'<li>{list_slot.get("placeholder", "")}</li>'
        list_html = f'<ul class="slide-list {empty_class}">{items_html}</ul>'
    
    image_html = ""
    if image_slot:
        empty_class = "empty" if image_slot.get("status") == "empty" else ""
        value = image_slot.get("value", "")
        if value:
            image_html = f'<div class="slide-image {empty_class}"><img src="{value}" alt="{image_slot.get("name", "")}" /></div>'
        else:
            image_html = f'<div class="slide-image {empty_class}"><div class="placeholder">{image_slot.get("placeholder", "")}</div></div>'
    
    return f"""
<div class="slide" data-slide-index="{slide_index}">
  <div class="slide-content">
    {title_html}
    {text_html}
    {list_html}
    {image_html}
  </div>
</div>
<style>
  .slide {{ width: 100%; height: 100vh; display: flex; align-items: center; justify-content: center; padding: 60px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
  .slide-content {{ max-width: 1200px; width: 100%; }}
  .slide-title {{ font-size: 3rem; font-weight: bold; margin-bottom: 2rem; }}
  .slide-title.empty {{ border: 2px dashed rgba(255,255,255,0.5); padding: 1rem; border-radius: 8px; color: rgba(255,255,255,0.7); }}
  .slide-text {{ font-size: 1.5rem; line-height: 1.8; margin-bottom: 1.5rem; }}
  .slide-text.empty {{ border: 2px dashed rgba(255,255,255,0.5); padding: 1rem; border-radius: 8px; color: rgba(255,255,255,0.7); min-height: 60px; }}
  .slide-list {{ font-size: 1.3rem; line-height: 2; margin-left: 2rem; }}
  .slide-list.empty {{ border: 2px dashed rgba(255,255,255,0.5); padding: 1rem; border-radius: 8px; color: rgba(255,255,255,0.7); }}
  .slide-image {{ width: 100%; max-width: 600px; margin: 2rem auto; }}
  .slide-image.empty {{ border: 2px dashed rgba(255,255,255,0.5); padding: 2rem; border-radius: 8px; text-align: center; color: rgba(255,255,255,0.7); }}
  .slide-image img {{ width: 100%; height: auto; border-radius: 8px; }}
</style>
"""


def generate_full_html(slides_html: List[str], template: Template) -> str:
    """全スライドを含む完全なHTMLを生成"""
    return f"""
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{template.name}</title>
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
    .slide-wrapper {{
      width: 100%;
      max-width: 1920px;
      margin: 0 auto;
      aspect-ratio: 16 / 9;
      background: white;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }}
    .slide-wrapper iframe {{
      width: 100%;
      height: 100%;
      border: none;
    }}
  </style>
</head>
<body>
  <div class="slides-container">
    {chr(10).join([f'    <div class="slide-wrapper" data-slide="{index}">{chr(10)}      {html}{chr(10)}    </div>' for index, html in enumerate(slides_html)])}
  </div>
</body>
</html>
"""

