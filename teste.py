
import streamlit as st
import os
import json
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from streamlit_quill import st_quill

# Caminhos base para os arquivos locais
pastas_base = {
    "preliminares": r"C:\\Users\\trt18\\Documents\\Prompts\\TEXTOS JR PARA COLAB\\preliminares",
    "prejudiciais": r"C:\\Users\\trt18\\Documents\\Prompts\\TEXTOS JR PARA COLAB\\prejudicias",
    "merito": r"C:\\Users\\trt18\\Documents\\Prompts\\TEXTOS JR PARA COLAB\\merito"
}

# Função para listar e ordenar arquivos de uma subpasta específica
def listar_arquivos_ordenados(pasta):
    arquivos = os.listdir(pasta)
    return sorted(arquivos, key=lambda x: ''.join([i for i in x if i.isdigit()]))

# Função para ler o conteúdo de um arquivo
def ler_arquivo(nome_arquivo, pasta):
    caminho_arquivo = os.path.join(pastas_base[pasta], nome_arquivo)
    try:
        with open(caminho_arquivo, 'r', encoding='latin1') as file:
            return file.read()
    except (FileNotFoundError, UnicodeDecodeError):
        return f'Erro ao abrir ou ler o arquivo {nome_arquivo}.'

# Configuração inicial do Streamlit
st.set_page_config(page_title="Gerador de Documentos Trabalhistas", layout="wide")

# Armazenar os dados entre as etapas
if "dados_extraidos" not in st.session_state:
    st.session_state["dados_extraidos"] = {}
if "editor_content" not in st.session_state:
    st.session_state["editor_content"] = ""

# Painel lateral para entrada de dados
st.sidebar.title("Configurações de Entrada")

# Campo para inserir os dados em JSON
dados_json = st.sidebar.text_area("Insira os dados em formato JSON", height=200)
try:
    if dados_json:
        st.session_state["dados_extraidos"] = json.loads(dados_json)
        st.sidebar.success("Dados carregados com sucesso!")
except json.JSONDecodeError:
    st.sidebar.error("Erro ao carregar os dados. Certifique-se de que o JSON está no formato correto.")

# Seções de quantidade de textos e arquivos de mérito
st.sidebar.subheader("Textos e Arquivos")
quantidade_textos = 5  # Definido para cinco caixas de texto

# Listar arquivos para a categoria de mérito
arquivos_merito = listar_arquivos_ordenados(pastas_base["merito"])

# Adicionar caixas de texto e seleção de arquivos de mérito para cada quantidade de texto
resumos_autor = []
resumos_reclamada = []
arquivos_selecionados_merito = []
for i in range(quantidade_textos):
    resumo_autor = st.sidebar.text_area(f"Resumo do Autor {i + 1}", "")
    resumo_reclamada = st.sidebar.text_area(f"Resumo da Reclamada {i + 1}", "")
    arquivo_merito = st.sidebar.selectbox(f"Arquivo do Mérito {i + 1}", ["Selecione um arquivo"] + arquivos_merito, key=f"arquivo_merito_{i}")
    resumos_autor.append(resumo_autor)
    resumos_reclamada.append(resumo_reclamada)
    arquivos_selecionados_merito.append(arquivo_merito)

# Caixa para Depoimentos e Outros Textos
depoimentos = st.sidebar.text_area("Depoimentos", "")
outros_textos = st.sidebar.text_area("Outros Textos", "")

# Editor de texto
st.subheader("Editor de Texto")
editor_content = st_quill(value=st.session_state["editor_content"], placeholder="Edite o conteúdo aqui...", key="quill", toolbar=True)

# Botão para inserir dados JSON e arquivos selecionados no editor
if st.sidebar.button("Inserir Dados e Arquivos no Editor"):
    dados_formatados = "\n".join([f"{value}" for value in st.session_state["dados_extraidos"].values()])
    arquivos_texto = "\n\n".join(ler_arquivo(arquivo, "merito") for arquivo in arquivos_selecionados_merito if arquivo != "Selecione um arquivo")
    
    # Atualizar o conteúdo do editor
    st.session_state["editor_content"] = editor_content + f"\n{dados_formatados}\n{arquivos_texto}\n{depoimentos}\n{outros_textos}"

# Atualizar conteúdo do editor com o novo valor
editor_content = st.session_state["editor_content"]

# Botão para salvar o conteúdo do editor em DOCX
if st.sidebar.button("Salvar Documento"):
    doc = Document()
    paragrafo = doc.add_paragraph(st.session_state["editor_content"])
    paragrafo.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY

    # Define estilo para Arial 14
    for run in paragrafo.runs:
        run.font.name = 'Arial'
        run.font.size = Pt(14)

    caminho_salvar = os.path.join(pastas_base["preliminares"], "documento_final.docx")
    doc.save(caminho_salvar)
    st.sidebar.success(f"Documento salvo com sucesso em: {caminho_salvar}")
