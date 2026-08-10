# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from tkinter import font as tkfont
from datetime import datetime, timedelta
from pathlib import Path
import json
import os

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.pdfgen import canvas
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import Paragraph
except ImportError:
    print("Instale: pip install reportlab pillow")
    exit()


# ==========================================
# INFORMACOES DA EMPRESA
# ==========================================
EMPRESA_NOME = "Bruceli Corp."
VERSAO = "1.2"


# ==========================================
# LISTA PRE-CADASTRADA DE EPIs (com periodicidade SUGERIDA)
# O usuario pode alterar a periodicidade direto na interface!
# ==========================================
EPIS_CADASTRADOS = {
    "Capacete de Protecao": 60,
    "Oculos de Protecao Incolor": 12,
    "Oculos de Protecao Escuro": 12,
    "Protetor Auricular Tipo Plug": 6,
    "Protetor Auricular Tipo Concha": 12,
    "Mascara de Protecao PFF2": 1,
    "Luva de Vaqueta": 3,
    "Luva de Nitrilon": 1,
    "Luva de Latex": 1,
    "Bota de Seguranca c/ Bico de Composite": 6,
    "Bota de Borracha": 6,
    "Perneira de Protecao": 12,
    "Protetor Solar": 1,
}


CARGOS_CADASTRADOS = [
    "Operador de Maquinas",
    "Operador de Rolo Compactador",
    "Operador de Motoniveladora",
    "Operador de Escavadeira",
    "Operador de Retroescavadeira",
    "Operador de Pa Carregadeira",
    "Operador de Vibroacabadora",
    "Rasteleiro",
    "Servente de Pavimentacao",
    "Auxiliar de Pavimentacao",
    "Motorista de Caminhao",
    "Motorista de Caminhao Basculante",
    "Motorista de Caminhao Pipa",
    "Encarregado de Obra",
    "Mestre de Obras",
    "Apontador",
    "Sinaleiro",
    "Ajudante Geral",
    "Pedreiro",
    "Servente",
    "Topografo",
    "Auxiliar de Topografia",
    "Tecnico em Seguranca do Trabalho",
]


SETORES_CADASTRADOS = [
    "Pavimentacao",
    "Terraplanagem",
    "Operacao Tapa Buraco",
    "Manutencao",
    "Administrativo",
    "Seguranca do Trabalho",
]


ARQUIVO_DADOS = "epis_personalizados.json"


