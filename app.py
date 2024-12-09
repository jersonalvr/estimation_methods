import streamlit as st
import subprocess
import os
import json
import pandas as pd
import numpy as np
import google.generativeai as genai
import streamlit_lottie as st_lottie

def run_manim(scene_name):
    """
    Ejecuta el script de Manim para generar el video de la escena especificada.
    """
    command = [
        "manim",
        "-pqh",                # Flags para reproducción y alta calidad
        "manim.py",            # Nombre del script de Manim
        scene_name             # Nombre de la clase de la escena
    ]

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def interpretar_p_hat(p_hat):
    """
    Proporciona una interpretación basada en el valor de p_hat.
    """
    if p_hat > 0.6:
        return "La moneda está fuertemente sesgada hacia **caras**."
    elif p_hat < 0.4:
        return "La moneda está fuertemente sesgada hacia **sellos**."
    elif 0.4 <= p_hat <= 0.6:
        return "La moneda es **equilibrada** y no está significativamente sesgada."
    else:
        return "No se pudo determinar una interpretación clara para el valor de p."

# Configuración de la clave de la API de Gemini
key = st.secrets["GEMINIAPI"]["key"]

def interpretar_valores_lse(m, b):
    """
    Proporciona una interpretación basada en los valores de m y b.
    """
    interpretation = f"La pendiente (m) es {m:.2f} y la intersección (b) es {b:.2f}.\n"
    if m > 0:
        interpretation += "Esto indica una relación positiva entre las horas trabajadas y la producción. A medida que aumentan las horas trabajadas, la producción también tiende a aumentar."
    elif m < 0:
        interpretation += "Esto indica una relación negativa entre las horas trabajadas y la producción. A medida que aumentan las horas trabajadas, la producción tiende a disminuir."
    else:
        interpretation += "Esto indica que no hay una relación lineal entre las horas trabajadas y la producción."
    return interpretation

