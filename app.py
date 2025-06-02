from flask import Flask, render_template, url_for, request, redirect
import os
from dotenv import load_dotenv
import csv
import google.generativeai as genai


load_dotenv()

app = Flask(__name__)

api_key = os.getenv("API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    print('AVISO: GOOGLE_GENAI_API_KEY não definida no ambiente.')

@app.route('/')
def Ola():
    # retun '<h1>Olá, Mundo!</h1>'
    return render_template('index.html')

@app.route('/sobre-equipe')
def sobreequipe():
    return render_template('sobre-equipe.html')

@app.route('/glossario')
def glossario():
    glosssario_de_termos = []

    with open('bd_glossario.csv', 'r', newline='', encoding='utf-8') as arquivo:
        reader = csv.reader(arquivo, delimiter=';')
        for linha in reader:
            glosssario_de_termos.append(linha)

    return render_template('glossario.html', glossario=glosssario_de_termos)

@app.route('/novo-termo')
def novo_termo():
   return render_template('novo-termo.html')

@app.route('/criar-termo', methods=['POST'])
def criar_termo():
    termo = request.form['termo']
    definicao = request.form['definicao']
    with open('bd_glossario.csv', 'a', newline='', encoding='utf-8') as arquivo:
        writer = csv.writer(arquivo, delimiter=';')
        writer.writerow([termo, definicao])

    return redirect(url_for('glossario'))

@app.route('/remover-termo', methods=['POST'])
def remover_termo():
    termo = request.form['termo']
    termos_atualizados = []

    with open('bd_glossario.csv', 'r', newline='', encoding='utf-8') as arquivo:
        reader = csv.reader(arquivo, delimiter=';')
        for linha in reader:
            if linha[0] != termo:
                termos_atualizados.append(linha)

    with open('bd_glossario.csv', 'w', newline='', encoding='utf-8') as arquivo:
        writer = csv.writer(arquivo, delimiter=';')
        writer.writerows(termos_atualizados)

    return redirect(url_for('glossario'))

@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot_page():
    resposta = None
    if request.method == 'POST':
        pergunta = request.form.get('pergunta')
        if pergunta:
            try:
                model = genai.GenerativeModel('gemini-2.0-flash')
                response = model.generate_content([pergunta])
                # Verificação segura para evitar AttributeError
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts') and candidate.content.parts:
                        resposta = getattr(candidate.content.parts[0], 'text', 'Sem resposta do modelo.')
                    else:
                        resposta = 'Sem resposta do modelo.'
                else:
                    resposta = 'Sem resposta do modelo.'
            except Exception as e:
                import traceback
                print('ERRO GEMINI:', traceback.format_exc())
                resposta = f"Erro ao consultar Gemini: {str(e)}\n{traceback.format_exc()}"
    return render_template('chatbot.html', resposta=resposta)

@app.route('/comandos-iniciais')
def comandos_iniciais():
    return render_template('comandos-iniciais.html')

@app.route('/dicas')
def dicas():
    return render_template('dicas.html')
   
app.run(debug=True)
