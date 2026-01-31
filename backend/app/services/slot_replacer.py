import re
from app.config.gemini import get_available_model
from app.types import FillSlotRequest, FilledSlot


async def fill_slot_with_ai(request: FillSlotRequest) -> str:
    """AIを使ってスロットの内容を生成・置き換え"""
    model = get_available_model()
    
    slot_id = request.slot_id
    value = request.value
    context = request.context or {}
    
    # コンテキスト情報を構築
    context_prompt = ""
    if context:
        story = context.get("story", [])
        other_slots = context.get("otherSlots", [])
        
        context_prompt = f"""
関連ストーリー:
{chr(10).join([f"- {s.get('title', '')}: {s.get('content', '')}" for s in story]) if story else "なし"}

関連スロット:
{chr(10).join([f"- {s.get('name', '')}: {s.get('value', '')}" for s in other_slots]) if other_slots else "なし"}
"""
    
    prompt = f"""
以下のスロットに適切な内容を生成してください。

スロットID: {slot_id}
ユーザー入力: {value or "なし"}

{context_prompt}

要件:
1. ユーザー入力がある場合は、それを基に適切な内容を生成
2. ユーザー入力がない場合は、コンテキストから適切な内容を推測
3. 関連するストーリーや他のスロットと一貫性を保つ
4. 簡潔で明確な内容にする

生成した内容のみを返してください（説明や余計なテキストは不要）。
"""
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error filling slot with AI: {e}")
        # フォールバック: ユーザー入力をそのまま返す
        return value or ""


def replace_slot_in_html(html: str, slot_id: str, new_value: str, slot_type: str) -> str:
    """HTML内の特定スロットを置き換え"""
    # スロットIDに基づいてHTML内の該当箇所を置き換え
    slot_selector = f'[data-slot-id="{slot_id}"]'
    
    # タイプに応じた置き換え
    replacement_html = ""
    
    if slot_type == "title":
        replacement_html = f'<h1 class="slide-title" data-slot-id="{slot_id}">{escape_html(new_value)}</h1>'
    elif slot_type == "text":
        replacement_html = f'<p class="slide-text" data-slot-id="{slot_id}">{escape_html(new_value)}</p>'
    elif slot_type == "list":
        list_items = [item.strip() for item in new_value.split("\n") if item.strip()]
        items_html = "".join([f"<li>{escape_html(item)}</li>" for item in list_items])
        replacement_html = f'<ul class="slide-list" data-slot-id="{slot_id}">{items_html}</ul>'
    elif slot_type in ["image", "icon"]:
        replacement_html = f'<div class="slide-image" data-slot-id="{slot_id}"><img src="{escape_html(new_value)}" alt="{slot_id}" /></div>'
    elif slot_type == "chart":
        replacement_html = f'<div class="slide-chart" data-slot-id="{slot_id}">{escape_html(new_value)}</div>'
    else:
        replacement_html = f'<div data-slot-id="{slot_id}">{escape_html(new_value)}</div>'
    
    # HTML内の該当スロットを置き換え
    # 正規表現で置き換え（簡易実装）
    pattern = rf'<[^>]*data-slot-id="{re.escape(slot_id)}"[^>]*>.*?</[^>]*>'
    
    if re.search(pattern, html, re.DOTALL):
        return re.sub(pattern, replacement_html, html, flags=re.DOTALL)
    
    # 見つからない場合は、適切な場所に挿入
    return html


def escape_html(text: str) -> str:
    """HTMLエスケープ"""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#039;")
    )

