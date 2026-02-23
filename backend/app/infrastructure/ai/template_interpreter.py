"""
テンプレート解読
LLM (Gemini) でテンプレート構造を分析し、編集可能スロットを抽出する。
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)

# スロットタイプ（骨子/スライド作成エージェントが利用）
SLOT_TYPES = ("title", "text", "image", "chart", "list", "icon")


def _build_structure_for_llm(contents: dict[str, Any]) -> str:
    """
    パーサー出力を LLM に渡すための簡潔なテキスト表現に変換する。
    各ページの要素（objectId, type, text）を列挙。
    """
    pages = contents.get("pages") or []
    if not pages:
        return "（ページなし）"

    lines: list[str] = []
    for p in pages:
        page_num = p.get("pageNum", 0)
        elements = p.get("elements") or []
        lines.append(f"--- ページ {page_num} ---")
        for el in elements:
            obj_id = el.get("objectId", "")
            el_type = el.get("type", "unknown")
            if el_type == "shape" and "text" in el:
                text = (el.get("text") or "").strip()
                preview = (text[:80] + "…") if len(text) > 80 else text
                lines.append(f"  objectId: {obj_id}, type: shape, text: \"{preview}\"")
            elif el_type == "image":
                lines.append(f"  objectId: {obj_id}, type: image")
            elif el_type == "shape_rect":
                lines.append(f"  objectId: {obj_id}, type: shape_rect")
        lines.append("")
    return "\n".join(lines).strip()


def interpret_template(contents: dict[str, Any]) -> list[dict[str, Any]]:
    """
    テンプレートの contents を LLM で解読し、編集可能スロットのリストを返す。

    Returns:
        slots: [ { objectId, slideIndex, name, type, placeholder, required }, ... ]
        GEMINI_API_KEY が未設定またはエラー時は [] を返す。
    """
    if not settings.gemini_api_key:
        logger.info("GEMINI_API_KEY not set, skipping template interpretation")
        return []

    try:
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
    except Exception as e:
        logger.warning("Failed to init Gemini: %s", e)
        return []

    structure = _build_structure_for_llm(contents)
    pages = contents.get("pages") or []

    prompt = f"""
以下のプレゼンテーションテンプレートの各要素を分析し、編集可能なスロット（AI/ユーザーが内容を埋めるべき場所）を抽出してください。

テンプレート構造:
{structure}

各スロットについて以下の JSON 形式で返してください。objectId は上記の要素の objectId と完全一致させてください。
編集対象とすべきでない要素（装飾のみ、背景など）はスロットに含めないでください。

出力形式（JSON 配列のみ、説明不要）:
[
  {{ "objectId": "elem-1", "slideIndex": 0, "name": "タイトル", "type": "title", "placeholder": "タイトルを入力", "required": true }},
  {{ "objectId": "elem-2", "slideIndex": 0, "name": "本文", "type": "text", "placeholder": "説明を入力", "required": false }}
]

ルール:
- objectId: 上記の objectId をそのまま使用
- slideIndex: 0始まりのページ番号（ページ1 = 0）
- name: スロットの日本語名（例: タイトル、サブタイトル、本文、箇条書き、画像）
- type: "title" | "text" | "image" | "chart" | "list" | "icon" のいずれか
- placeholder: 空のときのヒント文言
- required: 必須かどうか

JSON のみを返してください。
"""

    try:
        response = model.generate_content(prompt)
        text = (response.text or "").strip()
    except Exception as e:
        logger.warning("Gemini API error: %s", e)
        return []

    # JSON 抽出
    json_text = text
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if m:
        json_text = m.group(1)
    json_text = json_text.strip()

    try:
        raw = json.loads(json_text)
    except json.JSONDecodeError as e:
        logger.warning("Failed to parse Gemini response as JSON: %s", e)
        return []

    if not isinstance(raw, list):
        return []

    # バリデーション＆正規化
    valid_object_ids: set[str] = set()
    for p in pages:
        for el in p.get("elements") or []:
            oid = el.get("objectId")
            if oid:
                valid_object_ids.add(oid)

    slots: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        obj_id = item.get("objectId")
        if not obj_id or obj_id not in valid_object_ids:
            continue
        slot_type = item.get("type") or "text"
        if slot_type not in SLOT_TYPES:
            slot_type = "text"
        slots.append({
            "objectId": obj_id,
            "slideIndex": int(item.get("slideIndex", 0)),
            "name": str(item.get("name", "テキスト")).strip() or "テキスト",
            "type": slot_type,
            "placeholder": str(item.get("placeholder", "")).strip() or "入力してください",
            "required": bool(item.get("required", False)),
        })

    logger.info("Template interpretation: %d slots extracted", len(slots))
    return slots
