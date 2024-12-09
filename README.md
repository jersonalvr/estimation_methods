# Proyecto de Visualización Matemática
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://estimationmethods.streamlit.app/)
Este proyecto utiliza Manim para crear visualizaciones de funciones de verosimilitud y regresión. Se incluyen ejemplos de cómo configurar y ejecutar las visualizaciones.

## Requisitos

Asegúrate de tener instalados los siguientes paquetes:

- `streamlit`
- `streamlit_lottie`
- `manim`
- `pandas`
- `numpy`
- `google-generativeai`

Puedes instalar los requisitos utilizando el archivo `requirements.txt`:

```bash
pip install -r requirements.txt
```
Dependencias del Sistema
Además de los paquetes de Python, asegúrate de tener instaladas las siguientes dependencias del sistema:

libcairo2-dev
libpango1.0-dev
libpixman-1-dev
ffmpeg
texlive-full
Puedes instalar estas dependencias en sistemas basados en Debian/Ubuntu con el siguiente comando:

```bash
sudo apt-get install libcairo2-dev libpango1.0-dev libpixman-1-dev ffmpeg texlive-full
```
Archivos de Configuración
El proyecto utiliza archivos de configuración en formato JSON para definir los parámetros de las visualizaciones:

config.json: Parámetros para la función de verosimilitud.
config_regression.json: Parámetros para la función de regresión.
Asegúrate de que estos archivos existan y contengan los parámetros necesarios antes de ejecutar las visualizaciones.

Ejecución
Para ejecutar las visualizaciones, puedes utilizar los siguientes comandos:

```bash
manim -pql manim.py LikelihoodFunction
manim -pql manim.py RegressionFunction
```
Esto generará las animaciones correspondientes para la función de verosimilitud y la función de regresión.

Contribuciones
Las contribuciones son bienvenidas. Si deseas contribuir, por favor abre un issue o envía un pull request.
