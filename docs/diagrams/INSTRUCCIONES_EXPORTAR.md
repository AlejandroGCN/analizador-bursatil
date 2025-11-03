# 📋 Instrucciones de Exportación

## Archivos Generados

Se han creado los siguientes archivos `.mmd`:

### 1_arquitectura_completa.mmd
**Arquitectura Completa del Sistema**

```
1. Abre: https://mermaid.live/
2. Abre el archivo: docs/diagrams/1_arquitectura_completa.mmd
3. Copia TODO el contenido
4. Pega en Mermaid Live (borra contenido anterior)
5. Click 'Actions' → 'PNG' → Escala 3x
6. Descarga como: 1_arquitectura_completa.png
```

### 2_patrones_diseno.mmd
**Patrones de Diseño**

```
1. Abre: https://mermaid.live/
2. Abre el archivo: docs/diagrams/2_patrones_diseno.mmd
3. Copia TODO el contenido
4. Pega en Mermaid Live (borra contenido anterior)
5. Click 'Actions' → 'PNG' → Escala 3x
6. Descarga como: 2_patrones_diseno.png
```

### 3_flujo_secuencia.mmd
**Flujo de Datos en Secuencia**

```
1. Abre: https://mermaid.live/
2. Abre el archivo: docs/diagrams/3_flujo_secuencia.mmd
3. Copia TODO el contenido
4. Pega en Mermaid Live (borra contenido anterior)
5. Click 'Actions' → 'PNG' → Escala 3x
6. Descarga como: 3_flujo_secuencia.png
```

### 4_jerarquia_clases.mmd
**Jerarquía de Clases**

```
1. Abre: https://mermaid.live/
2. Abre el archivo: docs/diagrams/4_jerarquia_clases.mmd
3. Copia TODO el contenido
4. Pega en Mermaid Live (borra contenido anterior)
5. Click 'Actions' → 'PNG' → Escala 3x
6. Descarga como: 4_jerarquia_clases.png
```

### 5_stack_tecnologico.mmd
**Stack Tecnológico**

```
1. Abre: https://mermaid.live/
2. Abre el archivo: docs/diagrams/5_stack_tecnologico.mmd
3. Copia TODO el contenido
4. Pega en Mermaid Live (borra contenido anterior)
5. Click 'Actions' → 'PNG' → Escala 3x
6. Descarga como: 5_stack_tecnologico.png
```


## ⚡ Atajo Rápido

Para exportar todos de una vez usando CLI (requiere instalación):

```bash
# Instalar mermaid-cli (solo primera vez)
npm install -g @mermaid-js/mermaid-cli

# Exportar todos
for file in docs/diagrams/*.mmd; do
    mmdc -i "$file" -o "${file%.mmd}.png" -w 1920 -s 3
done
```

## 🎯 Prioridad de Exportación

Si tienes poco tiempo, exporta en este orden:

1. ⭐ **1_arquitectura_completa.mmd** - EL MÁS IMPORTANTE
2. 📊 **3_flujo_secuencia.mmd** - Para explicar el flujo
3. 🏛️ **4_jerarquia_clases.mmd** - Para explicar herencias
4. 🎯 **2_patrones_diseno.mmd** - Para explicar patrones
5. 📈 **5_stack_tecnologico.mmd** - Para explicar tecnologías

---

¡Exportación exitosa! 🚀
