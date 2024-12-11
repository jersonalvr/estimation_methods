import streamlit as st
import subprocess
import os
import json
import pandas as pd
import numpy as np
import google.generativeai as genai
import streamlit_lottie as st_lottie
import random

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

def get_funny_spinner_text(section):
    """Generate humorous spinner texts for different sections."""
    if section == "mle":
        mle_spinners = [
            "Descifrando los misterios cuánticos de la moneda...",
            "Interrogando a cada átomo de la moneda...",
            "Haciendo que la física cuántica haga horas extras...",
            "Consultando con el espíritu de Isaac Newton...",
            "Realizando magia estadística mientras tomas un café...",
            "Desatando el caos probabilístico...",
            "Haciendo que las leyes de la probabilidad tiemblen...",
        ]
        return random.choice(mle_spinners)
    
    elif section == "regression":
        regression_spinners = [
            "Desentrañando ecuaciones más complicadas que tu vida sentimental...",
            "Negociando con los coeficientes para que revelen sus secretos...",
            "Haciendo que las matemáticas lloren de la emoción...",
            "Convirtiendo datos en sabiduría, un píxel a la vez...",
            "Obligando a las líneas de regresión a contar su historia...",
            "Haciendo que los puntos de datos bailen un vals matemático...",
            "Descifrando ecuaciones más profundas que un agujero negro...",
        ]
        return random.choice(regression_spinners)

def main():
    st.set_page_config(page_title="Métodos de Estimación", page_icon="📈")
    st.title("Análisis y Aplicación de Métodos de Estimación")

    # Inicialización de session_state
    if 'show_mle_interpretation' not in st.session_state:
        st.session_state.show_mle_interpretation = False
    if 'show_regression_interpretation' not in st.session_state:
        st.session_state.show_regression_interpretation = False
    if 'mle_model_generated' not in st.session_state:
        st.session_state.mle_model_generated = False
    if 'regression_model_generated' not in st.session_state:
        st.session_state.regression_model_generated = False
    if 'x_value' not in st.session_state:
        st.session_state.x_value = None
    if 'n_value' not in st.session_state:
        st.session_state.n_value = None
    if 'regression_type' not in st.session_state:
        st.session_state.regression_type = "Lineal"
    if 'regression_coeficientes' not in st.session_state:
        st.session_state.regression_coeficientes = None

    # Configuración de la clave de la API de Gemini
    key = st.secrets["GEMINIAPI"]["key"]

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
            with st.spinner(get_funny_spinner_text("mle")):        
                
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

                st.session_state.x_value = x
                st.session_state.n_value = n
                st.session_state.mle_model_generated = True

        except Exception as e:
            st.error(f"Error: {e}")

    with st.expander("💡Interpretación del Valor de $p$"):
        if not st.session_state.mle_model_generated:
            st.warning("Primero genera el gráfico de la función de verosimilitud.")
        else:
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

            if st.button("Generar Interpretación Avanzada", key="mle_interpret_btn"):
                try:
                    genai.configure(api_key=key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    prompt = f"""Analiza el experimento de lanzamiento de moneda con {st.session_state.n_value} lanzamientos y {st.session_state.x_value} caras. 
                    Proporciona una interpretación detallada del valor estimado de p y su significado estadístico. 
                    Explica qué implica este resultado sobre la naturaleza de la moneda."""
                    
                    with st.spinner(get_funny_spinner_text("mle")):
                        response = model.generate_content(prompt)
                        st.write(response.text)
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
                    st.error(f"Error al generar interpretación: {e}")

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
    st.session_state.regression_type = modelo_regresion

    # Botón para generar el modelo de regresión
    if st.button("Generar modelo de regresión", key="generate_regression"):
        with st.spinner(get_funny_spinner_text("regression")):
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

                    st.session_state.regression_coeficientes = coeficientes.tolist()
                    st.session_state.regression_grado = grado
                    st.session_state.regression_model_generated = True
                    st.session_state.regression_type = modelo_regresion
                    
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

    # Regression Interpretation Expander
    expander_title = "💡Interpretación de la Regresión Lineal" if st.session_state.regression_type == "Lineal" else f"💡Interpretación de la Regresión Polinomial (Grado {2 if st.session_state.regression_type == 'Polinomial (grado 2)' else 3})"
    
    with st.expander(expander_title):
        if not st.session_state.regression_model_generated:
            st.warning("Primero genera el modelo de regresión.")
        else:
            st.write("""
            La regresión {} calcula la mejor {} que se ajusta a los datos proporcionados minimizando la suma de los errores cuadrados entre los valores observados y los valores predichos.
            """.format(
                "lineal" if st.session_state.regression_type == "Lineal" else "polinomial", 
                "línea recta" if st.session_state.regression_type == "Lineal" else "curva polinomial"
            ))

            # Gemini Interpretation Button (Only for Regression)
            if st.button("Generar Interpretación Avanzada", key="regression_interpret_btn"):
                try:
                    genai.configure(api_key=key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    # Prepare the prompt based on regression type
                    if st.session_state.regression_coeficientes is not None:
                        coeficientes = st.session_state.regression_coeficientes
                        grado = 1 if st.session_state.regression_type == "Lineal" else (2 if st.session_state.regression_type == "Polinomial (grado 2)" else 3)
                        
                        prompt = f"""Analiza la regresión {'lineal' if grado == 1 else f'polinomial de grado {grado}'} con los siguientes coeficientes: {coeficientes}. 
                        Proporciona una interpretación detallada de estos coeficientes en el contexto de la relación entre variables."""
                        
                        with st.spinner(get_funny_spinner_text("regression")):
                            response = model.generate_content(prompt)
                            st.write(response.text)
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
                    else:
                        st.error("No se encontraron los coeficientes del modelo.")
                except Exception as e:
                    st.error(f"Error al generar la interpretación: {e}")
if __name__ == "__main__":
    main()
