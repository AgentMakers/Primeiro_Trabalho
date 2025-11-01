"""
Script para converter documentos TXT em PDF
Cria PDFs a partir dos documentos da base de conhecimento

Uso: python generate_pdfs.py
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
from datetime import datetime


def create_pdf_from_txt(txt_path: Path, pdf_path: Path):
    """
    Converte arquivo TXT em PDF formatado

    Args:
        txt_path: Caminho do arquivo TXT
        pdf_path: Caminho do arquivo PDF de saída
    """
    # Lê conteúdo do TXT
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Cria documento PDF
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    # Estilos
    styles = getSampleStyleSheet()

    # Estilo para título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor='#1a1a1a',
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    # Estilo para subtítulos
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#2c3e50',
        spaceAfter=12,
        spaceBefore=18,
        fontName='Helvetica-Bold'
    )

    # Estilo para texto normal
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor='#333333',
        alignment=TA_JUSTIFY,
        spaceAfter=12,
        leading=14
    )

    # Monta story (conteúdo do PDF)
    story = []

    # Adiciona título (primeira linha do arquivo)
    lines = content.split('\n')
    if lines:
        title = lines[0].strip()
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 0.5*cm))

        # Adiciona informações do documento
        info_text = f"Documento gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        info_style = ParagraphStyle(
            'Info',
            parent=styles['Normal'],
            fontSize=8,
            textColor='#666666',
            alignment=TA_CENTER
        )
        story.append(Paragraph(info_text, info_style))
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph('<hr width="100%"/>', normal_style))
        story.append(Spacer(1, 0.5*cm))

    # Processa linhas do conteúdo
    in_list = False
    current_section = []

    for line in lines[1:]:  # Pula primeira linha (já usada como título)
        line = line.strip()

        # Linha vazia
        if not line:
            if current_section:
                story.extend(current_section)
                current_section = []
            story.append(Spacer(1, 0.3*cm))
            continue

        # Detecta separadores de seção
        if line.startswith('===') and line.endswith('==='):
            if current_section:
                story.extend(current_section)
                current_section = []
            # Remove === e pega o texto
            section_title = line.replace('===', '').strip()
            story.append(Spacer(1, 0.5*cm))
            story.append(Paragraph(section_title, subtitle_style))
            continue

        # Detecta sub-separadores
        if line.startswith('---'):
            if current_section:
                story.extend(current_section)
                current_section = []
            story.append(Spacer(1, 0.3*cm))
            continue

        # Escapa caracteres especiais para HTML
        line = line.replace('&', '&amp;')
        line = line.replace('<', '&lt;')
        line = line.replace('>', '&gt;')

        # Detecta títulos (MAIÚSCULAS seguidas de :)
        if ':' in line and line.split(':')[0].isupper() and len(line.split(':')[0]) > 3:
            if current_section:
                story.extend(current_section)
                current_section = []

            parts = line.split(':', 1)
            formatted_line = f"<b>{parts[0]}:</b> {parts[1] if len(parts) > 1 else ''}"
            story.append(Paragraph(formatted_line, normal_style))
            continue

        # Detecta listas (começam com - ou * ou número.)
        if line.startswith(('-', '*', '•')) or (len(line) > 2 and line[0].isdigit() and line[1] in '.):'):
            # Remove marcador e adiciona formatação
            if line.startswith(('-', '*', '•')):
                item_text = line[1:].strip()
                formatted_line = f"&nbsp;&nbsp;&nbsp;&nbsp;• {item_text}"
            else:
                formatted_line = f"&nbsp;&nbsp;&nbsp;&nbsp;{line}"

            story.append(Paragraph(formatted_line, normal_style))
            in_list = True
            continue

        # Texto normal
        if in_list:
            story.append(Spacer(1, 0.2*cm))
            in_list = False

        # Detecta negrito (texto entre **)
        if '**' in line:
            parts = line.split('**')
            formatted_line = ''
            for i, part in enumerate(parts):
                if i % 2 == 1:  # Parte entre **
                    formatted_line += f'<b>{part}</b>'
                else:
                    formatted_line += part
            line = formatted_line

        story.append(Paragraph(line, normal_style))

    # Adiciona seção restante
    if current_section:
        story.extend(current_section)

    # Adiciona rodapé
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph('<hr width="100%"/>', normal_style))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor='#999999',
        alignment=TA_CENTER
    )
    story.append(Paragraph(
        f"Fonte: {txt_path.name} | {txt_path.parent.name.upper()}",
        footer_style
    ))

    # Gera PDF
    doc.build(story)
    print(f"✅ PDF criado: {pdf_path.name}")


def main():
    """Processa todos os arquivos TXT e gera PDFs"""
    base_dir = Path("./base_conhecimento")

    if not base_dir.exists():
        print(f"❌ Pasta '{base_dir}' não encontrada!")
        return

    # Processa cada arquivo TXT
    txt_files = list(base_dir.glob("**/*.txt"))

    if not txt_files:
        print("⚠️  Nenhum arquivo TXT encontrado!")
        return

    print(f"📄 Encontrados {len(txt_files)} arquivos TXT\n")

    for txt_file in txt_files:
        try:
            # Define caminho do PDF (mesma estrutura, substitui .txt por .pdf)
            pdf_file = txt_file.with_suffix('.pdf')

            print(f"Processando: {txt_file.relative_to(base_dir)}")
            create_pdf_from_txt(txt_file, pdf_file)

        except Exception as e:
            print(f"❌ Erro ao processar {txt_file.name}: {e}")

    print(f"\n✅ Processo concluído! {len(txt_files)} PDFs gerados.")
    print(f"\n💡 Os PDFs foram criados na mesma estrutura de pastas dos TXT")


if __name__ == "__main__":
    # Verifica se reportlab está instalado
    try:
        import reportlab
        main()
    except ImportError:
        print("❌ Biblioteca 'reportlab' não encontrada!")
        print("📦 Instale com: pip install reportlab")
