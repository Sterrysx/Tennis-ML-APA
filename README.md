# 🎾 Tennis Match Prediction - Machine Learning Project

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)

> **Predicción de Ganadores en Partidos de Tenis ATP usando Machine Learning Avanzado**

Proyecto de Aprendizaje Automático (APA) - Q1 2025-26  
**Autores:** Oriol Farrés & Marc Gil

---

## 📖 Descripción del Proyecto

Este proyecto desarrolla un **sistema completo de predicción de partidos de tenis** del circuito ATP masculino utilizando técnicas avanzadas de Machine Learning. A partir de datos históricos de 2011-2024 (39,542 partidos), construimos modelos predictivos capaces de superar a sistemas profesionales como **IBM Watson** en torneos específicos.

### 🎯 Objetivos Principales

1. **Predicción binaria**: ¿Quién ganará el partido? (Player 1 vs Player 2)
2. **Feature Engineering riguroso**: Creación de 80+ variables predictivas
3. **Validación temporal**: TimeSeriesSplit para evitar data leakage
4. **Benchmarking profesional**: Comparación con IBM Watson en Roland Garros 2024

---

## 🏆 Resultados Destacados

| Métrica | Valor | Contexto |
|---------|-------|----------|
| **Best CV Score** | **70.65%** | XGBoost con Optuna (2011-2020) |
| **Test Score** | **69.8%** | Generalización en datos 2021-2024 |
| **Roland Garros 2024** | **80%** | Walk-forward validation ronda a ronda |
| **IBM Watson Benchmark** | ~70% | Nuestro modelo supera en Grand Slams |

### 📊 Modelos Implementados

- ✅ **Lineales**: Logistic Regression, Linear SVM, K-Nearest Neighbors
- ✅ **No Lineales**: Random Forest, XGBoost, Neural Networks (MLP)
- ✅ **Ensemble**: Voting Classifier, Stacking Classifier
- ✅ **Optimización**: Optuna para hyperparameter tuning (250+ trials por modelo)

---

## 🚀 Cómo Ejecutar el Proyecto

### 📋 Requisitos del Sistema

- **OS**: Windows/Linux/MacOS
- **RAM**: Mínimo 16GB (Recomendado: 32GB + 20GB swap)
- **GPU**: Opcional (XGBoost puede usar CUDA)
- **Tiempo estimado**: ~3 horas en HP Omen 16 (i7, 32GB RAM, RTX 3060)

### 1️⃣ Configuración Inicial

Sigue la [Guía de Configuración](SETUP.md) para instalar dependencias:

```bash
# Clonar repositorio
git clone git@github.com:Sterrysx/Tennis-ML-APA.git
cd Tennis-ML-APA

# Crear entorno virtual
conda create -n tennis-ml python=3.11 -y
conda activate tennis-ml

# Instalar dependencias
pip install -r requirements.txt

# También se puede crear el entorno virtual siguiendo las instrucciones de SETUP.md

# Configurar kernel de Jupyter
python -m ipykernel install --user --name=tennis-ml --display-name="Python (tennis-ml)"
```

### 2️⃣ Ejecución Secuencial de Notebooks

**Orden obligatorio:**

```bash
# OPCIONAL: Descargar datos desde cero (ya incluidos en el repo)
./pull_data.sh

# 1. Preprocesado (30-60 min)
jupyter notebook notebooks/01_preprocesado.ipynb

# 2. Modelado y Evaluación (2-4 horas)
jupyter notebook notebooks/02_ajuste_y_conclusiones.ipynb

# 3. Benchmarking Roland Garros (15-30 min)
jupyter notebook notebooks/03_extra_IBM.ipynb
```

### ⚙️ Configuración de Recursos

Si tienes **memoria limitada**, ajusta estos parámetros en los notebooks:

```python
# En 02_ajuste_y_conclusiones.ipynb

# Reducir trials de Optuna
n_iter=50  # En lugar de 250-500

# Reducir cores usados
n_jobs=4   # En lugar de -1 (todos los cores)
```

---

## 📂 Estructura del Proyecto

```
Tennis-ML-APA/
│
├── notebooks/                      # 📓 Jupyter Notebooks principales
│   ├── 00_preamble.ipynb          # Introducción y contexto
│   ├── 01_preprocesado.ipynb      # Limpieza y feature engineering
│   ├── 02_ajuste_y_conclusiones.ipynb  # Modelos ML y evaluación
│   ├── 03_extra_IBM.ipynb         # Benchmarking Roland Garros
│   └── data/
│       ├── raw/                    # Datos originales
│       │   └── raw_atp_matches.csv
│       ├── clean/                  # Datos procesados
│       │   ├── atp_matches_train.parquet
│       │   ├── atp_matches_test.parquet
│       │   └── ibm.parquet
│       └── ibm/                    # Roland Garros 2024 splits
│           ├── train_step_1_R128.parquet
│           ├── val_step_1_R128.parquet
│           └── ...
│
├── pull-data/                      # 📥 Scripts de descarga de datos
│   ├── atp_matches/               # CSVs originales por año
│   │   ├── atp_matches_2011.csv
│   │   ├── ...
│   │   └── atp_matches_2024.csv
│   ├── parsed_data/               # Datos intermedios
│   │   └── atp_matches_2011_2024.csv
│   └── src/                       # Scripts Python
│       ├── 01_download_data.py
│       ├── 02_merge.py
│
├── requirements.txt                # 📦 Dependencias Python
├── pull_data.sh                   # 🔧 Script de descarga automática
├── SETUP.md                       # 📖 Guía de instalación
└── README.md                      # 📘 Este archivo
```

