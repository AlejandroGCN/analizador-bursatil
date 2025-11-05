# 📊 Cómo Exportar Diagramas Mermaid a Imagen

## 🎯 Diagrama de Clases Completo

El archivo `class_diagram_complete.mmd` contiene el diagrama completo de herencias y dependencias del proyecto.

---

## 🖼️ Métodos para Convertir a Imagen

### Método 1: Mermaid Live Editor (Recomendado - Más Fácil)

1. **Abre el editor online:**
   - Ve a: https://mermaid.live/

2. **Copia el contenido:**
   - Abre `class_diagram_complete.mmd`
   - Copia TODO el contenido (incluyendo los triple backticks con `mermaid`)

3. **Pega en el editor:**
   - Pega en el panel izquierdo del editor
   - Verás el diagrama renderizado a la derecha

4. **Exporta como imagen:**
   - Haz clic en el botón **"Actions"** (esquina superior derecha)
   - Selecciona **"PNG"** o **"SVG"**
   - PNG: Mejor para incluir en documentos
   - SVG: Mejor calidad, escalable

5. **Guarda la imagen:**
   - Guárdala como: `class_diagram_complete.png`
   - Colócala en: `docs/diagrams/`

---

### Método 2: Mermaid CLI (Avanzado)

Si tienes Node.js instalado:

```bash
# Instalar Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# Navegar al directorio
cd "C:\Users\aleja\OneDrive\Documents\MASTER\Practica 1 Monte Carlo\analizador-bursatil\docs\diagrams"

# Convertir a PNG
mmdc -i class_diagram_complete.mmd -o class_diagram_complete.png -w 3000 -H 2500

# O convertir a SVG (mejor calidad)
mmdc -i class_diagram_complete.mmd -o class_diagram_complete.svg
```

---

### Método 3: Extensión de VS Code

Si usas Visual Studio Code:

1. **Instala la extensión:**
   - Busca: "Markdown Preview Mermaid Support"
   - O "Mermaid Chart"

2. **Crea un archivo temporal:**
   - Crea: `temp_diagram.md`
   - Contenido: Copia el contenido de `class_diagram_complete.mmd`

3. **Visualiza:**
   - Abre el preview de Markdown (Ctrl+Shift+V)
   - Click derecho en el diagrama
   - "Save as Image"

---

### Método 4: GitHub (Automático)

GitHub renderiza automáticamente diagramas Mermaid en archivos `.md`:

1. **Crea un archivo Markdown:**
   - Archivo: `CLASS_DIAGRAM.md`
   - Incluye el código Mermaid

2. **Sube a GitHub:**
   - GitHub lo renderizará automáticamente

3. **Captura de pantalla:**
   - Abre el archivo en GitHub
   - Haz captura de pantalla del diagrama renderizado
   - O usa herramienta como "Full Page Screen Capture"

---

## 📐 Configuración Recomendada para Exportar

### Para PNG (presentaciones/documentos):
```bash
mmdc -i class_diagram_complete.mmd -o class_diagram_complete.png \
  --width 3000 \
  --height 2500 \
  --backgroundColor white \
  --theme default
```

### Para SVG (web/documentación):
```bash
mmdc -i class_diagram_complete.mmd -o class_diagram_complete.svg \
  --theme default
```

---

## 🎨 Ajustar Tamaño/Calidad

Si el diagrama se ve muy pequeño o grande:

**En Mermaid Live:**
- Usa el zoom (+/-) antes de exportar
- Exporta en resolución alta

**En CLI:**
- Ajusta `--width` y `--height`
- Ejemplo para alta resolución: `-w 4000 -H 3000`

---

## ✅ Checklist para Incluir en GitHub

- [ ] Exportar `class_diagram_complete.mmd` a PNG
- [ ] Guardar como: `docs/diagrams/class_diagram_complete.png`
- [ ] Añadir al repositorio: `git add docs/diagrams/class_diagram_complete.png`
- [ ] Commit: `git commit -m "docs: Add complete class diagram image"`
- [ ] Push: `git push`
- [ ] Referenciar en README.md:
  ```markdown
  ## Diagrama de Clases
  ![Diagrama de Clases](docs/diagrams/class_diagram_complete.png)
  ```

---

## 🖼️ Resolución Recomendada

| Uso | Resolución | Formato |
|-----|------------|---------|
| Documentación | 3000x2500px | PNG |
| Presentación | 4000x3000px | PNG |
| Web | Cualquiera | SVG |
| Impresión | 5000x4000px | PNG/SVG |

---

## 💡 Tips

1. **Usa PNG para el video** - Se ve mejor en presentaciones
2. **Guarda ambos formatos** (PNG y SVG) si es posible
3. **Fondo blanco** - Mejor contraste para impresión/presentación
4. **Alta resolución** - Mínimo 3000px de ancho para claridad

---

## 🆘 Si Tienes Problemas

### El diagrama no se renderiza:
- Verifica que los triple backticks incluyan `mermaid`
- Comprueba que no haya errores de sintaxis

### Imagen muy pequeña:
- Aumenta la resolución (width/height)
- O usa SVG que es escalable

### Colores no se ven bien:
- Cambia el tema: `--theme default`, `--theme dark`, `--theme forest`

---

**Recomendación Final:** Usa **Mermaid Live Editor** (Método 1) - Es el más rápido y fácil. ✨

