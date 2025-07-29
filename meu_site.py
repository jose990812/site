from flask import Flask, request, jsonify, render_template
import pandas as pd
import unicodedata

app = Flask(__name__)

CSV_URL = "https://docs.google.com/spreadsheets/d/11Fw8g9alMZkxML-rDDQ-Za2KZwsbFFqgp6Tleat4-YI/export?format=csv"

def normalizar(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/buscar')
def buscar():
    try:
        df = pd.read_csv(CSV_URL, dtype=str)
        df.columns = df.columns.str.strip().str.lower()

        if "cidade" not in df.columns:
            return jsonify({"erro": "Coluna 'cidade' não encontrada."})

        df["cidade"] = df["cidade"].apply(lambda x: normalizar(str(x).strip().lower()))

        cidade = request.args.get('cidade', '').strip().lower()
        cidade_normalizada = normalizar(cidade)

        resultado_df = df[df["cidade"].str.contains(cidade_normalizada, case=False, na=False)]

        if resultado_df.empty:
            return jsonify({"erro": "Cidade não encontrada."})

        resultado_txt = ""
        numeros = []
        colunas = ["cidade"] + [col for col in df.columns if col != "cidade"][:3]

        for _, row in resultado_df.iterrows():
            linha_txt = "\t".join([str(row[col]) for col in colunas])
            resultado_txt += linha_txt + "\n"
            for val in row.values:
                if any(c.isdigit() for c in str(val)):
                    numeros.append(str(val).strip())

        numeros_unicos = list(set(numeros))
        return jsonify({
            "resultado": resultado_txt.strip(),
            "numeros": numeros_unicos
        })

    except Exception as e:
        return jsonify({"erro": f"Erro ao carregar planilha: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
