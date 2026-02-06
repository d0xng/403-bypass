# 403 Bypass Automator

Herramienta automatizada para probar diferentes técnicas de bypass de errores 403 Forbidden en endpoints web.

## Descripción

Este script prueba automáticamente más de 1000 técnicas diferentes de bypass para endpoints que retornan 403 Forbidden, incluyendo:

- **Encoding bypasses**: URL encoding, double encoding, extended encoding
- **Path manipulation**: Trailing slashes, path traversal, semicolons, etc.
- **HTTP methods**: GET, POST, PUT, DELETE, PATCH, OPTIONS, TRACE, CONNECT, y más
- **Header bypasses**: IP spoofing headers, path override headers, host headers
- **Protocol bypasses**: HTTP vs HTTPS
- **Port bypasses**: Headers de puerto
- **Endpath payloads**: Payloads al final del path
- **Midpath payloads**: Payloads insertados en el medio del path

## Requisitos

```bash
pip install requests colorama
```

## Uso

```bash
python 403_bypass_automator.py <URL>
```

### Ejemplo

```bash
python 403_bypass_automator.py https://example.com/api/admin
```

## Output

El script muestra los resultados en formato estilo Nuclei:

- **[BYPASSED]** en verde: Cuando encuentra un bypass exitoso (status 200)
- **[NOT BYPASSED]** en rojo: Cuando el bypass no funcionó (status diferente a 200)

Cada resultado incluye:
- URL probada
- Técnica utilizada
- Status code y tamaño de respuesta
- Información adicional sobre el payload utilizado

## Nota

El script incluye un delay de 3 segundos entre cada petición para evitar bloqueos por rate limiting. Con más de 1000 técnicas de bypass, la ejecución completa puede tardar bastante tiempo.
