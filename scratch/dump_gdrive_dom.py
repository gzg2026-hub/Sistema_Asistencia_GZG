import asyncio
from playwright.async_api import async_playwright

async def dump_dom():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            page = await context.new_page()
            
            await page.goto("https://drive.google.com/drive/folders/1YpKPT9uTbWzHguHqJrJMb8U5V3GwnEoU", wait_until="networkidle")
            await asyncio.sleep(3)
            
            # Guardar captura de pantalla
            screenshot_path = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\scratch\gdrive_page.png"
            await page.screenshot(path=screenshot_path)
            print(f"Captura guardada en: {screenshot_path}")
            
            # Buscar todos los data-id o hrefs
            content = await page.content()
            import re
            folder_ids = re.findall(r'drive/folders/([a-zA-Z0-9_-]+)', content)
            print("Folder IDs encontrados en la página:", set(folder_ids))
            
            await page.close()
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    asyncio.run(dump_dom())
