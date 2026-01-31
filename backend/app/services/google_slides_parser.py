from typing import Optional, List
from app.config.google_slides import get_google_slides_client


def fetch_presentation(presentation_id: str):
    """Google SlidesのプレゼンテーションIDからスライドデータを取得"""
    slides = get_google_slides_client()
    
    try:
        presentation = slides.presentations().get(presentationId=presentation_id).execute()
        return presentation
    except Exception as e:
        print(f"Error fetching presentation: {e}")
        raise ValueError(f"Failed to fetch presentation: {str(e)}")


class SlideElement:
    def __init__(
        self,
        element_id: str,
        element_type: str,
        content: Optional[str] = None,
        position: Optional[dict] = None,
        style: Optional[dict] = None,
        image_url: Optional[str] = None,
        children: Optional[List["SlideElement"]] = None,
    ):
        self.id = element_id
        self.type = element_type
        self.content = content
        self.position = position
        self.style = style
        self.image_url = image_url
        self.children = children or []


def extract_slide_elements(page: dict) -> List[SlideElement]:
    """スライドページから要素を抽出"""
    elements: List[SlideElement] = []
    
    page_elements = page.get("pageElements", [])
    for element in page_elements:
        extracted = extract_element(element)
        if extracted:
            elements.append(extracted)
    
    return elements


def extract_element(element: dict) -> Optional[SlideElement]:
    """単一要素を抽出"""
    element_id = element.get("objectId")
    if not element_id:
        return None
    
    # 位置情報を抽出
    transform = element.get("transform", {})
    position = None
    if transform:
        translate_x = transform.get("translateX", {}).get("magnitude", 0) / 9525  # EMU to pixels
        translate_y = transform.get("translateY", {}).get("magnitude", 0) / 9525
        width = transform.get("width", {}).get("magnitude", 0) / 9525
        height = transform.get("height", {}).get("magnitude", 0) / 9525
        position = {
            "x": translate_x,
            "y": translate_y,
            "width": width,
            "height": height,
        }
    
    base_element = SlideElement(
        element_id=element_id,
        element_type="shape",
        position=position,
    )
    
    # テキスト要素
    shape = element.get("shape", {})
    if shape.get("shapeType") == "TEXT_BOX" or shape.get("text"):
        text_content = extract_text_content(shape.get("text", {}))
        return SlideElement(
            element_id=element_id,
            element_type="text",
            content=text_content["text"],
            style=text_content.get("style"),
            position=position,
        )
    
    # 画像要素
    if "image" in element:
        image = element["image"]
        return SlideElement(
            element_id=element_id,
            element_type="image",
            image_url=image.get("contentUrl") or image.get("sourceUrl"),
            position=position,
        )
    
    # 図形要素
    if shape:
        shape_type = shape.get("shapeType")
        if shape_type and shape_type != "TEXT_BOX":
            return SlideElement(
                element_id=element_id,
                element_type="shape",
                content=shape_type,
                position=position,
            )
    
    # テーブル要素
    if "table" in element:
        table = element["table"]
        return SlideElement(
            element_id=element_id,
            element_type="table",
            content=extract_table_content(table),
            position=position,
        )
    
    # グループ要素
    if "elementGroup" in element:
        element_group = element["elementGroup"]
        children = []
        for child in element_group.get("children", []):
            child_element = extract_element(child)
            if child_element:
                children.append(child_element)
        
        return SlideElement(
            element_id=element_id,
            element_type="group",
            children=children,
            position=position,
        )
    
    return base_element


def extract_text_content(text_element: dict) -> dict:
    """テキストコンテンツを抽出"""
    text_elements = text_element.get("textElements", [])
    if not text_elements:
        return {"text": ""}
    
    full_text = ""
    style = None
    
    for text_el in text_elements:
        text_run = text_el.get("textRun", {})
        if text_run:
            full_text += text_run.get("content", "")
            
            text_style = text_run.get("textStyle", {})
            if text_style:
                style = {
                    "fontSize": text_style.get("fontSize", {}).get("magnitude", 0) / 100 if text_style.get("fontSize") else None,
                    "fontFamily": text_style.get("fontFamily"),
                    "color": rgb_to_hex(text_style.get("foregroundColor", {}).get("opaqueColor", {}).get("rgbColor")),
                    "bold": text_style.get("bold"),
                    "italic": text_style.get("italic"),
                }
    
    return {"text": full_text.strip(), "style": style}


def extract_table_content(table: dict) -> str:
    """テーブルコンテンツを抽出"""
    table_rows = table.get("tableRows", [])
    if not table_rows:
        return ""
    
    rows = []
    for row in table_rows:
        table_cells = row.get("tableCells", [])
        cells = []
        for cell in table_cells:
            text_content = extract_text_content(cell.get("text", {}).get("textContent", {}))
            cells.append(text_content["text"] or "")
        rows.append(" | ".join(cells))
    
    return "\n".join(rows)


def rgb_to_hex(rgb: Optional[dict]) -> Optional[str]:
    """RGBカラーをHEXに変換"""
    if not rgb:
        return None
    
    r = round((rgb.get("red", 0) or 0) * 255)
    g = round((rgb.get("green", 0) or 0) * 255)
    b = round((rgb.get("blue", 0) or 0) * 255)
    
    return f"#{r:02x}{g:02x}{b:02x}"