class ChecklistEPI:
    def __init__(self, root):
        self.root = root
        self.root.title("Checklist de EPI v" + VERSAO + " - " + EMPRESA_NOME)
        self.root.geometry("950x800")
        self.root.configure(bg="#f0f0f0")
        
        self.carregar_epis_personalizados()
        self.criar_interface()
    
    def carregar_epis_personalizados(self):
        """Carrega EPIs personalizados e periodicidades alteradas"""
        global EPIS_CADASTRADOS
        try:
            if Path(ARQUIVO_DADOS).exists():
                with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                    EPIS_CADASTRADOS.update(dados)
        except:
            pass
    
    def salvar_dados(self):
        """Salva todos os EPIs com periodicidades atuais"""
        try:
            with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
                json.dump(EPIS_CADASTRADOS, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("Erro ao salvar: " + str(e))
    
    def criar_interface(self):
        # Cabecalho
        header = tk.Frame(self.root, bg="#1a2b4a", height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, text="** " + EMPRESA_NOME.upper() + " **", 
                font=("Arial", 11, "bold"), bg="#1a2b4a", fg="#f39c12").pack(pady=(8, 0))
        tk.Label(header, text="CHECKLIST DE PERIODICIDADE DE EPI", 
                font=("Arial", 15, "bold"), bg="#1a2b4a", fg="white").pack()
        tk.Label(header, text="Gera checklist em PDF A4 para auditoria de EPIs", 
                font=("Arial", 9), bg="#1a2b4a", fg="#bdc3c7").pack()
        
        canvas_scroll = tk.Canvas(self.root, bg="#f0f0f0", highlightthickness=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas_scroll.yview)
        scrollable_frame = tk.Frame(canvas_scroll, bg="#f0f0f0")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all"))
        )
        
        canvas_scroll.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas_scroll.configure(yscrollcommand=scrollbar.set)
        
        canvas_scroll.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        def on_mousewheel(event):
            canvas_scroll.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas_scroll.bind_all("<MouseWheel>", on_mousewheel)
        
        # DADOS DO TRABALHADOR
        frame_dados = tk.LabelFrame(scrollable_frame, text=" DADOS DO TRABALHADOR (opcional) ", 
                                   font=("Arial", 10, "bold"), bg="#f0f0f0",
                                   padx=15, pady=10)
        frame_dados.pack(fill="x", pady=10)
        
        aviso = tk.Label(frame_dados, 
                        text="Todos os campos sao OPCIONAIS. Deixe em branco para preencher a mao na obra.",
                        font=("Arial", 9, "italic"), bg="#fff9e6", fg="#e67e22",
                        relief="solid", bd=1, padx=10, pady=5)
        aviso.grid(row=0, column=0, columnspan=2, sticky="ew", pady=5)
        
        tk.Label(frame_dados, text="Nome Completo:", font=("Arial", 10, "bold"), 
                bg="#f0f0f0").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_nome = tk.Entry(frame_dados, font=("Arial", 11), width=50)
        self.entry_nome.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        tk.Label(frame_dados, text="Cargo:", font=("Arial", 10, "bold"), 
                bg="#f0f0f0").grid(row=2, column=0, sticky="w", pady=5)
        self.combo_cargo = ttk.Combobox(frame_dados, values=CARGOS_CADASTRADOS, 
                                        font=("Arial", 11), width=48)
        self.combo_cargo.grid(row=2, column=1, sticky="w", padx=10, pady=5)
        
        tk.Label(frame_dados, text="Setor:", font=("Arial", 10, "bold"), 
                bg="#f0f0f0").grid(row=3, column=0, sticky="w", pady=5)
        self.combo_setor = ttk.Combobox(frame_dados, values=SETORES_CADASTRADOS, 
                                       font=("Arial", 11), width=48)
        self.combo_setor.grid(row=3, column=1, sticky="w", padx=10, pady=5)
        
        tk.Label(frame_dados, text="Data da Auditoria:", font=("Arial", 10, "bold"), 
                bg="#f0f0f0").grid(row=4, column=0, sticky="w", pady=5)
        self.entry_data = tk.Entry(frame_dados, font=("Arial", 11), width=15)
        self.entry_data.grid(row=4, column=1, sticky="w", padx=10, pady=5)
        
        tk.Label(frame_dados, text="Matricula/CTPS:", font=("Arial", 10, "bold"), 
                bg="#f0f0f0").grid(row=5, column=0, sticky="w", pady=5)
        self.entry_matricula = tk.Entry(frame_dados, font=("Arial", 11), width=25)
        self.entry_matricula.grid(row=5, column=1, sticky="w", padx=10, pady=5)
        
        tk.Button(frame_dados, text="Preencher data de hoje", 
                 command=self.preencher_data,
                 bg="#95a5a6", fg="white", font=("Arial", 8),
                 cursor="hand2").grid(row=4, column=1, sticky="e", padx=10)
        
        # SELECAO DE EPIs COM PERIODICIDADE EDITAVEL
        frame_epis = tk.LabelFrame(scrollable_frame, text=" SELECAO DE EPIs E PERIODICIDADE ", 
                                  font=("Arial", 10, "bold"), bg="#f0f0f0",
                                  padx=15, pady=10)
        frame_epis.pack(fill="x", pady=10)
        
        # Instrucao especial sobre periodicidade
        info_period = tk.Label(frame_epis, 
                              text="Selecione os EPIs e ALTERE a periodicidade (em meses) conforme necessario. As mudancas sao salvas automaticamente!",
                              font=("Arial", 9, "italic"), bg="#e8f4f8", fg="#2c3e50",
                              relief="solid", bd=1, padx=10, pady=5, wraplength=850)
        info_period.pack(fill="x", pady=5)
        
        frame_lista_epis = tk.Frame(frame_epis, bg="white", relief="sunken", bd=1)
        frame_lista_epis.pack(fill="both", expand=True, pady=5)
        
        canvas_epis = tk.Canvas(frame_lista_epis, bg="white", height=300, highlightthickness=0)
        scroll_epis = tk.Scrollbar(frame_lista_epis, orient="vertical", command=canvas_epis.yview)
        self.frame_checkboxes = tk.Frame(canvas_epis, bg="white")
        
        self.frame_checkboxes.bind(
            "<Configure>",
            lambda e: canvas_epis.configure(scrollregion=canvas_epis.bbox("all"))
        )
        
        canvas_epis.create_window((0, 0), window=self.frame_checkboxes, anchor="nw")
        canvas_epis.configure(yscrollcommand=scroll_epis.set)
        
        canvas_epis.pack(side="left", fill="both", expand=True)
        scroll_epis.pack(side="right", fill="y")
        
        self.checkboxes = {}  # {epi: BooleanVar}
        self.entries_periodo = {}  # {epi: Entry}
        self.atualizar_lista_epis()
        
        frame_botoes_epi = tk.Frame(frame_epis, bg="#f0f0f0")
        frame_botoes_epi.pack(fill="x", pady=10)
        
        tk.Button(frame_botoes_epi, text="+ Adicionar Novo EPI", 
                 command=self.adicionar_epi,
                 bg="#3498db", fg="white", font=("Arial", 10, "bold"),
                 cursor="hand2").pack(side="left", padx=5)
        
        tk.Button(frame_botoes_epi, text="Selecionar Todos", 
                 command=self.selecionar_todos,
                 bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
                 cursor="hand2").pack(side="left", padx=5)
        
        tk.Button(frame_botoes_epi, text="Desmarcar Todos", 
                 command=self.desmarcar_todos,
                 bg="#e74c3c", fg="white", font=("Arial", 10, "bold"),
                 cursor="hand2").pack(side="left", padx=5)
        
        tk.Button(frame_botoes_epi, text="Salvar Periodicidades", 
                 command=self.salvar_periodicidades,
                 bg="#8e44ad", fg="white", font=("Arial", 10, "bold"),
                 cursor="hand2").pack(side="left", padx=5)
        
        tk.Button(frame_botoes_epi, text="Excluir EPI Selecionado", 
                 command=self.excluir_epi,
                 bg="#95a5a6", fg="white", font=("Arial", 10, "bold"),
                 cursor="hand2").pack(side="left", padx=5)
        
        tk.Button(scrollable_frame, text="GERAR CHECKLIST EM PDF", 
                 command=self.gerar_pdf,
                 bg="#c0392b", fg="white", font=("Arial", 14, "bold"),
                 cursor="hand2", height=2).pack(fill="x", pady=15)
        
        tk.Label(scrollable_frame, 
                text="(C) 2025 " + EMPRESA_NOME + " - Todos os direitos reservados",
                font=("Arial", 8), bg="#f0f0f0", fg="#95a5a6").pack(pady=10)
    
    def preencher_data(self):
        self.entry_data.delete(0, tk.END)
        self.entry_data.insert(0, datetime.now().strftime("%d/%m/%Y"))
    
    def atualizar_lista_epis(self):
        """Atualiza lista de EPIs com campos EDITAVEIS de periodicidade"""
        for widget in self.frame_checkboxes.winfo_children():
            widget.destroy()
        
        self.checkboxes = {}
        self.entries_periodo = {}
        
        # Cabecalho da lista
        header_frame = tk.Frame(self.frame_checkboxes, bg="#34495e")
        header_frame.pack(fill="x")
        
        tk.Label(header_frame, text="  Sel.", font=("Arial", 9, "bold"), 
                bg="#34495e", fg="white", width=6).pack(side="left")
        tk.Label(header_frame, text="Nome do EPI", font=("Arial", 9, "bold"), 
                bg="#34495e", fg="white", width=45, anchor="w").pack(side="left")
        tk.Label(header_frame, text="Periodicidade (meses)", font=("Arial", 9, "bold"), 
                bg="#34495e", fg="white", width=18).pack(side="left")
        tk.Label(header_frame, text="Sugestao", font=("Arial", 9, "bold"), 
                bg="#34495e", fg="white", width=15).pack(side="left")
        
        # Lista dos EPIs
        for i, (epi, meses) in enumerate(sorted(EPIS_CADASTRADOS.items())):
            cor_fundo = "#ecf0f1" if i % 2 == 0 else "white"
            
            row_frame = tk.Frame(self.frame_checkboxes, bg=cor_fundo)
            row_frame.pack(fill="x")
            
            # Checkbox
            var = tk.BooleanVar()
            self.checkboxes[epi] = var
            
            cb = tk.Checkbutton(row_frame, variable=var, bg=cor_fundo)
            cb.pack(side="left", padx=10)
            
            # Nome do EPI
            tk.Label(row_frame, text=epi, bg=cor_fundo, font=("Arial", 9),
                    width=45, anchor="w").pack(side="left")
            
            # Campo EDITAVEL de periodicidade
            entry_frame = tk.Frame(row_frame, bg=cor_fundo)
            entry_frame.pack(side="left")
            
            entry_periodo = tk.Entry(entry_frame, font=("Arial", 10, "bold"), 
                                    width=8, justify="center",
                                    bg="#fff9e6", fg="#2c3e50",
                                    relief="solid", bd=1)
            entry_periodo.insert(0, str(meses))
            entry_periodo.pack(side="left", padx=5, pady=2)
            self.entries_periodo[epi] = entry_periodo
            
            # Rotulo "meses"
            tk.Label(entry_frame, text="meses", bg=cor_fundo, 
                    font=("Arial", 8), fg="#7f8c8d").pack(side="left", padx=2)
            
            # Sugestao (valor original salvo)
            texto_sugestao = "(" + str(meses) + " meses)"
            tk.Label(row_frame, text=texto_sugestao, bg=cor_fundo, 
                    font=("Arial", 8, "italic"), fg="#95a5a6", 
                    width=15).pack(side="left", padx=10)
    
    def salvar_periodicidades(self):
        """Salva as periodicidades alteradas pelo usuario"""
        alteracoes = 0
        erros = []
        
        for epi, entry in self.entries_periodo.items():
            try:
                novo_valor = int(entry.get().strip())
                if novo_valor <= 0:
                    erros.append(epi + " (valor deve ser maior que 0)")
                    continue
                
                if EPIS_CADASTRADOS.get(epi) != novo_valor:
                    EPIS_CADASTRADOS[epi] = novo_valor
                    alteracoes += 1
            except ValueError:
                erros.append(epi + " (valor invalido)")
        
        if erros:
            messagebox.showerror("Erros encontrados", 
                                "Corrija os seguintes EPIs:\n\n" + "\n".join(erros))
            return
        
        self.salvar_dados()
        self.atualizar_lista_epis()
        
        if alteracoes > 0:
            messagebox.showinfo("Sucesso", 
                              str(alteracoes) + " periodicidade(s) salva(s) com sucesso!")
        else:
            messagebox.showinfo("Info", "Nenhuma alteracao para salvar.")
    
    def adicionar_epi(self):
        janela = tk.Toplevel(self.root)
        janela.title("Adicionar Novo EPI")
        janela.geometry("400x280")
        janela.configure(bg="#f0f0f0")
        janela.transient(self.root)
        janela.grab_set()
        
        tk.Label(janela, text="+ Adicionar Novo EPI", 
                font=("Arial", 14, "bold"), bg="#f0f0f0", fg="#2c3e50").pack(pady=15)
        
        tk.Label(janela, text="Nome do EPI:", font=("Arial", 10, "bold"), 
                bg="#f0f0f0").pack(anchor="w", padx=30)
        entry_nome = tk.Entry(janela, font=("Arial", 11), width=40)
        entry_nome.pack(padx=30, pady=5)
        entry_nome.focus()
        
        tk.Label(janela, text="Periodicidade SUGERIDA (em meses):", 
                font=("Arial", 10, "bold"), bg="#f0f0f0").pack(anchor="w", padx=30, pady=(10,0))
        
        tk.Label(janela, text="(Voce podera alterar depois na tela principal)", 
                font=("Arial", 8, "italic"), bg="#f0f0f0", fg="#7f8c8d").pack(anchor="w", padx=30)
        
        entry_periodo = tk.Entry(janela, font=("Arial", 11), width=10)
        entry_periodo.pack(padx=30, pady=5, anchor="w")
        
        def salvar():
            nome = entry_nome.get().strip()
            try:
                periodo = int(entry_periodo.get().strip())
                if not nome:
                    messagebox.showerror("Erro", "Digite o nome do EPI!")
                    return
                if periodo <= 0:
                    messagebox.showerror("Erro", "Periodicidade deve ser maior que 0!")
                    return
                
                EPIS_CADASTRADOS[nome] = periodo
                self.salvar_dados()
                self.atualizar_lista_epis()
                messagebox.showinfo("Sucesso", "EPI '" + nome + "' adicionado com sucesso!")
                janela.destroy()
            except ValueError:
                messagebox.showerror("Erro", "Periodicidade deve ser um numero!")
        
        tk.Button(janela, text="SALVAR EPI", command=salvar,
                 bg="#27ae60", fg="white", font=("Arial", 11, "bold"),
                 cursor="hand2").pack(pady=20)
    
    def excluir_epi(self):
        selecionados = [epi for epi, var in self.checkboxes.items() if var.get()]
        
        if not selecionados:
            messagebox.showwarning("Aviso", "Selecione ao menos um EPI para excluir!")
            return
        
        resposta = messagebox.askyesno("Confirmar", 
                                       "Deseja excluir " + str(len(selecionados)) + " EPI(s) da lista?")
        if not resposta:
            return
        
        for epi in selecionados:
            if epi in EPIS_CADASTRADOS:
                del EPIS_CADASTRADOS[epi]
        
        self.salvar_dados()
        self.atualizar_lista_epis()
        messagebox.showinfo("Sucesso", str(len(selecionados)) + " EPI(s) excluido(s)!")
    
    def selecionar_todos(self):
        for var in self.checkboxes.values():
            var.set(True)
    
    def desmarcar_todos(self):
        for var in self.checkboxes.values():
            var.set(False)
    
    def gerar_pdf(self):
        nome = self.entry_nome.get().strip()
        cargo = self.combo_cargo.get().strip()
        setor = self.combo_setor.get().strip()
        data = self.entry_data.get().strip()
        matricula = self.entry_matricula.get().strip()
        
        # Pega EPIs selecionados COM as periodicidades ATUAIS dos campos editaveis
        epis_selecionados = []
        for epi, var in self.checkboxes.items():
            if var.get():
                try:
                    # Pega a periodicidade do campo editavel (nao do dicionario)
                    periodo = int(self.entries_periodo[epi].get().strip())
                    if periodo > 0:
                        epis_selecionados.append((epi, periodo))
                except:
                    # Se der erro, usa a periodicidade padrao
                    epis_selecionados.append((epi, EPIS_CADASTRADOS[epi]))
        
        if not epis_selecionados:
            messagebox.showerror("Erro", "Selecione ao menos um EPI!")
            return
        
        epis_selecionados.sort(key=lambda x: x[0])
        
        if nome:
            nome_arquivo_padrao = "Checklist_EPI_" + nome.replace(' ', '_') + "_" + datetime.now().strftime('%Y%m%d') + ".pdf"
        else:
            nome_arquivo_padrao = "Checklist_EPI_EmBranco_" + datetime.now().strftime('%Y%m%d_%H%M%S') + ".pdf"
        
        arquivo = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile=nome_arquivo_padrao,
            title="Salvar Checklist como..."
        )
        
        if not arquivo:
            return
        
        try:
            self.criar_pdf(arquivo, nome, cargo, setor, data, matricula, epis_selecionados)
            
            resposta = messagebox.askyesno("Sucesso!", 
                                          "PDF gerado com sucesso!\n\nDeseja abrir agora?")
            if resposta:
                os.startfile(arquivo)
        except Exception as e:
            messagebox.showerror("Erro", "Erro ao gerar PDF:\n" + str(e))
    
    def criar_pdf(self, arquivo, nome, cargo, setor, data, matricula, epis):
        """Cria PDF LIMPO - sem tarjas coloridas para economia de tinta"""
        c = canvas.Canvas(arquivo, pagesize=A4)
        largura, altura = A4
        
        # TITULO
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(largura/2, altura - 1.5*cm, "CHECKLIST DE PERIODICIDADE DE EPI")
        
        c.setFont("Helvetica", 10)
        c.drawCentredString(largura/2, altura - 2*cm, 
                          "Auditoria de Equipamentos de Protecao Individual")
        
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.line(1*cm, altura - 2.3*cm, largura - 1*cm, altura - 2.3*cm)
        
        # DADOS DO TRABALHADOR
        y = altura - 3*cm
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(1*cm, y, "DADOS DO TRABALHADOR")
        
        c.setLineWidth(0.5)
        c.line(1*cm, y - 0.2*cm, largura - 1*cm, y - 0.2*cm)
        
        # Nome
        y = y - 0.9*cm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(1*cm, y, "Nome:")
        if nome:
            c.setFont("Helvetica", 11)
            c.drawString(2.3*cm, y, nome)
        c.setStrokeColor(colors.HexColor("#666666"))
        c.setLineWidth(0.5)
        c.line(2.3*cm, y - 0.15*cm, largura - 1*cm, y - 0.15*cm)
        
        # Cargo e Setor
        y = y - 0.9*cm
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(1*cm, y, "Cargo:")
        if cargo:
            c.setFont("Helvetica", 11)
            c.drawString(2.5*cm, y, cargo)
        c.line(2.5*cm, y - 0.15*cm, 10*cm, y - 0.15*cm)
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(10.5*cm, y, "Setor:")
        if setor:
            c.setFont("Helvetica", 11)
            c.drawString(11.7*cm, y, setor)
        c.line(11.7*cm, y - 0.15*cm, largura - 1*cm, y - 0.15*cm)
        
        # Matricula e Data
        y = y - 0.9*cm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(1*cm, y, "Matricula:")
        if matricula:
            c.setFont("Helvetica", 11)
            c.drawString(3*cm, y, matricula)
        c.line(3*cm, y - 0.15*cm, 10*cm, y - 0.15*cm)
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(10.5*cm, y, "Data:")
        if data:
            c.setFont("Helvetica", 11)
            c.drawString(11.5*cm, y, data)
        c.line(11.5*cm, y - 0.15*cm, largura - 1*cm, y - 0.15*cm)
        
        # INSTRUCOES
        y = y - 1.3*cm
        c.setStrokeColor(colors.black)
        c.setLineWidth(0.5)
        c.rect(1*cm, y - 1.4*cm, largura - 2*cm, 1.4*cm, fill=0, stroke=1)
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(1.2*cm, y - 0.4*cm, "INSTRUCOES PARA PREENCHIMENTO:")
        c.setFont("Helvetica", 9)
        c.drawString(1.2*cm, y - 0.8*cm, 
                    "1. Para cada EPI, informe a DATA DA ULTIMA TROCA (dd/mm/aaaa)")
        c.drawString(1.2*cm, y - 1.15*cm, 
                    "2. Compare com a periodicidade e marque na coluna STATUS: OK ou VENCIDO")
        
        # TABELA DE EPIs
        y = y - 2.0*cm
        
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.rect(1*cm, y - 0.7*cm, largura - 2*cm, 0.7*cm, fill=0, stroke=1)
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(1.2*cm, y - 0.45*cm, "N")
        c.drawString(2*cm, y - 0.45*cm, "EPI")
        c.drawString(9.5*cm, y - 0.45*cm, "Periodicidade")
        c.drawString(12.5*cm, y - 0.45*cm, "Ultima Troca")
        c.drawString(16*cm, y - 0.45*cm, "Status")
        
        c.line(1.8*cm, y - 0.7*cm, 1.8*cm, y)
        c.line(9.3*cm, y - 0.7*cm, 9.3*cm, y)
        c.line(12.3*cm, y - 0.7*cm, 12.3*cm, y)
        c.line(15.8*cm, y - 0.7*cm, 15.8*cm, y)
        
        c.setFont("Helvetica", 9)
        y_linha = y - 0.7*cm
        altura_linha = 0.75*cm
        
        for i, (epi, meses) in enumerate(epis, 1):
            if y_linha - altura_linha < 4*cm:
                self.desenhar_rodape(c, largura)
                c.showPage()
                
                c.setFillColor(colors.black)
                c.setFont("Helvetica-Bold", 12)
                c.drawCentredString(largura/2, altura - 1.5*cm, 
                                   "CHECKLIST DE EPI - continuacao")
                c.line(1*cm, altura - 1.8*cm, largura - 1*cm, altura - 1.8*cm)
                
                y_linha = altura - 2.5*cm
                c.setStrokeColor(colors.black)
                c.setLineWidth(1)
                c.rect(1*cm, y_linha, largura - 2*cm, 0.7*cm, fill=0, stroke=1)
                c.setFont("Helvetica-Bold", 10)
                c.drawString(1.2*cm, y_linha + 0.25*cm, "N")
                c.drawString(2*cm, y_linha + 0.25*cm, "EPI")
                c.drawString(9.5*cm, y_linha + 0.25*cm, "Periodicidade")
                c.drawString(12.5*cm, y_linha + 0.25*cm, "Ultima Troca")
                c.drawString(16*cm, y_linha + 0.25*cm, "Status")
                
                c.line(1.8*cm, y_linha, 1.8*cm, y_linha + 0.7*cm)
                c.line(9.3*cm, y_linha, 9.3*cm, y_linha + 0.7*cm)
                c.line(12.3*cm, y_linha, 12.3*cm, y_linha + 0.7*cm)
                c.line(15.8*cm, y_linha, 15.8*cm, y_linha + 0.7*cm)
                
                c.setFont("Helvetica", 9)
            
            c.setStrokeColor(colors.black)
            c.setLineWidth(0.5)
            c.rect(1*cm, y_linha - altura_linha, 
                  largura - 2*cm, altura_linha, fill=0, stroke=1)
            
            c.line(1.8*cm, y_linha - altura_linha, 1.8*cm, y_linha)
            c.line(9.3*cm, y_linha - altura_linha, 9.3*cm, y_linha)
            c.line(12.3*cm, y_linha - altura_linha, 12.3*cm, y_linha)
            c.line(15.8*cm, y_linha - altura_linha, 15.8*cm, y_linha)
            
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(1.2*cm, y_linha - 0.45*cm, "%02d" % i)
            
            c.setFont("Helvetica", 9)
            epi_texto = epi if len(epi) < 55 else epi[:52] + "..."
            c.drawString(2*cm, y_linha - 0.45*cm, epi_texto)
            
            texto_periodo = str(meses) + " " + ("mes" if meses == 1 else "meses")
            c.drawString(9.5*cm, y_linha - 0.45*cm, texto_periodo)
            
            y_linha -= altura_linha
        
        # ASSINATURAS
        if y_linha < 5*cm:
            self.desenhar_rodape(c, largura)
            c.showPage()
            y_linha = altura - 3*cm
        
        y_ass = y_linha - 2*cm
        
        c.setStrokeColor(colors.black)
        c.setLineWidth(0.5)
        
        c.line(2*cm, y_ass, 9*cm, y_ass)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(5.5*cm, y_ass - 0.4*cm, "Assinatura do Trabalhador")
        
        c.line(12*cm, y_ass, 19*cm, y_ass)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(15.5*cm, y_ass - 0.4*cm, "Tecnico em Seguranca do Trabalho")
        
        self.desenhar_rodape(c, largura)
        
        c.save()
    
    def desenhar_rodape(self, c, largura):
        """Rodape sutil e pequeno - economia de tinta"""
        c.setStrokeColor(colors.HexColor("#999999"))
        c.setLineWidth(0.3)
        c.line(1*cm, 1*cm, largura - 1*cm, 1*cm)
        
        c.setFillColor(colors.HexColor("#666666"))
        c.setFont("Helvetica", 7)
        c.drawCentredString(largura/2, 0.6*cm, 
                          EMPRESA_NOME + " | Documento gerado em " + datetime.now().strftime('%d/%m/%Y'))
        c.setFont("Helvetica-Oblique", 6)
        c.drawCentredString(largura/2, 0.3*cm, 
                          "Auditoria de EPI - Seguranca do Trabalho")


if __name__ == "__main__":
    root = tk.Tk()
    app = ChecklistEPI(root)
    root.mainloop()
