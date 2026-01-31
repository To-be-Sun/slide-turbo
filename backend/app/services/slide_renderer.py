from playwright.async_api import async_playwright
from app.types import SlideData
from typing import List
import base64


async def render_slides_from_html(html: str) -> List[SlideData]:
    """HTMLからスライドを画像として描画"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 16:9のアスペクト比で設定
        await page.set_viewport_size({"width": 1920, "height": 1080})
        
        # HTMLを読み込み
        await page.set_content(html, wait_until="networkidle")
        
        # 各スライドを抽出して画像化
        slides: List[SlideData] = []
        slide_wrappers = await page.query_selector_all(".slide-wrapper")
        
        for i, slide_wrapper in enumerate(slide_wrappers):
            # スライドのHTMLを取得
            slide_html = await slide_wrapper.inner_html()
            
            # スライドを画像としてキャプチャ
            screenshot = await slide_wrapper.screenshot(type="png")
            
            # Base64エンコード
            image_base64 = base64.b64encode(screenshot).decode("utf-8")
            image_url = f"data:image/png;base64,{image_base64}"
            
            slides.append(
                SlideData(
                    slide_index=i,
                    html=slide_html,
                    image_url=image_url,
                )
            )
        
        await browser.close()
        return slides


async def render_single_slide(html: str, slide_index: int) -> str:
    """単一スライドを画像として描画"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.set_viewport_size({"width": 1920, "height": 1080})
        await page.set_content(html, wait_until="networkidle")
        
        slide_element = await page.query_selector(f'.slide-wrapper[data-slide="{slide_index}"]')
        if not slide_element:
            raise ValueError(f"Slide {slide_index} not found")
        
        screenshot = await slide_element.screenshot(type="png")
        return base64.b64encode(screenshot).decode("utf-8")


async def render_slides_to_pdf(html: str, output_path: str) -> None:
    """HTMLをPDFとして出力"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.set_viewport_size({"width": 1920, "height": 1080})
        await page.set_content(html, wait_until="networkidle")
        
        await page.pdf(
            path=output_path,
            format="A4",
            landscape=True,
            print_background=True,
        )
        
        await browser.close()

