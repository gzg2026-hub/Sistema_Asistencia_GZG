# Códigos de Arreglo — Sistema de Asistencia GZG
Generado a partir de la sesión de auditoría — 26 de agosto de 2026

Aplica los cambios en el orden en que aparecen. Cada bloque indica el archivo exacto y qué buscar con `Ctrl+F` para ubicar el punto de inserción o reemplazo.

---

## 1. `core/auth.py` — Quitar el bypass de contraseña

**Buscar:** `def verify_password`
**Acción:** reemplazar toda la función por:

```python
def verify_password(password: str, password_hash: str, username: str = "") -> bool:
    """Verifica si la contraseña coincide con el hash almacenado, con tolerancia inteligente para teclados móviles."""
    if not password:
        return False
    p_clean = password.strip()
    if hash_password(p_clean) == password_hash:
        return True
    if not p_clean.endswith('*') and hash_password(p_clean + '*') == password_hash:
        return True
    return False
```

---

## 2. `core/hikvision_downloader.py` — Quitar la contraseña hardcodeada

**Buscar:** `"password": "GzG@ACCESO2026"`
**Acción:** reemplazar la función completa por:

```python
def cargar_config_hikvision():
    """Lee la configuración de IP y credenciales desde config_hikvision.json."""
    config_file = os.path.join(PROJECT_ROOT, "config_hikvision.json")
    defaults = {
        "host": "127.0.0.1",
        "port": 443,
        "scheme": "https",
        "username": "admin",
        "password": ""
    }
    if os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                defaults.update(data)
        except Exception:
            pass
    if not defaults.get("password"):
        print("[HikCentral] ADVERTENCIA: no hay password en config_hikvision.json")
    return defaults
```

**No olvidar:** confirmar que `config_hikvision.json` esté en `.gitignore`, crear ese archivo localmente con la contraseña real, y **cambiar la contraseña en HikCentral** (la vieja quedó expuesta en el repo).

---

## 3. `scripts/gdrive_uploader.py` — Quitar la clave de Google hardcodeada

**Buscar:** `if not creds:\n            try:\n                import json, base64`
**Acción:** borrar ese bloque completo (el que decodifica `_sa_b64`), dejando solo:

```python
        if creds:
            return build("drive", "v3", credentials=creds)
    except Exception as e:
        log_drive(f"Error inicializando Google Drive API: {e}")
    return None
```

**Antes de guardar:** rotar la clave en Google Cloud Console (IAM & Admin → Cuentas de servicio → `gzg-asistencia-uploader@...`) y configurar el bloque `[gcp_service_account]` real en **Secrets** de ambas apps de Streamlit Cloud (`app.py` y `mobile.py` son despliegues separados, cada uno necesita el suyo).

---

## 4. `mobile.py` — Botón "Salir" (arreglo del doble clic)

**Buscar:** `if st.button("🚪 Salir"`
**Acción:** reemplazar el bloque completo del `if` por:

```python
if st.button("🚪 Salir", key="btn_logout_mobile", use_container_width=True):
    _cur_token = st.query_params.get('token', '')
    logout_user()
    st.session_state['authenticated'] = False
    st.session_state['user'] = None
    st.session_state['just_logged_out'] = True
    try:
        eliminar_token_sesion(token=_cur_token, username=username)
    except Exception:
        pass
    try:
        st.query_params.clear()
    except Exception:
        pass
    st.rerun()
```

---

## 5. `mobile.py` — Cambio de contraseña (arreglo del congelamiento)

**Buscar:** `if cambiar_password_usuario(username, new_h):`
**Acción:** reemplazar ese bloque por:

```python
                    if cambiar_password_usuario(username, new_h):
                        try:
                            eliminar_token_sesion(username=username)
                        except Exception:
                            pass
                        if st.session_state.get("user"):
                            st.session_state["user"]["password_hash"] = new_h
                        st.session_state["show_change_pw_box"] = False
                        st.session_state["pw_change_success"] = True
                        st.toast("🎉 ¡Contraseña actualizada exitosamente!", icon="🔑")
                        st.rerun()
```

---

## 6. `mobile.py` — Push notifications (2 cambios pequeños)

**Buscar:** `if (window.parent && window.parent !== window)`
**Acción:** reemplazar esa línea y la de adentro por:

```javascript
if (window.top && window.top !== window) {
  window.top.postMessage({ type: 'GZG_REQUEST_PUSH', vapid_pub: "{vapid_pub}" }, '*');
  return;
}
```

**Buscar:** `window.parent.location.replace(curUrl.toString())` (dentro del listener de `GZG_PUSH_SUB_SUCCESS`)
**Acción:** cambiar por:

```javascript
window.top.location.replace(curUrl.toString());
```

---

## 7. `mobile.py` — CSS anti-parpadeo (llevar el fix de app.py)

**Buscar:** el `<style>` cerca del inicio del archivo (CSS del login/dashboard)
**Acción:** agregar justo después de la apertura `<style>`:

```css
*, *::before, *::after {
    transition: none !important;
    animation: none !important;
}
```

---

## 8. `index.html` (raíz del repo, GitHub Pages) — Nuevo listener de push

**Acción:** dentro del `<script>` que ya tiene el listener de `gzg:ready`, combinar en un solo `addEventListener('message', ...)`:

