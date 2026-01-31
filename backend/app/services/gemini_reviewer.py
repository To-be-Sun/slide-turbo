import json
import re
from app.config.gemini import get_available_model
from app.types import SlideReview, SuggestedSlot, PresentationReview


async def review_slide_html(html: str, slide_index: int) -> SlideReview:
    """スライドHTMLをレビューしてメタデータを生成"""
    model = get_available_model()
    
    prompt = f"""
以下のHTMLスライドを分析して、以下の情報をJSON形式で返してください：

1. title: スライドのタイトル（簡潔に、30文字以内）
2. description: スライドの説明（50文字以内）
3. suggestedSlots: このスライドから抽出できる編集可能なスロットの配列
   - id: スロットID（例: "s{slide_index}-title"）
   - name: スロット名（例: "タイトル"）
   - type: スロットタイプ（"title" | "text" | "image" | "chart" | "list" | "icon"）
   - placeholder: プレースホルダーテキスト
   - required: 必須かどうか
4. improvements: 改善提案（任意、配列）

HTML:
{html[:5000]}{"..." if len(html) > 5000 else ""}

JSON形式のみを返してください。説明や余計なテキストは不要です。
"""
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # JSONを抽出（```json```ブロックがある場合）
        json_text = text
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if json_match:
            json_text = json_match.group(1)
        
        review_data = json.loads(json_text)
        
        # バリデーション
        if not review_data.get("title") or not review_data.get("description"):
            raise ValueError("Invalid review response: missing title or description")
        
        return SlideReview(
            title=review_data["title"],
            description=review_data["description"],
            suggested_slots=[
                SuggestedSlot(**slot) for slot in review_data.get("suggestedSlots", [])
            ],
            improvements=review_data.get("improvements"),
        )
    except Exception as e:
        print(f"Error reviewing slide HTML: {e}")
        
        # フォールバック: 基本的なレビューを返す
        return SlideReview(
            title=f"スライド {slide_index + 1}",
            description="スライドコンテンツ",
            suggested_slots=[
                SuggestedSlot(
                    id=f"s{slide_index}-title",
                    name="タイトル",
                    type="title",
                    placeholder="スライドのタイトル",
                    required=True,
                )
            ],
        )


async def review_presentation(slides_html: list[str]) -> PresentationReview:
    """プレゼンテーション全体をレビュー"""
    model = get_available_model()
    
    # 各スライドをレビュー
    slide_reviews = []
    for index, html in enumerate(slides_html):
        review = await review_slide_html(html, index)
        slide_reviews.append(review)
    
    # 全体のタイトルと説明を生成
    all_titles = ", ".join([r.title for r in slide_reviews])
    prompt = f"""
以下のスライドタイトルから、プレゼンテーション全体のタイトルと説明を生成してください：

スライドタイトル:
{all_titles}

以下のJSON形式で返してください：
{{
  "title": "プレゼンテーション全体のタイトル",
  "description": "プレゼンテーションの説明（100文字以内）"
}}

JSON形式のみを返してください。
"""
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        json_text = text
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if json_match:
            json_text = json_match.group(1)
        
        presentation_info = json.loads(json_text)
        
        return PresentationReview(
            title=presentation_info.get("title", "Untitled Presentation"),
            description=presentation_info.get("description", ""),
            slide_reviews=slide_reviews,
        )
    except Exception as e:
        print(f"Error reviewing presentation: {e}")
        return PresentationReview(
            title="Untitled Presentation",
            description="",
            slide_reviews=slide_reviews,
        )

