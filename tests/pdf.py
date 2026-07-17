from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("helvetica", style="B", size=16)
pdf.cell(40,10, "Hello World! Meu primeiro PDF via VS Code.")
pdf.output("meu_documento.pdf")
print("PDF criado com sucesso!")