```javascript
function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) outputArray[i] = rawData.charCodeAt(i);
  return outputArray;
}

window.addEventListener('message', async function(ev) {
  if (ev.data && ev.data.type === 'gzg:ready') {
    showApp();
  }
  if (ev.data && ev.data.type === 'GZG_REQUEST_PUSH') {
    try {
      const perm = await Notification.requestPermission();
      if (perm !== 'granted') return;
      const reg = await navigator.serviceWorker.ready;
      let sub = await reg.pushManager.getSubscription();
      if (!sub) {
        sub = await reg.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: urlBase64ToUint8Array(ev.data.vapid_pub)
        });
      }
      ev.source.postMessage({ type: 'GZG_PUSH_SUB_SUCCESS', sub: JSON.stringify(sub) }, '*');
    } catch (err) {
      console.error('Error suscribiendo push:', err);
    }
  }
});
```

**Importante:** no agregar un segundo `addEventListener` separado — combinar con el que ya existe para `gzg:ready`, tal como se ve arriba.

**El resto de `index.html`** (splash, overlay, iframe, fallback de 18s) queda igual que en el ajuste de carga que ya se implementó.

---

## 9. `data/database.py` — Excel + Drive en segundo plano, sin Git

**Buscar:** `def regenerar_aprobaciones_excel`
**Acción:** reemplazar toda la función (desde `def` hasta el `return False` final) por:

```python
def regenerar_aprobaciones_excel(db_path: str = DB_PATH) -> bool:
    """
    Regenera el Excel de aprobaciones y lo sube a Google Drive, todo en segundo plano.
    El llamador (actualizar_estado_aprobacion) no espera a que esto termine.
    Archivo autorizado: Aprobaciones_GZG_YYYY-MM.xlsx (único archivo de aprobaciones permitido en Drive)
    """
    import threading

    sa_info = None
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "gcp_service_account" in st.secrets:
            sa_info = dict(st.secrets["gcp_service_account"])
    except Exception:
        pass

    def _async_full_regen(p_db, sa):
        try:
            import os, datetime
            import pandas as pd
            from data.exporter import exportar_aprobaciones_excel
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

            conn = get_connection(p_db)
            df_aprob = pd.read_sql_query("SELECT * FROM aprobaciones ORDER BY fecha DESC, id DESC", conn)
            conn.close()

            mes_str = datetime.date.today().strftime('%Y-%m')
            out_path = os.path.join(root_dir, 'downloads', 'data_procesada', f'Aprobaciones_GZG_{mes_str}.xlsx')
            os.makedirs(os.path.dirname(out_path), exist_ok=True)

            ok_local = exportar_aprobaciones_excel(df_aprob, out_path)
            if ok_local and os.path.exists(out_path):
                try:
                    from scripts.gdrive_uploader import subir_archivo_a_gdrive
                    subir_archivo_a_gdrive(out_path, sa_dict=sa)
                except Exception as e_drive:
                    print(f"[Aviso] Subida Drive Aprobaciones: {e_drive}")
        except Exception as e:
            print(f"[Aviso] Error regenerando Excel de aprobaciones: {e}")

    threading.Thread(target=_async_full_regen, args=(db_path, sa_info), daemon=True).start()
    return True
```

**No olvidar:** quitar las 4 líneas de diagnóstico temporal (`🔷🔷🔷` / `◆◆◆`) que se agregaron antes en este mismo archivo para depurar la subida a Drive — ya cumplieron su función.

---

## 10. `scripts/auto_sync_approvals.py` — Reemplazar el archivo entero

```python
"""
auto_sync_approvals.py
======================
Descarga puntual (NO sincronización) del Excel de Aprobaciones desde Google Drive.
Solo LEE ese archivo específico — nunca sube nada desde la PC, así que
archivos de prueba locales nunca se filtran hacia Drive.
"""

import os
import sys
import time
import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from scripts.gdrive_uploader import descargar_archivo_de_gdrive

def log_sync(msg: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [AprobacionesWatch] {msg}", flush=True)

def descargar_aprobaciones_actual():
    mes_str = datetime.date.today().strftime('%Y-%m')
    nombre_archivo = f"Aprobaciones_GZG_{mes_str}.xlsx"
    destino_local = os.path.join(ROOT_DIR, "downloads", "data_procesada", nombre_archivo)
    ok = descargar_archivo_de_gdrive(nombre_archivo, destino_local)
    if ok:
        log_sync(f"{nombre_archivo} actualizado desde Drive.")
    return ok

def sync_cycle(intervalo_segundos: int = 90):
    log_sync("Iniciando descarga periódica de Aprobaciones (solo lectura desde Drive)...")
    while True:
        try:
            descargar_aprobaciones_actual()
        except Exception as e:
            log_sync(f"Aviso: {e}")
        time.sleep(intervalo_segundos)

if __name__ == "__main__":
    sync_cycle(90)
```

---

## Después de aplicar todo

1. Guardar todos los archivos.
2. `git add . && git commit -m "fix: seguridad, sesion limpia, push notifications, sync sin git" && git push origin main`
3. Esperar el redeploy automático de **ambas** apps en Streamlit Cloud (`app.py` y `mobile.py`).
4. Probar en orden: login/logout, cambio de contraseña, aprobar una solicitud (debe sentirse instantáneo), y el botón de activar notificaciones push.
5. Confirmar en Google Drive que `Aprobaciones_GZG_YYYY-MM.xlsx` se actualiza tras cada aprobación.