---

## 🧪 Metodología Técnica

### 🔬 Feature Engineering (80+ Variables)

#### **Características Temporales**
- **ELO Rating**: Sistema estándar de ajedrez adaptado a tenis
  - ELO Global (`elo`)
  - ELO por Superficie (`elo_surface`: Clay/Grass/Hard)
  - ELO Blended: `(elo + elo_surface) / 2`
  - **Margin of Victory (MoV)**: Multiplicador basado en diferencia de juegos
    - Fórmula: `K * log(game_diff + 1) * 0.6`
    - Ejemplo: Victoria 6-0, 6-0 → Multiplicador ~2.5x

#### **Estadísticas Bayesianas (Suavizado C=10)**
Para cada ventana temporal (last_1, last_5, last_10, lifetime):
- `win_rate`: Ratio de victorias
- `ace_pct`: Porcentaje de aces
- `df_pct`: Porcentaje de dobles faltas
- `1st_won_pct`: Efectividad primer servicio
- `bp_save_pct`: Salvamento de break points
- `tb_rate`: Frecuencia de tiebreaks
- `tb_won_pct`: Victorias en tiebreaks

**Lógica de Rookies vs Veteranos:**
- Rookies (ranking > 200 en primera aparición): Imputación conservadora
- Veteranos (ranking < 200): Suavizado Bayesiano hasta 10 partidos

#### **Variables Contextuales**
- `h2h`: Head-to-Head histórico (victorias previas)
- `is_seeded`: ¿Es cabeza de serie?
- `is_first_match`: ¿Es su debut profesional? (con filtro de veteranos)
- `days_since`: Días desde último partido (detecta lesiones si > 90 días)
- `diff_*`: Diferencias entre jugadores (rank, elo, h2h, stats...)

### 🎯 Validación sin Data Leakage

#### **Temporal Split Estricto**
```python
# Train: 2011-2020 (70% - 25,125 partidos)
# Test:  2021-2024 (30% - 10,921 partidos)
```

#### **TimeSeriesSplit para CV**
```python
from sklearn.model_selection import TimeSeriesSplit

tscv = TimeSeriesSplit(n_splits=5)
# Cada fold respeta el orden cronológico
# Fold 1: Train [2011-2014] → Val [2015]
# Fold 2: Train [2011-2016] → Val [2017]
# ...
```

#### **Garantía de No-Leakage**
- Todas las features históricas usan `.shift(1)` en pandas
- H2H se calcula ANTES de actualizar el registro
- ELO pre-partido se guarda ANTES de aplicar el delta
- Variables in-match eliminadas: `ace`, `df`, `svpt`, `minutes`, `score`

### 🤖 Optimización con Optuna

**Hyperparameter Tuning Bayesiano:**
- **Tree-Based Optimization**: Optuna usa TPE (Tree-structured Parzen Estimator)
- **Early Stopping**: Pruning automático de trials no prometedores
- **Distribuciones Continuas**: FloatDistribution con escala logarítmica

**Ejemplo XGBoost:**
```python
param_dist_xgb = {
    'n_estimators': IntDistribution(100, 600),
    'learning_rate': FloatDistribution(0.005, 0.3, log=True),
    'max_depth': IntDistribution(3, 10),
    'subsample': FloatDistribution(0.5, 1.0),
    'gamma': FloatDistribution(0, 5.0),
    'reg_alpha': FloatDistribution(1e-8, 10.0, log=True),
}
```

---

## 📊 Análisis de Resultados

### 🏅 Ranking de Modelos (por CV Score)

| Posición | Modelo | CV Score | Test Score | Diferencia | AUC |
|----------|--------|----------|------------|------------|-----|
| 🥇 1º | **XGBoost** | **70.65%** | 69.8% | +0.85% | 0.780 |
| 🥈 2º | Stacking Ensemble | 70.50% | 69.5% | +1.00% | 0.775 |
| 🥉 3º | Voting Ensemble | 70.33% | 69.3% | +1.03% | 0.772 |
| 4º | MLP Neural Network | 69.85% | 68.9% | +0.95% | 0.765 |
| 5º | SVM con Kernel | 69.94% | 69.1% | +0.84% | 0.768 |
| 6º | Random Forest | 69.60% | 68.7% | +0.90% | 0.760 |
| 7º | Linear SVM | 68.02% | 67.5% | +0.52% | 0.745 |
| 8º | Logistic Regression | 68.19% | 67.8% | +0.39% | 0.748 |
| 9º | K-Nearest Neighbors | 67.73% | 67.2% | +0.53% | 0.742 |

