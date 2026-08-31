import asyncio
from playwright.async_api import async_playwright

async def get_breadcrumbs():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            page = await context.new_page()
            
            await page.goto("https://drive.google.com/drive/folders/1YpKPT9uTbWzHguHqJrJMb8U5V3GwnEoU", wait_until="networkidle")
            await asyncio.sleep(2)
            
            # Imprimir todos los botones y links en la barra de navegación
            links = await page.locator("a, button").all()
            for l in links:
                txt = (await l.inner_text()).strip()
                href = await l.get_attribute("href")
                if "ASISTENCIA" in txt.upper() or "CONECTIVIDAD" in txt.upper():
                    print(f"Text: '{txt}' | Href: {href}")
            
            await page.close()
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    asyncio.run(get_breadcrumbs())
