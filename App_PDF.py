import streamlit as st
from docx2pdf import convert
from PIL import Image
import PyPDF2
import io
import os

st.title("📄 App de Manipulação de PDFs")
st.markdown("**Transforme, una ou separe páginas de arquivos PDF, Word e Imagens de maneira fácil e rápida!**")

# Carregamento do arquivo e configuração do local de salvamento
st.header("Configurações Gerais")
uploaded_file = st.file_uploader("Faça o upload do arquivo (PDF, DOCX ou Imagem)", type=["pdf", "docx", "jpg", "jpeg", "png"])
file_type = st.selectbox("Selecione o tipo do arquivo carregado", ["PDF", "Word (.docx)", "Imagem (JPG, PNG)"])

# Verificar se o arquivo foi carregado corretamente e exibir mensagem de erro
if uploaded_file:
    file_extension = uploaded_file.name.split(".")[-1].lower()
    if (file_type == "Word (.docx)" and file_extension != "docx") or \
       (file_type == "Imagem (JPG, PNG)" and file_extension not in ["jpg", "jpeg", "png"]) or \
       (file_type == "PDF" and file_extension != "pdf"):
        st.error("Erro: o tipo selecionado não corresponde ao arquivo carregado.")
        uploaded_file = None

# Organizar funcionalidades em abas com ícones
tab1, tab2, tab3, tab4 = st.tabs(["📑 Conversão para PDF", "📚 União de PDFs", "✂️ Separação de Páginas", "📄 Separar Páginas Individualmente"])

# 1. Conversão para PDF
with tab1:
    st.header("📑 Conversão para PDF")
    st.write("Converta arquivos do Word (.docx) ou imagens (.jpg, .png) para PDF com um clique.")
    
    if st.button("Converter para PDF"):
        if uploaded_file:
            if file_type == "PDF":
                st.warning("O arquivo já está em PDF. Por favor, carregue um arquivo Word ou imagem para conversão.")
            else:
                try:
                    with st.spinner("Convertendo..."):
                        output_buffer = io.BytesIO()
                        if file_type == "Word (.docx)":
                            with open("temp_file.docx", "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            convert("temp_file.docx", "output.pdf")
                            with open("output.pdf", "rb") as output_file:
                                output_buffer.write(output_file.read())
                            os.remove("temp_file.docx")
                            os.remove("output.pdf")
                        elif file_type == "Imagem (JPG, PNG)":
                            image = Image.open(uploaded_file)
                            image.save(output_buffer, format="PDF")
                        st.download_button(label="Baixar PDF", data=output_buffer.getvalue(), file_name="Convertido.pdf", mime="application/pdf")
                        st.success("Conversão para PDF realizada com sucesso!")
                except PermissionError:
                    st.error("Erro ao converter o arquivo. Verifique as permissões.")

# 2. União de PDFs
with tab2:
    st.header("📚 União de Múltiplos PDFs")
    st.write("Selecione vários arquivos PDF para unir em um único documento.")
    uploaded_pdfs = st.file_uploader("Faça o upload dos arquivos PDF que deseja unir", type="pdf", accept_multiple_files=True)

    if st.button("Unir PDFs"):
        if uploaded_pdfs:
            with st.spinner("Unindo PDFs..."):
                output_buffer = io.BytesIO()
                pdf_merger = PyPDF2.PdfMerger()
                for pdf in uploaded_pdfs:
                    pdf_merger.append(io.BytesIO(pdf.read()))
                pdf_merger.write(output_buffer)
                st.download_button(label="Baixar PDF Unificado", data=output_buffer.getvalue(), file_name="PDF_Unificado.pdf", mime="application/pdf")
                st.success("União de PDFs realizada com sucesso!")
        else:
            st.warning("Por favor, faça o upload de pelo menos dois arquivos PDF.")

# 3. Separar Páginas de um PDF em um único arquivo
with tab3:
    st.header("✂️ Separar Páginas Específicas de um PDF")
    st.write("Escolha as páginas de um PDF para extrair em um novo arquivo PDF.")
    pages_to_extract = st.text_input("Digite as páginas a extrair (ex: 1,2,5):")

    if st.button("Separar Páginas"):
        if uploaded_file and pages_to_extract and file_type == "PDF":
            with st.spinner("Extraindo páginas..."):
                output_buffer = io.BytesIO()
                pages = [int(x) - 1 for x in pages_to_extract.split(",") if x.isdigit()]
                reader = PyPDF2.PdfReader(uploaded_file)
                writer = PyPDF2.PdfWriter()

                for page_num in pages:
                    writer.add_page(reader.pages[page_num])

                writer.write(output_buffer)
                st.download_button(label="Baixar PDF com Páginas Extraídas", data=output_buffer.getvalue(), file_name="PDF_Extraido.pdf", mime="application/pdf")
                st.success("Páginas extraídas com sucesso!")
        else:
            st.warning("Por favor, carregue um PDF válido e defina as páginas.")

# 4. Separar cada página do PDF em arquivos individuais
with tab4:
    st.header("📄 Separar Cada Página do PDF em Arquivos Individuais")
    st.write("Extraia cada página de um PDF em arquivos PDF separados.")
    
    if st.button("Separar Páginas Individualmente"):
        if uploaded_file and file_type == "PDF":
            with st.spinner("Salvando páginas individualmente..."):
                reader = PyPDF2.PdfReader(uploaded_file)
                for page_num in range(len(reader.pages)):
                    output_buffer = io.BytesIO()
                    writer = PyPDF2.PdfWriter()
                    writer.add_page(reader.pages[page_num])
                    writer.write(output_buffer)
                    st.download_button(label=f"Baixar Página {page_num + 1}", data=output_buffer.getvalue(), file_name=f"Pagina_{page_num + 1}.pdf", mime="application/pdf")
                st.success("Todas as páginas foram separadas e salvas individualmente!")
        else:
            st.warning("Por favor, carregue um PDF válido.")
