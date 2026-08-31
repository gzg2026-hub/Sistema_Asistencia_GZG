import asyncio
import os
from playwright.async_api import async_playwright

async def upload_padron_to_asistencia_parent():
    padron_file = r"c:\Users\GZG Minerales 2026\Desktop\GZG\Sistema_Asistencia_GZG\Padron_Trabajadores_GZG.xlsx"
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            page = await context.new_page()
            
            # Ir a la carpeta AGOSTO
            await page.goto("https://drive.google.com/drive/folders/1YpKPT9uTbWzHguHqJrJMb8U5V3GwnEoU", wait_until="networkidle")
            await asyncio.sleep(2)
            
            # Buscar el elemento del pan de migas "ASISTENCIA" (nivel superior)
            # En la barra de pan de migas de Google Drive
            print("Buscando pan de migas 'ASISTENCIA'...")
            asistencia_link = page.get_by_role("link", name="ASISTENCIA")
            if await asistencia_link.count() > 0:
                await asistencia_link.first.click()
                await asyncio.sleep(3)
                print(f"Navegado a carpeta superior ASISTENCIA. URL actual: {page.url}")
                
                # Subir archivo Padron_Trabajadores_GZG.xlsx en la carpeta ASISTENCIA
                file_input = page.locator('input[type="file"]')
                if await file_input.count() > 0:
                    await file_input.first.set_input_files(padron_file)
                    print("[OK] Archivo Padron_Trabajadores_GZG.xlsx enviado via input a ASISTENCIA")
                    await asyncio.sleep(5)
                else:
                    print("No se encontró input file directo, intentando drag and drop...")
            else:
                print("No se encontró link ASISTENCIA en el pan de migas")
                
            await page.close()
        except Exception as e:
            print(f"Error CDP Playwright: {e}")

if __name__ == "__main__":
    asyncio.run(upload_padron_to_asistencia_parent())
