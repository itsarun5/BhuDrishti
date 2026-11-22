# 🛰️ BhuDrishti

**Satellite insights for everyone.** Pick a place in Madhya Pradesh and get a simple green / amber / red scorecard for crops, water, urban & green cover, and climate trends, built from satellite data.

Built for **ASTRA 2026** (Earth Observation) by **Team Midnight Maveric (T33)**, ANTERiX Club, VIT Bhopal.

## The problem
Satellite data exists, but farmers, citizens and officers can't use it. BhuDrishti turns it into plain-language answers and clear advice.

## Features
- Choose a district or drop a pin on the map
- Overall health score plus 4 modules: **Crop health · Water · Urban & green · Climate**
- **Citizen view:** simple insight and advice, WhatsApp share
- **Officer view:** NDVI / NDWI / NDBI map layers, trend charts, data provenance, PDF/JSON export

## Tech stack
| Layer | Tools |
|---|---|
| Satellite data | Bhoonidhi, Bhuvan, VEDAS, MOSDAC (ISRO) |
| Processing | Python, NumPy, Rasterio, GeoPandas, scikit-learn |
| Backend | FastAPI / Flask |
| Frontend | React (Vite), Leaflet, Chart.js |
| Deployment | Vercel / Render, GitHub |

## Team
Team Midnight Maveric (T33), ANTERiX Club, VIT Bhopal
