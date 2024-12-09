from manim import *
import json
import os
import numpy as np

class LikelihoodFunction(Scene):
    def construct(self):
        # Ruta al archivo de configuración
        config_path = "config.json"

        # Verificar si el archivo de configuración existe
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"El archivo de configuración '{config_path}' no fue encontrado.")

        # Leer los parámetros desde config.json
        with open(config_path, 'r') as file:
            config = json.load(file)
            n = config.get('n', 10)
            x = config.get('x', 7)

        # Validar los parámetros
        if x > n:
            raise ValueError("El número de caras obtenidas (x) no puede ser mayor que el número de lanzamientos (n).")

        # Definir la función de verosimilitud
        def likelihood(p):
            return (p ** x) * ((1 - p) ** (n - x))

        # Crear los ejes con un rango de y más manejable
        likelihood_max = likelihood(x/n)  # El máximo de la función de verosimilitud ocurre en p = x/n
        axes = Axes(
            x_range=[0, 1, 0.1],
            y_range=[0, likelihood_max * 1.2, likelihood_max * 0.2],
            axis_config={"include_numbers": True},
            x_axis_config={"label_direction": DOWN},
            y_axis_config={"label_direction": LEFT},
        ).add_coordinates()

        # Etiquetas de los ejes
        axes_labels = axes.get_axis_labels(x_label="p", y_label="L(p) = p^x (1-p)^{n-x}")

        # Mover la etiqueta de L(p) para evitar superposición
        axes_labels[1].shift(UP * 0.3)

        # Crear la gráfica de la función de verosimilitud
        graph = axes.plot(
            likelihood,
            color=BLUE,
            x_range=[0, 1],
        )

        # Mostrar los valores de n y x en la esquina superior derecha
        text = Text(f"n = {n}, x = {x}", font_size=24).to_corner(UR)

        # Añadir elementos a la escena
        self.play(Create(axes), Write(axes_labels))
        self.play(Write(text))
        self.play(Create(graph))
        self.wait(2)

class RegressionFunction(Scene):
    def construct(self):
        # Ruta al archivo de configuración
        config_path = "config_regression.json"

        # Verificar si el archivo de configuración existe
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"El archivo de configuración '{config_path}' no fue encontrado.")

        # Leer los parámetros desde config_regression.json
        with open(config_path, 'r') as file:
            config = json.load(file)
            X = np.array(config.get('X', []))
            Y = np.array(config.get('Y', []))
            grado = config.get('grado', 1)
            coeficientes = config.get('coeficientes', [])

        # Validar los datos
        if len(X) == 0 or len(Y) == 0:
            raise ValueError("No hay datos para graficar.")
        if len(coeficientes) != grado + 1:
            raise ValueError("Los coeficientes no coinciden con el grado del polinomio.")

        # Definir la función de regresión
        polinomio = np.poly1d(coeficientes)

        # Crear los ejes
        x_min = min(X) - 1
        x_max = max(X) + 1
        y_min = min(Y) - 5
        y_max = max(Y) + 5

        axes = Axes(
            x_range=[x_min, x_max, 1],
            y_range=[y_min, y_max, 5],
            axis_config={"include_numbers": True},
            x_axis_config={"label_direction": DOWN},
            y_axis_config={"label_direction": LEFT},
        ).add_coordinates()

        # Crear etiquetas para los ejes
        x_label = Tex("Producción (x)")
        
        # Construir la fórmula de regresión
        if grado == 1:
            m, b = coeficientes
            formula_text = f"y = {m:.2f}x + {b:.2f}"
        else:
            terms = [f"{coef:.2f}x^{grado - i}" for i, coef in enumerate(coeficientes[:-1])]
            terms.append(f"{coeficientes[-1]:.2f}")
            formula_text = "y = " + " + ".join(terms)
        
        # Crear el objeto MathTex para la fórmula
        formula = MathTex(formula_text)

        # Combinar la etiqueta del eje y con la fórmula
        y_label = VGroup(
            Tex("Horas Trabajadas (y)"),
            formula
        ).arrange(DOWN, aligned_edge=LEFT)

        # Posicionar las etiquetas en los ejes
        axes_labels = axes.get_axis_labels(x_label=x_label, y_label=y_label)

        # Crear los puntos de datos
        puntos = VGroup(*[
            Dot(axes.coords_to_point(x, y), color=RED) for x, y in zip(X, Y)
        ])

        # Crear la gráfica de la regresión
        graph = axes.plot(
            polinomio,
            color=BLUE,
            x_range=[x_min, x_max],
        )

        # Crear líneas de error
        errores = VGroup()
        for x, y in zip(X, Y):
            punto = axes.coords_to_point(x, y)
            y_pred = polinomio(x)
            punto_pred = axes.coords_to_point(x, y_pred)
            error = DashedLine(punto, punto_pred, color=GREEN)
            errores.add(error)

        # Añadir elementos a la escena
        self.play(Create(axes), Write(axes_labels))
        self.play(Create(puntos))
        self.play(Create(graph))
        self.play(Create(errores))
        self.wait(2)