### 💡 Insights Clave

1. **XGBoost domina** gracias a su capacidad de capturar interacciones no lineales
2. **Ensemble Methods** mejoran marginalmente pero añaden complejidad computacional
3. **Baja diferencia CV-Test** (~0.5-1%) indica **NO overfitting**
4. **Modelos lineales** alcanzan ~68% (muy respetable para un problema tan complejo)

### 🎾 Variables Más Importantes (XGBoost)

Top 10 Features por Gain:
1. `diff_elo_blend` - Diferencia de ELO combinado (global + superficie)
2. `diff_rank` - Diferencia de ranking ATP
3. `diff_win_rate_last_10` - Forma reciente (últimos 10 partidos)
4. `diff_elo_surface` - Diferencia de ELO específico de superficie
5. `diff_h2h` - Head-to-Head histórico
6. `diff_1st_won_pct_lifetime` - Efectividad primer servicio (carrera)
7. `diff_bp_save_pct_last_5` - Salvamento de BPs (últimos 5 partidos)
8. `diff_days_since` - Diferencia de inactividad (frescura)
9. `diff_ace_pct_last_10` - Potencia al servicio reciente
10. `diff_tb_won_pct_lifetime` - Clutch mental en tiebreaks

---

## 🔬 Experimento Roland Garros 2024

### 🎯 Objetivo
Validar el modelo en condiciones **real-world** contra el predictor oficial de IBM Watson.

### 📈 Resultados por Ronda

| Ronda | Partidos | Accuracy | Confianza Media | Upsets Detectados |
|-------|----------|----------|-----------------|-------------------|
| R128 | 64 | 75.0% | 0.68 | 16 |
| R64 | 32 | 78.1% | 0.71 | 7 |
| R32 | 16 | 81.3% | 0.74 | 3 |
| R16 | 8 | 75.0% | 0.69 | 2 |
| QF | 4 | 100% | 0.81 | 0 |
| SF | 2 | 100% | 0.85 | 0 |
| F | 1 | 100% | 0.58 | 0 (Alcaraz vs Zverev) |
| **TOTAL** | **127** | **~80%** | **0.72** | **28** |

### 📊 Análisis

**¿Por qué 80% en RG vs 70% CV general?**

1. **Grand Slams son más predecibles**
   - Top 32 seeded (protección de favoritos)
   - Best-of-5 sets (reduce varianza)
   - Motivación máxima (reduce upsets)

2. **Clay-specific features brillan**
   - `elo_surface` captura especialización en tierra
   - Roland Garros = Torneo más predecible en clay

3. **Walk-forward learning**
   - Modelo se adapta partido a partido
   - Incorpora forma del torneo en tiempo real

4. **Varianza estadística**
   - 127 partidos vs 25,000 de CV (muestra pequeña)
   - Intervalo de confianza: [75%-85%] es razonable

**Comparación con IBM Watson:**
- IBM Watson: ~70% reported accuracy
- Nuestro modelo: ~80% en Roland Garros
- **Ventaja**: +10% en Grand Slams específicos

---

## 📈 Métricas de Rendimiento

### ⏱️ Tiempos de Ejecución (HP Omen 16)

**Especificaciones de prueba:**
- CPU: Intel i7-11800H (8 cores)
- RAM: 32GB DDR4 + 20GB swap
- GPU: NVIDIA RTX 3060 (6GB VRAM - no usado por XGBoost CPU)
- SSD: NVMe Gen4

| Notebook | Tiempo | CPU Uso | RAM Pico | Nota |
|----------|--------|---------|----------|------|
| 00_preamble | ~1 min | 20% | 2GB | Carga inicial |
| 01_preprocesado | 30-60 min | 90% | 8GB | Feature engineering intensivo |
| 02_ajuste_y_conclusiones | 2-4 horas | 95% | 12GB | Optuna + múltiples modelos |
| 03_extra_IBM | 15-30 min | 80% | 6GB | Walk-forward RG 2024 |
| **TOTAL** | **~3-5 horas** | - | - | Ejecución completa |

### 💾 Espacio en Disco

- **Datos raw**: ~11 MB (`raw_atp_matches.csv`)
- **Datos procesados**: ~5 MB (parquet files)
- **Modelos guardados**: ~200 MB (pipelines con preprocesadores)
- **Notebooks ejecutados**: ~50 MB (con outputs)
- **Total proyecto**: ~300 MB


---

## 📚 Referencias y Fuentes de Datos

### 📊 Datos

- **Jeff Sackmann** - tennis_atp repository  
  GitHub: [JeffSackmann/tennis_atp](https://github.com/JeffSackmann/tennis_atp)  
  License: CC BY-NC-SA 4.0

### 🏆 Benchmarks

- **IBM Watson Tennis**: Predictor oficial de Grand Slams
  - [IBM Sports & Entertainment](https://www.ibm.com/sports)
  - Accuracy reportado: ~70% en Grand Slams

---

**Última actualización:** Enero 2026  
