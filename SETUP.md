# 🎾 Guía de Configuración - Tennis ML APA

Este documento te guiará paso a paso para configurar el entorno de desarrollo del proyecto.

---

## 📋 Prerequisitos

Antes de empezar, asegúrate de tener instalado:

- **Anaconda** o **Miniconda** ([Descargar aquí](https://docs.conda.io/en/latest/miniconda.html))
- **Git** (para clonar el repositorio)

---

## 🚀 Instalación Paso a Paso

### 1️⃣ Clonar el Repositorio (por ssh)

```bash
git clone git@github.com:Sterrysx/Tennis-ML-APA.git
cd Tennis-ML-APA
```

---

### 2️⃣ Crear el Entorno Virtual con Conda

Crea un entorno virtual llamado `tennis-ml` con Python 3.11:

```bash
conda create -n tennis-ml python=3.11 -y
```

**Explicación:**
- `-n tennis-ml`: Nombre del entorno
- `python=3.11`: Versión de Python
- `-y`: Acepta automáticamente la instalación

---

### 3️⃣ Activar el Entorno Virtual

```bash
conda activate tennis-ml
```

**⚠️ Importante:** Debes activar este entorno **cada vez** que trabajes en el proyecto.

**Verificar que está activado:**
- Tu prompt debería mostrar: `(tennis-ml) $`
- Verifica con: `conda env list` (verás un `*` junto a `tennis-ml`)

---

### 4️⃣ Instalar las Dependencias

Instala todas las librerías necesarias desde el archivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

Este proceso puede tardar varios minutos. Instalará:
- **pandas, numpy**: Manipulación de datos
- **scikit-learn**: Modelos de Machine Learning
- **xgboost**: Gradient Boosting
- **matplotlib, seaborn**: Visualización
- **jupyter, ipykernel**: Notebooks
- **optuna**: Optimización de hiperparámetros
- Y muchas más...

---

### 5️⃣ Configurar Jupyter Notebook con el Entorno

Para que Jupyter reconozca tu entorno virtual:

```bash
python -m ipykernel install --user --name=tennis-ml --display-name="Python (tennis-ml)"
```

**Ahora puedes:**
1. Abrir VS Code o Jupyter Notebook
2. Al abrir un `.ipynb`, seleccionar el kernel **"Python (tennis-ml)"**

---

### 6️⃣ Descargar los Datos (Opcional)

Si necesitas descargar los datos desde cero:

```bash
./pull_data.sh
```

Este script:
- Descarga datos de ATP 2011-2024 desde GitHub (Jeff Sackmann)
- Genera: `pull-data/parsed_data/atp_matches_2011_2024.csv`

**Nota:** Los datos ya están incluidos en `notebooks/data/raw/raw_atp_matches.csv`, por lo que este paso es **opcional**.

---

## 👥 Autores

- Oriol Farrés
- Marc Gil