def main():
    st.set_page_config(page_title="Métodos de Estimación", page_icon="📈")
    st.title("Análisis y Aplicación de Métodos de Estimación")

    # Inicialización de session_state
    if 'show_interpretation' not in st.session_state:
        st.session_state.show_interpretation = False
    if 'model_generated' not in st.session_state:
        st.session_state.model_generated = False
    if 'value_explanation' not in st.session_state:
        st.session_state.value_explanation = ""

    st.header("Sección 1: Máxima Verosimilitud (MLE)")
    st.write(r"""
    **Descripción del Problema:**
    
    Un investigador está estudiando una moneda posiblemente sesgada. Realiza 10 lanzamientos y obtiene $“x”$ caras. (Recuerda que $x$ representa la cantidad de caras que obtienes en tu experimento)
    
    **Preguntas:**
    
    1. **Usando el método de máxima verosimilitud:**
       - Estima la probabilidad $p$ de que la moneda caiga en cara.
       - Genera un gráfico que muestre la función de verosimilitud $L(p)$ para $p$ en el intervalo $[0,1]$.
    
    2. **¿Qué implica el valor obtenido para $p$ en términos de la probabilidad de que caiga cara?**
    """)
    COIN = "https://static.videezy.com/system/protected/files/000/031/969/MM009213___MONEY_COIN_007__1080p___phantom___E_Sub_07.mp4"
    st.markdown(f'''
        <video width="100%" autoplay loop muted>
            <source src="{COIN}" type="video/mp4">
            Tu navegador no soporta el elemento de video.
        </video>
    ''', unsafe_allow_html=True)

    # Formulario para la entrada de datos
    with st.form(key='parameters_form'):
        col1, col2 = st.columns(2)
        with col1:
            n = st.number_input("Número de lanzamientos (n)", min_value=1, max_value=1000, value=10, step=1)
        with col2:
            x = st.number_input("Número de caras obtenidas (x)", min_value=0, max_value=n, value=7, step=1)
        submit_button = st.form_submit_button(label='Generar el gráfico ')

    if submit_button:
        try:
            with st.spinner("Generando el gráfico de la función de verosimilitud..."):        
                
                # Calcular \hat{p}
                p_hat = x / n

                # Escribir los parámetros en config.json
                config = {
                    "n": int(n),
                    "x": int(x)
                }

                try:
                    with open("config.json", "w") as config_file:
                        json.dump(config, config_file)
                except Exception as e:
                    st.error(f"Error al escribir el archivo de configuración: {e}")
                    st.stop()

                # Crear los directorios necesarios si no existen
                video_directory = os.path.join("media", "videos", "manim", "1080p60")
                os.makedirs(video_directory, exist_ok=True)

                # Ejecutar Manim para generar el video
                success, message = run_manim("LikelihoodFunction")

                if success:
                    # Ruta al video generado
                    video_path = os.path.join("media", "videos", "manim", "1080p60", "LikelihoodFunction.mp4")

                    if os.path.exists(video_path):
                        st.success("Gráfico de la función de verosimilitud generado exitosamente.")

                        # Reproducir el video
                        video_url = video_path.replace("\\", "/")  # Compatibilidad con Windows
                        st.video(video_url)

                        # Mostrar las fórmulas relevantes utilizando cadenas crudas
                        st.latex(r"L(p) = p^x (1 - p)^{n - x}")
                        st.latex(r"\hat{p} = \frac{x}{n}")

                        # Mostrar el valor calculado de \hat{p}
                        st.subheader(r"Valor Estimado de $\hat{p}$")
                        st.write(f"El valor estimado de $\hat{{p}}$ es: **{p_hat:.4f}**")

                        # Proporcionar una interpretación basada en el valor de \hat{p}
                        interpretacion = interpretar_p_hat(p_hat)
                        st.write("**Interpretación:**")
                        st.write(interpretacion)

                        # Actualizar el estado para indicar que el modelo ha sido generado
                        st.session_state.model_generated = True
                        st.session_state.interpret = False  # Resetear interpretación si se regenera el modelo
                    else:
                        st.error("El video no se encontró. Asegúrate de que Manim generó el video correctamente.")
                        st.text("Salida de Manim:")
                        st.text(message)
                else:
                    st.error("No se pudo generar el video.")
                    st.text("Error de Manim:")
                    st.text(message)

        except Exception as e:
            st.error(f"Error: {e}")

    with st.expander("💡Interpretación del Valor de $p$"):

        st.write("""
        El valor estimado de $p$ representa la probabilidad de que la moneda caiga en cara en cada lanzamiento. Un valor de $p$ cercano a 1 indica que la moneda es fuertemente sesgada hacia las caras, mientras que un valor cercano a 0 indica un sesgo hacia los sellos. Un valor de $(p = 0.5)$ sugiere que la moneda es equilibrada y no está sesgada.
        """)

        st.write("""
        **Fórmula de la estimación de máxima verosimilitud:**
        """)

        st.latex(r"\hat{p} = \frac{x}{n}")

        st.write(r"""
        Donde:
        - $\hat{p}$ es la estimación de máxima verosimilitud para la probabilidad de cara.
        - x es el número de caras obtenidas en los lanzamientos.
        - n es el número total de lanzamientos.
        """)

    st.write("---")  # Línea divisoria

    # Sección 2: Mínimos Cuadrados (LSE)
    st.header("Sección 2: Mínimos Cuadrados (LSE)")
    st.write(r"""
    **Descripción del Problema:**
    
    Un fabricante está analizando la relación entre el número de horas trabajadas y la producción de una máquina. Se obtuvieron los siguientes datos:
    """)
    SUPPLIER = "https://videos.pexels.com/video-files/10095306/10095306-uhd_3840_2160_25fps.mp4"
    st.markdown(f'''
        <video width="100%" autoplay loop muted>
            <source src="{SUPPLIER}" type="video/mp4">
            Tu navegador no soporta el elemento de video.
        </video>
    ''', unsafe_allow_html=True)
    # Datos por defecto
    default_data = {
        'Producción (x)': [1, 2, 3, 4, 5],
        'Horas Trabajadas (y)': [5, 7.5, 10, 11, 12]
    }

    # Opción para usar datos por defecto o personalizados
    data_option = st.radio(
        "Selecciona los datos", 
        ["Datos por Defecto", "Ingresar Datos Personalizados"]
    )

    # Entrada de datos
    if data_option == "Datos por Defecto":
        df = st.data_editor(
            pd.DataFrame(default_data),
            num_rows="dynamic",
            key="regression_data"
        )
    else:
        df = st.data_editor(
            pd.DataFrame(columns=['Producción (x)', 'Horas Trabajadas (y)']),
            num_rows="dynamic",
            key="custom_regression_data"
        )

    # Preguntas y opciones
    st.write("""
    **Preguntas:**
    1. Encuentra la mejor línea de regresión ($y=mx+b$) que minimice el error cuadrado entre los puntos y la línea.
    2. Genera un gráfico que incluya los puntos de datos, la línea de regresión y los errores (distancias entre los puntos y la línea).
    3. Interpreta los valores de $m$ (pendiente) y $b$ (intersección) obtenidos.
    """)

    # Selección de modelo de regresión
    modelo_regresion = st.selectbox(
        "Selecciona el modelo de regresión",
        ["Lineal", "Polinomial (grado 2)", "Polinomial (grado 3)"]
    )

    # Botón para generar el modelo de regresión
    st.markdown("<br>", unsafe_allow_html=True)  # Espacio adicional

    if st.button("Generar modelo de regresión", key="generate_regression"):
        try:
            if df.empty or df.isnull().values.any():
                st.error("Por favor, asegúrate de que no haya celdas vacías en los datos.")
            else:
                # Preparar los datos
                X = np.array(df['Producción (x)'])
                Y = np.array(df['Horas Trabajadas (y)'])
                n = len(X)

                # Seleccionar el modelo de regresión
                if modelo_regresion == "Lineal":
                    grado = 1
                elif modelo_regresion == "Polinomial (grado 2)":
                    grado = 2
                elif modelo_regresion == "Polinomial (grado 3)":
                    grado = 3

                # Ajustar el modelo
                coeficientes = np.polyfit(X, Y, grado)
                polinomio = np.poly1d(coeficientes)
                Y_pred = polinomio(X)

                # Calcular los errores
                errores = Y - Y_pred

                # Guardar los parámetros en config_regression.json
                config_regression = {
                    "X": X.tolist(),
                    "Y": Y.tolist(),
                    "grado": grado,
                    "coeficientes": coeficientes.tolist()
                }

                with open("config_regression.json", "w") as config_file:
                    json.dump(config_regression, config_file)

                # Crear los directorios necesarios si no existen
                video_directory = os.path.join("media", "videos", "manim", "1080p60")
                os.makedirs(video_directory, exist_ok=True)

                # Ejecutar Manim para generar el video de regresión
                success, message = run_manim("RegressionFunction")

                if success:
                    # Ruta al video generado
                    video_path = os.path.join("media", "videos", "manim", "1080p60", "RegressionFunction.mp4")

                    if os.path.exists(video_path):
                        st.success("Modelo de regresión generado exitosamente.")
                        st.session_state.model_generated = True
                        st.session_state.show_interpretation = False
                        # Reproducir el video
                        video_url = video_path.replace("\\", "/")  # Compatibilidad con Windows
                        st.video(video_url)

                        # Mostrar las fórmulas relevantes utilizando cadenas crudas
                        if grado == 1:
                            st.latex(r"y = mx + b")
                        else:
                            # Usar Markdown para saltos de línea
                            coef_list = []
                            for i, coef in enumerate(coeficientes[::-1]):
                                if grado - i == 0:
                                    coef_list.append(f"**Intersección:** {coef:.4f}")
                                else:
                                    coef_list.append(f"**Coeficiente de $x^{{{grado - i}}}$:** {coef:.4f}")
                            coef_text = "<br>".join(coef_list)
                            st.markdown(coef_text, unsafe_allow_html=True)

                        # Mostrar los coeficientes únicamente una vez
                        st.subheader("Valores de los Coeficientes")
                        if grado == 1:
                            m, b = coeficientes
                            st.write(f"""**Pendiente (m):** **{m:.4f}**  
                                         **Intersección (b):** **{b:.4f}**""")
                        else:
                            for i, coef in enumerate(coeficientes[::-1]):
                                if grado - i == 0:
                                    st.write(f"""**Intersección:** **{coef:.4f}**""")
                                else:
                                    st.write(f"""**Coeficiente de $x^{{{grado - i}}}$:** **{coef:.4f}**""")

                        # Almacenar coeficientes y grado en session_state
                        st.session_state.coeficientes = coeficientes
                        st.session_state.grado = grado

                        # Actualizar el estado para indicar que el modelo ha sido generado
                        st.session_state.model_generated = True
                        st.session_state.interpret = False  # Resetear interpretación si se regenera el modelo
                    else:
                        st.error("El video no se encontró. Asegúrate de que Manim generó el video correctamente.")
                        st.text("Salida de Manim:")
                        st.text(message)

                else:
                    st.error("No se pudo generar el video.")
                    st.text("Error de Manim:")
                    st.text(message)

        except Exception as e:
            st.error(f"Error: {e}")

    with st.expander("💡Interpretación de la Regresión Lineal"):

        st.write("""
        La regresión lineal calcula la mejor línea recta que se ajusta a los datos proporcionados minimizando la suma de los errores cuadrados entre los valores observados y los valores predichos por la línea.

        **Fórmulas de la regresión lineal:**
        """)

        st.latex(r"y = mx + b")

        st.write(r"""
        Donde:
        - $m$ es la pendiente de la línea, que indica la tasa de cambio de la producción con respecto a las horas trabajadas.
        - $b$ es la intersección con el eje y, que representa la producción esperada cuando las horas trabajadas son cero.
        """)

        st.write("""
        **Interpretación de los coeficientes:**
        - Una pendiente positiva ($m > 0$) indica que a medida que aumentan las horas trabajadas, la producción también aumenta.
        - Una pendiente negativa ($m < 0$) indica que a medida que aumentan las horas trabajadas, la producción disminuye.
        - Una pendiente de cero ($m = 0$) sugiere que no hay relación lineal entre las horas trabajadas y la producción.
        """)
        # Botón para interpretar los valores (solo visible si el modelo ha sido generado)
        if st.session_state.model_generated:
            st.markdown("<br>", unsafe_allow_html=True)  # Espacio adicional
            show_interpretation = st.button("Interpreta los valores", key="interpret_button")
            if show_interpretation:
                st.session_state.show_interpretation = True
            if st.session_state.show_interpretation:
                try:
                    # Verificar si 'coeficientes' y 'grado' están en session_state
                    if 'coeficientes' not in st.session_state or 'grado' not in st.session_state:
                        st.error("No se encontraron los coeficientes del modelo de regresión.")
                    else:
                        coeficientes = st.session_state.coeficientes
                        grado = st.session_state.grado

                        # Preparar el texto para la generación de contenido
                        if grado == 1:
                            m, b = coeficientes
                            prompt = f"Analiza la regresión lineal obtenida con pendiente m={m:.4f} y intersección b={b:.4f}. Explica qué significan estos valores en el contexto de la relación entre horas trabajadas y producción de la máquina."
                        else:
                            prompt = f"Analiza la regresión polinomial de grado {grado} obtenida con coeficientes {coeficientes}. Explica qué significan estos valores en el contexto de la relación entre horas trabajadas y producción de la máquina."

                        # Configurar Gemini y generar la explicación
                        genai.configure(api_key=key)
                        model = genai.GenerativeModel('gemini-1.5-flash')

                        with st.spinner('Generando explicación...'):
                            response = model.generate_content(prompt)
                            st.session_state.value_explanation = response.text

                        st.markdown("### Explicación Generada por Gemini")
                        st.write(st.session_state.value_explanation)

                        # Cargar y mostrar la animación Lottie
                        def load_lottie_file(filepath: str):
                            with open(filepath, 'r') as f:
                                return json.load(f)

                        # Ruta al archivo JSON de Lottie
                        try:
                            base_dir = os.getcwd()
                            lottie_path = os.path.join(base_dir, "gemini_logo.json")
                            if os.path.exists(lottie_path):
                                gemini_logo = load_lottie_file(lottie_path)

                                # Mostrar la animación Lottie con tamaño pequeño
                                st_lottie.st_lottie(
                                    gemini_logo, 
                                    key='logo', 
                                    height=50,  # Ajusta la altura según tus necesidades
                                    width=50,   # Ajusta el ancho según tus necesidades
                                    loop=True,
                                    quality="low"
                                )
                            else:
                                st.warning("El archivo de animación Lottie no se encontró.")
                        except Exception as e:
                            st.error(f"Error al cargar la animación Lottie: {e}")
                except Exception as e:
                    st.error(f"Error al generar la interpretación: {e}")
if __name__ == "__main__":
    main()
