import os
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from PyPDF2 import PdfReader
from docx import Document

app = Flask(__name__)

# Configuração do caminho absoluto para a pasta de templates
template_dir = os.path.abspath('templates')
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['TEMPLATE_FOLDER'] = template_dir

# Configurações para upload de arquivos
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Funções para verificar a extensão do arquivo permitida
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Função para contar palavras em um arquivo PDF
def count_words_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PdfReader(file)
        num_words = 0
        for page in reader.pages:
            num_words += len(page.extract_text().split())
    return num_words

# Função para contar palavras em um arquivo DOCX
def count_words_docx(file_path):
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    text = '\n'.join(full_text)
    words = text.split()
    return len(words)

# Rota principal
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Verifica se o arquivo foi fornecido
        if 'file' not in request.files:
            return render_template('index.html', error='Nenhum arquivo fornecido.')
        
        file = request.files['file']
        # Verifica se o arquivo é permitido
        if file and allowed_file(file.filename):
            # Salva o arquivo no diretório de uploads
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Obtém o valor por palavra e realiza o cálculo
            value_per_word = float(request.form['value_per_word'])
            if filename.endswith('.pdf'):
                result = count_words_pdf(filepath) * value_per_word
            elif filename.endswith('.docx'):
                result = count_words_docx(filepath) * value_per_word
            else:
                return render_template('index.html', error='Formato de arquivo não suportado.')

            return render_template('index.html', result=result)
        else:
            return render_template('index.html', error='Formato de arquivo não suportado.')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
