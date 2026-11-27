from docx import Document
from openpyxl import Workbook


def gerar_word() -> None:
    documento = Document()
    documento.add_heading('Projeto Aurora', level=1)
    documento.add_paragraph(
        'Responsável: Marina Souza. O prazo final é 15 de dezembro de 2026 e a prioridade é alta.'
    )
    documento.add_paragraph(
        'Entregas previstas: portal de atendimento, migração do cadastro de clientes '
        'e treinamento da equipe.'
    )
    documento.save('examples/projeto_aurora.docx')


def gerar_excel() -> None:
    planilha = Workbook()
    aba = planilha.active
    aba.title = 'Resumo'
    aba.append(['Projeto', 'Responsável', 'Prazo', 'Prioridade'])
    aba.append(['Projeto Aurora', 'Marina Souza', '2026-12-15', 'alta'])
    planilha.save('examples/projeto_aurora.xlsx')


if __name__ == '__main__':
    gerar_word()
    gerar_excel()
    print('Exemplos criados na pasta examples/')
