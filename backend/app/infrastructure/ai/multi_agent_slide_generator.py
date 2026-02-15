"""
LLM-driven multi-agent slide output generator.
"""

from __future__ import annotations

import asyncio
import json
import logging
import random
import re
import urllib.parse
from typing import Any

import google.generativeai as genai

from app.core.config import settings
from app.shared.exceptions import ValidationException

logger = logging.getLogger(__name__)


def _extract_json(text: str) -> dict[str, Any]:
    content = text.strip()
    code_block = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
    if code_block:
        content = code_block.group(1).strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Fallback: extract first top-level JSON object.
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(content[start : end + 1])
        raise


class LLMClient:
    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise ValidationException(
                "GEMINI_API_KEY is required for LLM multi-agent slide generation."
            )
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)

    async def generate_json(self, prompt: str) -> dict[str, Any]:
        def _call() -> dict[str, Any]:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "response_mime_type": "application/json",
                    "temperature": 0.3,
                },
            )
            text = getattr(response, "text", "") or ""
            if not text:
                logger.warning("Gemini returned empty text response.")
            return _extract_json(text)

        return await asyncio.to_thread(_call)


class PlannerAgent:
    """Extract structured plan from the outline."""

    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def run(
        self,
        title: str,
        description: str,
        *,
        page_num: int | None = None,
        total_pages: int | None = None,
        previous_slide_summary: str | None = None,
        current_outline_id: str | None = None,
        outlines_context: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        prompt = f"""
You are PlannerAgent for slide generation.
Given an outline title and description, output JSON only.

Constraints:
- language: Japanese
- points length: 2 to 4
- each point <= 40 chars

Output schema:
{{
  "title": "string",
  "points": ["string", "string"]
}}

Input:
title: {title}
description: {description}
page_num: {page_num}
total_pages: {total_pages}
previous_slide_summary: {previous_slide_summary or ""}
current_outline_id: {current_outline_id}
all_outlines_json: {json.dumps(outlines_context or [], ensure_ascii=False)}
"""
        return await self.llm.generate_json(prompt)


class CopywriterAgent:
    """Convert plan to concise slide copy."""

    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def run(
        self,
        plan: dict[str, Any],
        *,
        page_num: int | None = None,
        total_pages: int | None = None,
        previous_slide_summary: str | None = None,
        current_outline_id: str | None = None,
        outlines_context: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        prompt = f"""
You are CopywriterAgent for slides.
Refine the content for one slide and output JSON only.

Constraints:
- language: Japanese
- title <= 24 chars
- bullets length: exactly 2
- each bullet <= 30 chars

Output schema:
{{
  "title": "string",
  "bullets": ["string", "string"]
}}

Input JSON:
{json.dumps(plan, ensure_ascii=False)}
page_num: {page_num}
total_pages: {total_pages}
previous_slide_summary: {previous_slide_summary or ""}
current_outline_id: {current_outline_id}
all_outlines_json: {json.dumps(outlines_context or [], ensure_ascii=False)}
"""
        return await self.llm.generate_json(prompt)


class VisualAgent:
    """Create a visual prompt and derive placeholder image URL."""

    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def run(
        self,
        *,
        title: str,
        bullets: list[str],
        image_url: str | None = None,
        page_num: int | None = None,
        total_pages: int | None = None,
        previous_slide_summary: str | None = None,
        current_outline_id: str | None = None,
        outlines_context: list[dict[str, Any]] | None = None,
    ) -> str:
        if image_url:
            return image_url

        prompt = f"""
You are VisualAgent for one slide.
Create a short visual keyword phrase for placeholder image text.
Output JSON only.

Output schema:
{{
  "visual_keywords": "string"
}}

Input:
title: {title}
bullets: {json.dumps(bullets, ensure_ascii=False)}
page_num: {page_num}
total_pages: {total_pages}
previous_slide_summary: {previous_slide_summary or ""}
current_outline_id: {current_outline_id}
all_outlines_json: {json.dumps(outlines_context or [], ensure_ascii=False)}
"""
        resp = await self.llm.generate_json(prompt)
        keywords = str(resp.get("visual_keywords", "")).strip() or title
        encoded = urllib.parse.quote_plus(keywords[:24] or "Slide")
        return f"https://placehold.co/600x400/png?text={encoded}"


class LayoutPlannerAgent:
    """Choose visual layout pattern for this slide."""

    _ALLOWED = {"title_top_image_bottom", "title_left_image_right", "hero_center"}

    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def run(
        self,
        *,
        title: str,
        bullets: list[str],
        page_num: int | None = None,
        total_pages: int | None = None,
        previous_slide_summary: str | None = None,
        current_outline_id: str | None = None,
        outlines_context: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        prompt = f"""
You are LayoutPlannerAgent for one-slide layout.
Choose one layout key from allowed values. Output JSON only.

Allowed layout values:
- title_top_image_bottom
- title_left_image_right
- hero_center

Output schema:
{{
  "layout": "title_top_image_bottom | title_left_image_right | hero_center",
  "title_font_pt": 40,
  "bullet_font_pt": 22
}}

Constraints:
- title_font_pt: 34-56
- bullet_font_pt: 18-28

Input:
title: {title}
bullets: {json.dumps(bullets, ensure_ascii=False)}
page_num: {page_num}
total_pages: {total_pages}
previous_slide_summary: {previous_slide_summary or ""}
current_outline_id: {current_outline_id}
all_outlines_json: {json.dumps(outlines_context or [], ensure_ascii=False)}
"""
        data = await self.llm.generate_json(prompt)
        layout = str(data.get("layout", "")).strip()
        if layout not in self._ALLOWED:
            layout = random.choice(list(self._ALLOWED))
        title_font = int(data.get("title_font_pt", 48))
        bullet_font = int(data.get("bullet_font_pt", 24))
        return {
            "layout": layout,
            "title_font_pt": max(34, min(56, title_font)),
            "bullet_font_pt": max(18, min(28, bullet_font)),
        }


class LayoutAgent:
    """Assemble final one-slide JSON structure."""

    @staticmethod
    def _build_title_text_elements(
        title: str, *, title_font_pt: int
    ) -> list[dict[str, Any]]:
        return [
            {
                "startIndex": 0,
                "endIndex": len(title),
                "textRun": {
                    "content": title,
                    "style": {
                        "fontSize": {"magnitude": title_font_pt, "unit": "PT"},
                        "bold": True,
                        "foregroundColor": {
                            "opaqueColor": {"themeColor": "DARK1"}
                        },
                        "fontFamily": "Arial",
                    },
                },
            }
        ]

    @staticmethod
    def _build_bullet_text_elements(
        bullets: list[str], *, bullet_font_pt: int
    ) -> list[dict[str, Any]]:
        text_elements: list[dict[str, Any]] = []
        cursor = 0
        for bullet in bullets:
            content = f"{bullet}\n"
            end = cursor + len(content)
            text_elements.append(
                {
                    "startIndex": cursor,
                    "endIndex": end,
                    "textRun": {
                        "content": content,
                        "style": {
                            "fontSize": {"magnitude": bullet_font_pt, "unit": "PT"}
                        },
                    },
                }
            )
            text_elements.append(
                {
                    "startIndex": end - 1,
                    "endIndex": end,
                    "paragraphMarker": {
                        "style": {
                            "bullet": {"listId": "list-id-1", "nestingLevel": 0}
                        }
                    },
                }
            )
            cursor = end
        return text_elements

    @staticmethod
    def _layout_spec(layout_name: str) -> dict[str, dict[str, float]]:
        if layout_name == "title_left_image_right":
            return {
                "title": {"x": 50, "y": 60, "w": 420, "h": 120},
                "bullets": {"x": 50, "y": 190, "w": 420, "h": 250},
                "image": {"x": 500, "y": 80, "w": 410, "h": 360},
            }
        if layout_name == "hero_center":
            return {
                "title": {"x": 90, "y": 40, "w": 780, "h": 90},
                "bullets": {"x": 210, "y": 360, "w": 540, "h": 130},
                "image": {"x": 240, "y": 120, "w": 480, "h": 230},
            }
        return {
            "title": {"x": 50, "y": 40, "w": 860, "h": 80},
            "bullets": {"x": 50, "y": 150, "w": 860, "h": 300},
            "image": {"x": 180, "y": 250, "w": 600, "h": 250},
        }

    def run(
        self,
        *,
        slide_id: str,
        title: str,
        bullets: list[str],
        image_url: str,
        layout_name: str,
        title_font_pt: int,
        bullet_font_pt: int,
    ) -> dict[str, Any]:
        spec = self._layout_spec(layout_name)
        return {
            "objectId": slide_id,
            "pageType": "SLIDE",
            "pageElements": [
                {
                    "objectId": f"{slide_id}-elem-1",
                    "transform": {
                        "scaleX": 1,
                        "scaleY": 1,
                        "translateX": spec["title"]["x"],
                        "translateY": spec["title"]["y"],
                    },
                    "size": {
                        "width": {"magnitude": spec["title"]["w"], "unit": "PT"},
                        "height": {"magnitude": spec["title"]["h"], "unit": "PT"},
                    },
                    "shape": {
                        "shapeType": "TEXT_BOX",
                        "text": {
                            "textElements": self._build_title_text_elements(
                                title, title_font_pt=title_font_pt
                            )
                        },
                    },
                },
                {
                    "objectId": f"{slide_id}-elem-2",
                    "transform": {
                        "scaleX": 1,
                        "scaleY": 1,
                        "translateX": spec["bullets"]["x"],
                        "translateY": spec["bullets"]["y"],
                    },
                    "size": {
                        "width": {"magnitude": spec["bullets"]["w"], "unit": "PT"},
                        "height": {"magnitude": spec["bullets"]["h"], "unit": "PT"},
                    },
                    "shape": {
                        "shapeType": "TEXT_BOX",
                        "text": {
                            "textElements": self._build_bullet_text_elements(
                                bullets, bullet_font_pt=bullet_font_pt
                            )
                        },
                    },
                },
                {
                    "objectId": f"{slide_id}-elem-3",
                    "transform": {
                        "scaleX": 1,
                        "scaleY": 1,
                        "translateX": spec["image"]["x"],
                        "translateY": spec["image"]["y"],
                    },
                    "size": {
                        "width": {"magnitude": spec["image"]["w"], "unit": "PT"},
                        "height": {"magnitude": spec["image"]["h"], "unit": "PT"},
                    },
                    "image": {"contentUrl": image_url},
                },
            ],
        }


class MultiAgentSlideGenerator:
    """Coordinator for LLM multi-agent slide generation."""

    def __init__(self) -> None:
        llm = LLMClient()
        self.planner = PlannerAgent(llm)
        self.copywriter = CopywriterAgent(llm)
        self.visual = VisualAgent(llm)
        self.layout_planner = LayoutPlannerAgent(llm)
        self.layout = LayoutAgent()

    async def generate_one_slide(
        self,
        *,
        title: str,
        description: str,
        slide_id: str = "slide-mvp-001",
        image_url: str | None = None,
        page_num: int | None = None,
        total_pages: int | None = None,
        previous_slide_summary: str | None = None,
        current_outline_id: str | None = None,
        outlines_context: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        try:
            planned = await self.planner.run(
                title=title,
                description=description,
                page_num=page_num,
                total_pages=total_pages,
                previous_slide_summary=previous_slide_summary,
                current_outline_id=current_outline_id,
                outlines_context=outlines_context,
            )
            written = await self.copywriter.run(
                plan=planned,
                page_num=page_num,
                total_pages=total_pages,
                previous_slide_summary=previous_slide_summary,
                current_outline_id=current_outline_id,
                outlines_context=outlines_context,
            )
            slide_title = str(written.get("title", title)).strip()[:24] or title
            bullets = [
                str(x).strip()
                for x in written.get("bullets", [])
                if str(x).strip()
            ][:2]
            if len(bullets) < 2:
                bullets = [description[:28] or "要点を提示", "次のアクションを示す"][:2]
            final_image_url = await self.visual.run(
                title=slide_title,
                bullets=bullets,
                image_url=image_url,
                page_num=page_num,
                total_pages=total_pages,
                previous_slide_summary=previous_slide_summary,
                current_outline_id=current_outline_id,
                outlines_context=outlines_context,
            )
            layout_plan = await self.layout_planner.run(
                title=slide_title,
                bullets=bullets,
                page_num=page_num,
                total_pages=total_pages,
                previous_slide_summary=previous_slide_summary,
                current_outline_id=current_outline_id,
                outlines_context=outlines_context,
            )
        except Exception:
            # Fallback keeps API resilient when model output is malformed.
            logger.exception(
                "LLM multi-agent generation failed. Falling back to rule-based output. "
                "title=%s slide_id=%s",
                title,
                slide_id,
            )
            slide_title = (title or "Untitled Slide").strip()[:24]
            bullets = [b for b in re.split(r"[\n。.!?]\s*", description) if b.strip()]
            bullets = [b.strip(" ・-\t")[:30] for b in bullets[:2]]
            if len(bullets) < 2:
                bullets = ["要点を整理して提示する", "次のアクションを明確化する"]
            text = urllib.parse.quote_plus((slide_title or bullets[0])[:24])
            final_image_url = image_url or f"https://placehold.co/600x400/png?text={text}"
            layout_plan = {
                "layout": random.choice(
                    ["title_top_image_bottom", "title_left_image_right", "hero_center"]
                ),
                "title_font_pt": 48,
                "bullet_font_pt": 24,
            }

        logger.info(
            "multi-agent slide generated: page=%s/%s outlines=%s layout=%s title=%s",
            page_num,
            total_pages,
            len(outlines_context or []),
            layout_plan.get("layout"),
            slide_title,
        )

        return self.layout.run(
            slide_id=slide_id,
            title=slide_title,
            bullets=bullets,
            image_url=final_image_url,
            layout_name=str(layout_plan.get("layout", "title_top_image_bottom")),
            title_font_pt=int(layout_plan.get("title_font_pt", 48)),
            bullet_font_pt=int(layout_plan.get("bullet_font_pt", 24)),
        )
