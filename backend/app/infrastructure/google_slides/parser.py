"""
Google Slides パーサー
プレゼンテーションデータをパースし、テンプレートとして取り込む。
"""

from __future__ import annotations

import re
from typing import Any

from app.infrastructure.google_slides.client import GoogleSlidesClient


class GoogleSlidesParser:
    """Google Slides をパースしてテンプレート構造に変換"""

    def __init__(self, client: GoogleSlidesClient) -> None:
        self.client = client

    @staticmethod
    def extract_presentation_id(url_or_id: str) -> str:
        """URL またはプレゼンテーション ID からIDを抽出"""
        match = re.search(r"/d/([a-zA-Z0-9_-]+)", url_or_id)
        if match:
            return match.group(1)
        return url_or_id

    async def parse(self, url_or_id: str) -> dict[str, Any]:
        """
        Google Slides をフェッチし、テンプレート構造を返す。

        Returns:
            {"title": str, "contents": dict}
        """
        presentation_id = self.extract_presentation_id(url_or_id)
        presentation = self.client.get_presentation(presentation_id)

        title = presentation.get("title", "Untitled")
        slides = presentation.get("slides", [])
        page_size = presentation.get("pageSize") or {}
        slide_w_pt, slide_h_pt = self._slide_size_pt(page_size)

        layouts = presentation.get("layouts") or []
        masters = presentation.get("masters") or []
        layouts_by_id = {l["objectId"]: l for l in layouts if l.get("objectId")}
        masters_by_id = {m["objectId"]: m for m in masters if m.get("objectId")}

        pages = []
        for i, slide in enumerate(slides):
            page_id = slide.get("objectId")
            if page_id:
                try:
                    full_page = self.client.get_page(presentation_id, page_id)
                    slide = full_page
                except Exception:
                    pass
            layout = None
            layout_id = (slide.get("slideProperties") or {}).get("layoutObjectId")
            if layout_id and layout_id in layouts_by_id:
                try:
                    layout = self.client.get_page(presentation_id, layout_id)
                except Exception:
                    layout = layouts_by_id[layout_id]
            pages.append(
                {
                    "pageNum": i + 1,
                    "pageObjectId": slide.get("objectId"),
                    "elements": self._extract_elements(
                        slide, page_size, layouts_by_id, masters_by_id, layout
                    ),
                }
            )

        return {
            "title": title,
            "contents": {
                "presentationId": presentation_id,
                "pageCount": len(slides),
                "pageSize": {"widthPt": slide_w_pt, "heightPt": slide_h_pt},
                "pages": pages,
            },
        }

    # デフォルトスライドサイズ (pt) — 16:9
    _SLIDE_WIDTH_PT = 720.0
    _SLIDE_HEIGHT_PT = 405.0
    # 1 PT = 914400/72 EMU
    _EMU_PER_PT = 914400.0 / 72.0

    @classmethod
    def _to_pt(cls, v: Any, fallback_unit: str | None = None) -> float:
        """Dimension または number を PT に正規化。EMU の場合は PT に変換する"""
        if v is None:
            return 0.0
        mag: float
        u: str | None
        if isinstance(v, (int, float)):
            mag = float(v)
            u = fallback_unit
        elif isinstance(v, dict):
            mag = float(v.get("magnitude", 0))
            u = v.get("unit") or fallback_unit
        else:
            return 0.0
        # API が EMU で返す場合、または数値が PT ではありえない大きさなら EMU とみなす（PT は通常 0～1000 程度）
        u_str = (u or "").upper()
        if u_str == "EMU" or (not u_str and mag > 50000):
            mag = mag / cls._EMU_PER_PT
        return mag

    @staticmethod
    def _solid_fill_to_rgb(sf: dict) -> str | None:
        """solidFill オブジェクトから RGB 文字列を生成。shape / pageBackgroundFill 共通。"""
        if not isinstance(sf, dict):
            return None
        color = sf.get("color")
        if not isinstance(color, dict):
            return None
        rgb = color.get("rgbColor")
        if not isinstance(rgb, dict):
            return None
        r = rgb.get("red", 0)
        g = rgb.get("green", 0)
        b = rgb.get("blue", 0)
        alpha = sf.get("alpha")
        if isinstance(alpha, (int, float)) and alpha < 1.0:
            return f"rgba({int(float(r)*255)},{int(float(g)*255)},{int(float(b)*255)},{alpha})"
        return f"rgb({int(float(r)*255)},{int(float(g)*255)},{int(float(b)*255)})"

    @classmethod
    def _extract_solid_fill(cls, shape: dict) -> str | None:
        """
        shape.shapeProperties.shapeBackgroundFill.solidFill から RGB 色を取得。
        rgbColor のみ対応（themeColor はスキップ）。
        """
        sp = shape.get("shapeProperties") or {}
        sbf = sp.get("shapeBackgroundFill") or {}
        sf = sbf.get("solidFill") or {}
        return cls._solid_fill_to_rgb(sf)

    @staticmethod
    def _extract_page_background_fill(page: dict) -> str | None:
        """
        pageProperties.pageBackgroundFill.solidFill から RGB を取得。
        INHERIT の場合は None（呼び出し側で親を辿る）。
        """
        pp = page.get("pageProperties") or {}
        pbf = pp.get("pageBackgroundFill") or {}
        if pbf.get("propertyState") == "NOT_RENDERED":
            return None
        sf = pbf.get("solidFill")
        if not sf:
            return None
        return GoogleSlidesParser._solid_fill_to_rgb(sf)

    @classmethod
    def _resolve_page_background(
        cls,
        slide: dict,
        layouts_by_id: dict[str, dict],
        masters_by_id: dict[str, dict],
    ) -> str | None:
        """
        スライド → レイアウト → マスター の継承チェーンで pageBackgroundFill を解決。
        solidFill が得られたら RGB 文字列を返す。
        """
        fill = cls._extract_page_background_fill(slide)
        if fill:
            return fill
        layout_id = (slide.get("slideProperties") or {}).get("layoutObjectId")
        if layout_id and layout_id in layouts_by_id:
            layout = layouts_by_id[layout_id]
            fill = cls._extract_page_background_fill(layout)
            if fill:
                return fill
            master_id = (layout.get("layoutProperties") or {}).get("masterObjectId")
            if master_id and master_id in masters_by_id:
                fill = cls._extract_page_background_fill(masters_by_id[master_id])
                if fill:
                    return fill
        return None

    @classmethod
    def _slide_size_pt(cls, page_size: dict) -> tuple[float, float]:
        """presentation.pageSize から幅・高さ (pt) を取得"""
        w = page_size.get("width")
        h = page_size.get("height")
        w_pt = cls._to_pt(w)
        h_pt = cls._to_pt(h)
        if w_pt <= 0:
            w_pt = cls._SLIDE_WIDTH_PT
        if h_pt <= 0:
            h_pt = cls._SLIDE_HEIGHT_PT
        return w_pt, h_pt

    @classmethod
    def _element_to_flat_item(
        cls,
        element: dict,
        parent_tx_pt: float,
        parent_ty_pt: float,
        parent_sx: float,
        parent_sy: float,
        slide_w_pt: float,
        slide_h_pt: float,
    ) -> list[dict]:
        """
        1要素を処理。グループなら子を再帰して絶対座標で返す。
        通常要素なら絶対座標1件のリストを返す（shape/image のみ。unknown はスキップ）。
        """
        transform = element.get("transform") or {}
        size = element.get("size") or {}
        unit = transform.get("unit")
        tx_pt = cls._to_pt(transform.get("translateX"), unit)
        ty_pt = cls._to_pt(transform.get("translateY"), unit)
        sx = float(transform.get("scaleX") or 1)
        sy = float(transform.get("scaleY") or 1)
        w_pt = cls._to_pt(size.get("width"))
        h_pt = cls._to_pt(size.get("height"))
        if w_pt <= 0:
            w_pt = 100.0
        if h_pt <= 0:
            h_pt = 50.0
        # 親座標系での位置・サイズ → ページ絶対座標（親の scale をかける）
        abs_tx = parent_tx_pt + parent_sx * tx_pt
        abs_ty = parent_ty_pt + parent_sy * ty_pt
        abs_w = w_pt * sx * parent_sx
        abs_h = h_pt * sy * parent_sy

        if "elementGroup" in element:
            children = (element.get("elementGroup") or {}).get("children") or []
            out: list[dict] = []
            for child in children:
                out.extend(
                    cls._element_to_flat_item(
                        child,
                        abs_tx,
                        abs_ty,
                        sx * parent_sx,
                        sy * parent_sy,
                        slide_w_pt,
                        slide_h_pt,
                    )
                )
            return out

        el: dict[str, Any] = {
            "objectId": element.get("objectId"),
            "type": "unknown",
            "left_pt": abs_tx,
            "top_pt": abs_ty,
            "width_pt": abs_w,
            "height_pt": abs_h,
            "left_pct": round(abs_tx / slide_w_pt * 100, 2),
            "top_pct": round(abs_ty / slide_h_pt * 100, 2),
            "width_pct": round(abs_w / slide_w_pt * 100, 2),
            "height_pct": round(abs_h / slide_h_pt * 100, 2),
        }
        if "shape" in element:
            shape = element["shape"]
            fill = cls._extract_solid_fill(shape)
            if fill:
                el["fill"] = fill
            text_content = (
                (shape or {})
                .get("text", {})
                .get("textElements", []) or []
            )
            parts = []
            for te in text_content:
                if "textRun" not in te:
                    continue
                content = (te.get("textRun") or {}).get("content")
                if content is not None:
                    parts.append(str(content))
            text = " ".join(parts).strip()
            if text:
                el["type"] = "shape"
                el["text"] = text
                return [el]
            if fill:
                el["type"] = "shape_rect"
                return [el]
            return []
        elif "image" in element:
            el["type"] = "image"
            img = element["image"]
            el["contentUrl"] = img.get("contentUrl") or img.get("sourceUrl", "")
            el["sourceUrl"] = el["contentUrl"]
            return [el]
        return []

    @classmethod
    def _extract_elements_from_page(
        cls,
        page: dict,
        slide_w_pt: float,
        slide_h_pt: float,
    ) -> list[dict]:
        """ページ（スライド/レイアウト）からコンテンツ要素のみ抽出（背景なし）"""
        out: list[dict] = []
        for element in page.get("pageElements", []):
            out.extend(
                cls._element_to_flat_item(
                    element,
                    parent_tx_pt=0.0,
                    parent_ty_pt=0.0,
                    parent_sx=1.0,
                    parent_sy=1.0,
                    slide_w_pt=slide_w_pt,
                    slide_h_pt=slide_h_pt,
                )
            )
        return out

    @classmethod
    def _merge_layout_with_slide(
        cls, layout_elements: list[dict], slide_elements: list[dict]
    ) -> list[dict]:
        """
        レイアウト要素（位置・サイズ）にスライドのテキストをマージ。
        テキスト要素はインデックスで対応付け、スライド側のテキストを優先。
        """
        layout_text_indices = [i for i, e in enumerate(layout_elements) if e.get("type") == "shape" and "text" in e]
        slide_texts = [e.get("text", "") for e in slide_elements if e.get("type") == "shape" and e.get("text")]
        result = list(layout_elements)
        for i, layout_idx in enumerate(layout_text_indices):
            if i < len(slide_texts) and slide_texts[i]:
                result[layout_idx] = {**result[layout_idx], "text": slide_texts[i]}
        return result

    @classmethod
    def _extract_elements(
        cls,
        slide: dict,
        page_size: dict | None = None,
        layouts_by_id: dict[str, dict] | None = None,
        masters_by_id: dict[str, dict] | None = None,
        layout: dict | None = None,
    ) -> list[dict]:
        """スライド内の要素 (テキスト, 画像, 図形) を抽出。ページ背景は継承解決して先頭に追加。"""
        slide_w_pt = cls._SLIDE_WIDTH_PT
        slide_h_pt = cls._SLIDE_HEIGHT_PT
        if page_size:
            slide_w_pt, slide_h_pt = cls._slide_size_pt(page_size)

        elements: list[dict] = []

        # ページ背景: スライド→レイアウト→マスターで solidFill を解決し、あれば先頭に追加
        if layouts_by_id is not None and masters_by_id is not None:
            page_bg = cls._resolve_page_background(
                slide, layouts_by_id, masters_by_id
            )
            if page_bg:
                elements.append({
                    "type": "shape_rect",
                    "fill": page_bg,
                    "left_pct": 0,
                    "top_pct": 0,
                    "width_pct": 100,
                    "height_pct": 100,
                })

        slide_content = cls._extract_elements_from_page(slide, slide_w_pt, slide_h_pt)
        layout_content = cls._extract_elements_from_page(layout, slide_w_pt, slide_h_pt) if layout else []

        # レイアウトがある場合: レイアウトの位置・サイズを優先し、スライドのテキストをマージ（元の配置に合わせる）
        if layout_content:
            # 全面背景（0,0,100,100）は page_bg で追加済みのためスキップ
            layout_filtered = [
                e for e in layout_content
                if not (
                    e.get("type") == "shape_rect"
                    and (e.get("left_pct") or 0) == 0
                    and (e.get("top_pct") or 0) == 0
                    and (e.get("width_pct") or 100) >= 99
                    and (e.get("height_pct") or 100) >= 99
                )
            ]
            merged = cls._merge_layout_with_slide(layout_filtered, slide_content)
            elements.extend(merged)
            return elements

        elements.extend(slide_content)
        return elements

    async def parse_debug(self, url_or_id: str) -> dict:
        """
        デバッグ用: パース結果と1ページ目の raw API 生データを返す。
        配置ずれ・塗りつぶし等の診断に使う。rawPage は API レスポンスをそのまま返す。
        """
        parsed = await self.parse(url_or_id)
        contents = parsed.get("contents", {}) or {}
        pages = contents.get("pages") or []
        if not pages:
            return {"pageSize": contents.get("pageSize"), "computedElements": [], "rawPage": None}
        first_page = pages[0]
        presentation_id = self.extract_presentation_id(url_or_id)
        raw_page = None
        page_id = first_page.get("pageObjectId")
        if page_id:
            try:
                raw_page = self.client.get_page(presentation_id, page_id)
            except Exception:
                pass
        return {
            "pageSize": contents.get("pageSize"),
            "computedElements": first_page.get("elements", []),
            "rawPage": raw_page,
        }
