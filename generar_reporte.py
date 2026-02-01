import json
import ast
import os
import webbrowser

def generar_html_interactivo():
    archivo_entrada = "conocimiento_gato.json"
    archivo_salida = "REPORTE_CEREBRO_INTERACTIVO.html"
    
    print(f"Leyendo {archivo_entrada}...")
    
    if not os.path.exists(archivo_entrada):
        print("Error: No se encuentra el archivo de conocimiento. Entrena primero.")
        return

    with open(archivo_entrada, "r") as f:
        data = json.load(f)

    estados_ordenados = sorted(data.keys())

    # --- HTML + CSS + JAVASCRIPT (Todo en uno) ---
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Cerebro IA - Reporte Interactivo</title>
        <style>
            body { font-family: 'Segoe UI', sans-serif; background-color: #f0f2f5; padding: 20px; color: #333; }
            h1 { text-align: center; color: #2c3e50; }
            .controles { text-align: center; margin: 20px 0; position: sticky; top: 0; background: #f0f2f5; padding: 10px; z-index: 100; }
            
            /* Botones de Filtro */
            button {
                padding: 10px 20px; margin: 0 5px; border: none; border-radius: 5px; cursor: pointer;
                font-weight: bold; font-size: 14px; transition: transform 0.1s;
            }
            button:active { transform: scale(0.95); }
            .btn-todo { background-color: #34495e; color: white; }
            .btn-ganar { background-color: #27ae60; color: white; }
            .btn-perder { background-color: #c0392b; color: white; }
            .btn-neutro { background-color: #7f8c8d; color: white; }

            table { width: 100%; border-collapse: collapse; background-color: white; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            th, td { padding: 12px 10px; text-align: center; border-bottom: 1px solid #ecf0f1; }
            th { background-color: #2980b9; color: white; }
            tr:hover { background-color: #f1f9fe; }

            /* Mini Tablero */
            .tablero-visual { 
                font-family: 'Courier New', monospace; font-weight: bold; line-height: 14px; 
                display: inline-block; border: 1px solid #bdc3c7; padding: 4px; background: #ecf0f1; border-radius: 4px;
            }
            
            /* Colores de Celdas */
            .val-pos { color: #27ae60; font-weight: bold; }
            .val-neg { color: #c0392b; }
            .val-zero { color: #bdc3c7; font-size: 0.85em; }
            .mejor-jugada { background-color: #d5f5e3; border: 2px solid #2ecc71; border-radius: 4px; }
            
            /* Clases para Filtrado (JavaScript las usará) */
            .fila-ganadora { }
            .fila-perdedora { }
            .fila-neutra { }
            .oculto { display: none; }
        </style>
    </head>
    <body>
        <h1> Análisis del Cerebro Q-Learning</h1>
        
        <div class="controles">
            <p>Julio Romero Merry-am Blanco</p>
            <button class="btn-todo" onclick="filtrar('todo')">Ver Todo</button>
            <button class="btn-ganar" onclick="filtrar('ganar')"> Explotación (Mejores Jugadas)</button>
            <button class="btn-perder" onclick="filtrar('perder')">Errores (Castigos)</button>
            <button class="btn-neutro" onclick="filtrar('neutro')">Exploración (Incertidumbre)</button>
        </div>

        <table id="tabla-q">
            <thead>
                <tr>
                    <th>Tablero</th>
                    <th>Estado (Tupla)</th>
                    <th>0</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th><th>7</th><th>8</th>
                </tr>
            </thead>
            <tbody>
    """

    conteo_ganar = 0
    conteo_perder = 0

    for estado_str in estados_ordenados:
        acciones = data[estado_str]
        valores = [acciones.get(str(i), 0.0) for i in range(9)]
        
        # --- LÓGICA DE CLASIFICACIÓN ---
        max_val = max(valores) if valores else 0
        min_val = min(valores) if valores else 0
        
        clase_fila = "fila-neutra" # Por defecto
        
        # Si hay una jugada muy buena (> 1.0), es conocimiento de "Cómo Ganar"
        if max_val > 1.0:
            clase_fila = "fila-ganadora"
            conteo_ganar += 1
        # Si hay una jugada muy mala (< -1.0) y no hay buenas, es conocimiento de "Errores"
        elif min_val < -1.0:
            clase_fila = "fila-perdedora"
            conteo_perder += 1

        # Generar Tablero Visual
        try:
            estado_tupla = ast.literal_eval(estado_str)
            v = [c if c != " " else "·" for c in estado_tupla]
            visual_html = f"{v[0]}{v[1]}{v[2]}<br>{v[3]}{v[4]}{v[5]}<br>{v[6]}{v[7]}{v[8]}"
        except:
            visual_html = "?"

        html += f"<tr class='{clase_fila}'>"
        html += f"<td><div class='tablero-visual'>{visual_html}</div></td>"
        html += f"<td style='font-size:0.75em; color:#7f8c8d;'>{estado_str}</td>"
        
        # Celdas de valores
        for val in valores:
            estilo = ""
            texto = f"{val:.2f}"
            clase_val = "val-zero"
            
            if val > 0: clase_val = "val-pos"
            if val < 0: clase_val = "val-neg"
            
            # Resaltar la estrella
            if val == max_val and val != 0:
                estilo = "class='mejor-jugada'"
                texto = f"★ {val:.1f}"
            
            html += f"<td {estilo}><span class='{clase_val}'>{texto}</span></td>"
        html += "</tr>"

    html += """
            </tbody>
        </table>

        <script>
            function filtrar(tipo) {
                var filas = document.querySelectorAll('#tabla-q tbody tr');
                filas.forEach(fila => {
                    if (tipo === 'todo') {
                        fila.classList.remove('oculto');
                    } else if (tipo === 'ganar') {
                        fila.classList.contains('fila-ganadora') ? fila.classList.remove('oculto') : fila.classList.add('oculto');
                    } else if (tipo === 'perder') {
                        fila.classList.contains('fila-perdedora') ? fila.classList.remove('oculto') : fila.classList.add('oculto');
                    } else if (tipo === 'neutro') {
                        fila.classList.contains('fila-neutra') ? fila.classList.remove('oculto') : fila.classList.add('oculto');
                    }
                });
            }
        </script>
    </body>
    </html>
    """

    with open(archivo_salida, "w", encoding="utf-8") as f:
        f.write(html)
        
    print(f"Reporte generado: {archivo_salida}")
    print(f"   - Estados ganadores detectados: {conteo_ganar}")
    print(f"   - Estados con errores detectados: {conteo_perder}")
    webbrowser.open('file://' + os.path.realpath(archivo_salida))

if __name__ == "__main__":
    generar_html_interactivo()