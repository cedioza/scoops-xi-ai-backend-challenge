# Guía de Uso de la API - Scoops XI AI Backend

Esta guía detalla cómo interactuar con los endpoints del servicio utilizando `curl`. Todos los endpoints de análisis soportan filtrado opcional por fecha.

## 1. Ingesta de Feedback

**Endpoint**: `POST /api/v1/feedback`

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/feedback" \
     -H "Content-Type: application/json" \
     -d '{
           "date": "2025-11-20",
           "nps": 10,
           "csat": 5,
           "ces": 1,
           "comment": "La comida estuvo increíble y el servicio fue muy rápido."
         }'
```

---

## 2. Overview de Experiencia

**Endpoint**: `GET /api/v1/insights/overview`
**Parámetros**: `start_date` (opcional), `end_date` (opcional)

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/insights/overview?start_date=2025-11-01&end_date=2025-11-30"
```

---

## 3. Insights por Indicador (NPS, CSAT, CES)

**Endpoints**: 
- `GET /api/v1/insights/nps`
- `GET /api/v1/insights/csat`
- `GET /api/v1/insights/ces`

**Ejemplo NPS**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/insights/nps"
```

**Ejemplo CSAT con filtro**:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/insights/csat?start_date=2025-12-01"
```

---

## 4. Drivers (Positivos y Negativos)

**Endpoint**: `GET /api/v1/insights/drivers`

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/insights/drivers"
```

---

## 5. Tópicos Principales

**Endpoint**: `GET /api/v1/insights/topics`

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/insights/topics"
```

---

## 6. Segmentos Críticos

**Endpoint**: `GET /api/v1/insights/segments`

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/insights/segments"
```

---

## 7. Planes de Mejora

**Endpoint**: `GET /api/v1/insights/action-plans`

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/insights/action-plans"
```

---

## Notas Técnicas
- **Formato de Fecha**: `YYYY-MM-DD`.
- **Cálculos**: Se realizan en tiempo real sobre la base de datos de 100 registros.
- **IA**: La narrativa es generada por OpenAI basándose en los resultados determinísticos previos.
