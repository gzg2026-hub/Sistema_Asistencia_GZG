# 🌐 GUÍA DE DESPLIEGUE EN LA NUBE GRATUITA - GZG MINERALES PERU S.R.L.

Esta guía paso a paso te explica cómo publicar el **Sistema de Control de Asistencia GZG** en **Streamlit Community Cloud** (servidor 100% gratuito) para que cualquier persona autorizada (Superintendente, Supervisores, Administración) pueda ingresar desde cualquier computadora, teléfono o tablet mediante un enlace web.

---

## 📌 Requisitos Previos (Única vez)

1. Una cuenta gratuita en **GitHub** ([github.com](https://github.com)).
2. Una cuenta gratuita en **Streamlit Community Cloud** ([share.streamlit.io](https://share.streamlit.io)).

---

## 🚀 PASO 1: Subir el Proyecto a GitHub

1. Ingresa a tu cuenta de GitHub y haz clic en **New Repository** (Nuevo Repositorio).
2. Nombre del repositorio: `Sistema_Asistencia_GZG`.
3. Selecciona si deseas que sea **Public** (Público) o **Private** (Privado) y haz clic en **Create repository**.
4. En tu computadora, abre la terminal o la consola de Git dentro de la carpeta del proyecto y ejecuta:

```bash
git init
git add .
git commit -m "Versión 1.0 Sistema de Asistencia GZG con RBAC y Aprobaciones"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/Sistema_Asistencia_GZG.git
git push -u origin main
```

---

## ☁️ PASO 2: Publicar en Streamlit Community Cloud (Servidor Gratuito)

1. Inicia sesión en **[share.streamlit.io](https://share.streamlit.io)** usando tu cuenta de GitHub.
2. Haz clic en el botón azul **"Create App"** (o **"New app"**).
3. Completa los 3 datos principales:
   - **Repository**: `TU_USUARIO/Sistema_Asistencia_GZG`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. Haz clic en **"Deploy!"**.

¡Listo! En menos de 2 minutos se compilará tu aplicación y obtendrás un enlace web público tipo:
`https://gzg-asistencia.streamlit.app`

---

## 🔐 PASO 3: Usuarios de Acceso por Defecto (RBAC)

Una vez ingreses al enlace de tu aplicación en la nube, el sistema te solicitará **Usuario** y **Contraseña**.

| Usuario | Contraseña | Rol / Permisos | Área Asignada |
| :--- | :--- | :--- | :--- |
| **`raul.espinoza`** | `gzg2026*` | 👑 **Gerente General** (Aprobación ejecutiva global) | `TODAS` |
| **`jhon.alva`** | `gzg2026*` | 🏬 **Gerente de Planta** (Aprobación ejecutiva de planta/operaciones) | `TODAS` |
| **`carlos.mendoza`** | `gzg2026*` | 🏛️ **Superintendente de Mina** (Aprobación general operacional) | `TODAS` |
| **`manuel.benitez`** | `gzg2026*` | 👷 **Jefe de Operaciones** (Validación de su área) | `OPER&MTTO` |
| **`javier.delariva`** | `gzg2026*` | 👷 **Supervisor de Jefatura** (Validación de su área) | `JEFATURA` |
| **`admin`** | `gzg2026*` | 💼 **Administración RRHH** (Control total, usuarios, cargas, exportación) | `TODAS` |

---

> 💡 **Nota**: Desde el usuario `admin`, puedes ir a la pestaña **👥 Gestión de Usuarios** para crear nuevos usuarios con sus contraseñas personalizadas.
