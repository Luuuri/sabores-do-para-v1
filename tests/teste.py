""""from app.utils.componentes import Frames, TabelaGenerica
import customtkinter as ctk
from app.utils.estilos import Cores, Fontes, Icones

root = ctk.CTk()
root.geometry("1100x700")

cores = Cores()
fontes = Fontes()
icones = Icones()

layout = Frames.FrameLayoutPadrao(root, cores, fontes, icones,
                                  titulo="Funcionários")
layout.pack(expand=True, fill="both")

frames = Frames.FrameConteudoTabela(layout, cores)
frames.pack(expand=True, fill="both", padx=100, pady=70)

frame = TabelaGenerica(frames, cores, fontes, icones,
                       colunas=[("Nome", "nome"), ("Descrição", "descricao")],
                       mostrar_busca=True, mostrar_filtros=True)
frame.pack(expand=True, fill="both", padx=20,pady=20)


root.mainloop()"""




import customtkinter as ctk
from tkinter import messagebox

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class StatusBadge(ctk.CTkFrame):
    COLORS = {
        "OK":     ("#2ecc71", "#27ae60"),
        "Baixo":  ("#f39c12", "#e67e22"),
        "Zerado": ("#e74c3c", "#c0392b"),
    }

    def __init__(self, master, status: str, **kwargs):
        colors = self.COLORS.get(status, ("#95a5a6", "#7f8c8d"))
        super().__init__(master, fg_color=colors[0], corner_radius=12,
                         width=70, height=26, **kwargs)
        self.grid_propagate(False)
        label = ctk.CTkLabel(self, text=status, text_color="white",
                             font=ctk.CTkFont(size=12, weight="bold"))
        label.place(relx=0.5, rely=0.5, anchor="center")


class QuantityControl(ctk.CTkFrame):
    def __init__(self, master, initial: int, on_change=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._value = initial
        self._on_change = on_change

        btn_minus = ctk.CTkButton(self, text="−", width=26, height=26,
                                  corner_radius=13, fg_color="#e74c3c",
                                  hover_color="#c0392b",
                                  font=ctk.CTkFont(size=14, weight="bold"),
                                  command=self._decrement)
        btn_minus.grid(row=0, column=0, padx=(0, 4))

        self._label = ctk.CTkLabel(self, text=str(self._value),
                                   font=ctk.CTkFont(size=13, weight="bold"),
                                   width=30, anchor="center")
        self._label.grid(row=0, column=1)

        btn_plus = ctk.CTkButton(self, text="+", width=26, height=26,
                                 corner_radius=13, fg_color="#2ecc71",
                                 hover_color="#27ae60",
                                 font=ctk.CTkFont(size=14, weight="bold"),
                                 command=self._increment)
        btn_plus.grid(row=0, column=2, padx=(4, 0))

    def _increment(self):
        self._value += 1
        self._label.configure(text=str(self._value))
        if self._on_change:
            self._on_change(self._value)

    def _decrement(self):
        if self._value > 0:
            self._value -= 1
            self._label.configure(text=str(self._value))
            if self._on_change:
                self._on_change(self._value)


class AddItemDialog(ctk.CTkToplevel):
    CATEGORIAS = ["Ingredientes", "Bebidas", "Descartáveis", "Limpeza", "Outros"]
    UNIDADES = ["KG", "UN", "L", "G", "CX", "PCT"]

    def __init__(self, master, on_save, item=None):
        super().__init__(master)
        self.on_save = on_save
        self.item = item
        self.title("Novo Item" if item is None else "Editar Item")
        self.geometry("400x420")
        self.resizable(False, False)
        self.grab_set()

        pad = {"padx": 20, "pady": 6}

        ctk.CTkLabel(self, text="Nome do Item", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=20, pady=(20, 2))
        self.nome_entry = ctk.CTkEntry(self, placeholder_text="Ex: Farinha", width=360, height=38)
        self.nome_entry.pack(**pad)

        ctk.CTkLabel(self, text="Subtítulo (opcional)", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=20, pady=(4, 2))
        self.sub_entry = ctk.CTkEntry(self, placeholder_text="Ex: Lata, 350ml...", width=360, height=38)
        self.sub_entry.pack(**pad)

        ctk.CTkLabel(self, text="Categoria", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=20, pady=(4, 2))
        self.cat_var = ctk.StringVar(value=self.CATEGORIAS[0])
        self.cat_menu = ctk.CTkOptionMenu(self, variable=self.cat_var, values=self.CATEGORIAS, width=360)
        self.cat_menu.pack(**pad)

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=6)

        left = ctk.CTkFrame(row, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkLabel(left, text="Quantidade", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 2))
        self.qty_entry = ctk.CTkEntry(left, placeholder_text="0", height=38)
        self.qty_entry.pack(fill="x")

        right = ctk.CTkFrame(row, fg_color="transparent")
        right.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(right, text="Unidade", font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 2))
        self.unit_var = ctk.StringVar(value=self.UNIDADES[0])
        self.unit_menu = ctk.CTkOptionMenu(right, variable=self.unit_var, values=self.UNIDADES)
        self.unit_menu.pack(fill="x")

        if item:
            self.nome_entry.insert(0, item.get("nome", ""))
            self.sub_entry.insert(0, item.get("sub", ""))
            self.cat_var.set(item.get("categoria", self.CATEGORIAS[0]))
            self.qty_entry.insert(0, str(item.get("quantidade", 0)))
            self.unit_var.set(item.get("unidade", "UN"))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(10, 20))
        ctk.CTkButton(btn_frame, text="Cancelar", width=160, height=38,
                      fg_color="#e0e0e0", text_color="#333", hover_color="#cccccc",
                      command=self.destroy).pack(side="left")
        ctk.CTkButton(btn_frame, text="Salvar", width=160, height=38,
                      fg_color="#1a1a1a", hover_color="#333",
                      command=self._save).pack(side="right")

    def _save(self):
        nome = self.nome_entry.get().strip()
        if not nome:
            messagebox.showwarning("Atenção", "O nome do item é obrigatório.", parent=self)
            return
        try:
            qty = int(self.qty_entry.get() or 0)
        except ValueError:
            messagebox.showwarning("Atenção", "Quantidade deve ser um número inteiro.", parent=self)
            return

        self.on_save({
            "nome": nome,
            "sub": self.sub_entry.get().strip(),
            "categoria": self.cat_var.get(),
            "quantidade": qty,
            "unidade": self.unit_var.get(),
        })
        self.destroy()


def status_from_qty(qty: int) -> str:
    if qty == 0:
        return "Zerado"
    elif qty <= 5:
        return "Baixo"
    return "OK"


class EstoqueApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Estoque")
        self.geometry("960x620")
        self.minsize(720, 500)
        self.configure(fg_color="#f0f0f0")

        self._items = [
            {"nome": "Farinha",    "sub": "",       "categoria": "Ingredientes",  "quantidade": 10, "unidade": "KG"},
            {"nome": "Coca-Cola",  "sub": "Lata",   "categoria": "Bebidas",       "quantidade": 5,  "unidade": "UN"},
            {"nome": "Copo",       "sub": "350 ml", "categoria": "Descartáveis",  "quantidade": 0,  "unidade": "UN"},
        ]

        self._build_header()
        self._build_body()
        self._render_rows()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="white", corner_radius=0, height=64)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkButton(header, text="🏠", width=40, height=40, corner_radius=8,
                      fg_color="transparent", hover_color="#f0f0f0",
                      font=ctk.CTkFont(size=20)).pack(side="left", padx=(16, 4), pady=12)

        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", padx=6)
        ctk.CTkLabel(title_frame, text="📦", font=ctk.CTkFont(size=18)).pack(side="left", padx=(0, 6))
        ctk.CTkLabel(title_frame, text="Estoque",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#1a1a1a").pack(side="left")

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right", padx=16)

        ctk.CTkButton(right, text="⚙", width=38, height=38, corner_radius=8,
                      fg_color="transparent", hover_color="#f0f0f0",
                      font=ctk.CTkFont(size=18), text_color="#555").pack(side="right", padx=(8, 0))

        ctk.CTkButton(right, text="+ Novo Item", height=38, corner_radius=10,
                      fg_color="#1a1a1a", hover_color="#333",
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._open_add_dialog).pack(side="right")

    def _build_body(self):
        body = ctk.CTkFrame(self, fg_color="#f0f0f0")
        body.pack(fill="both", expand=True, padx=24, pady=16)

        top = ctk.CTkFrame(body, fg_color="transparent")
        top.pack(fill="x", pady=(0, 12))

        search_frame = ctk.CTkFrame(top, fg_color="white", corner_radius=10,
                                    border_width=1, border_color="#ddd")
        search_frame.pack(side="left")
        ctk.CTkLabel(search_frame, text="🔍", font=ctk.CTkFont(size=14),
                     text_color="#999").pack(side="left", padx=(10, 2))
        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._render_rows())
        self._search_entry = ctk.CTkEntry(search_frame, placeholder_text="Buscar Item...",
                                          width=200, height=36, border_width=0,
                                          fg_color="transparent",
                                          textvariable=self._search_var)
        self._search_entry.pack(side="left", padx=(0, 8))

        ctk.CTkButton(top, text="⊟", width=36, height=36, corner_radius=8,
                      fg_color="white", text_color="#555", hover_color="#e0e0e0",
                      border_width=1, border_color="#ddd",
                      font=ctk.CTkFont(size=16)).pack(side="left", padx=(8, 0))

        self._table_frame = ctk.CTkScrollableFrame(body, fg_color="white",
                                                   corner_radius=12)
        self._table_frame.pack(fill="both", expand=True)
        self._table_frame.columnconfigure(0, weight=3)
        self._table_frame.columnconfigure(1, weight=2)
        self._table_frame.columnconfigure(2, weight=2)
        self._table_frame.columnconfigure(3, weight=1)
        self._table_frame.columnconfigure(4, weight=2)
        self._table_frame.columnconfigure(5, weight=1)

        self._build_column_headers()

    def _build_column_headers(self):
        f = self._table_frame
        header_opts = dict(font=ctk.CTkFont(size=12, weight="bold"),
                           text_color="#888", anchor="w")
        ctk.CTkLabel(f, text="Item ▾",       **header_opts).grid(row=0, column=0, sticky="w", padx=(16, 8), pady=(12, 4))
        ctk.CTkLabel(f, text="Categoria ▾",  **header_opts).grid(row=0, column=1, sticky="w", padx=8, pady=(12, 4))
        ctk.CTkLabel(f, text="Quantidade ▾", **header_opts).grid(row=0, column=2, sticky="w", padx=8, pady=(12, 4))
        ctk.CTkLabel(f, text="Unidade ▾",    **header_opts).grid(row=0, column=3, sticky="w", padx=8, pady=(12, 4))
        ctk.CTkLabel(f, text="Status ▾",     **header_opts).grid(row=0, column=4, sticky="w", padx=8, pady=(12, 4))
        ctk.CTkLabel(f, text="Ações",        **header_opts).grid(row=0, column=5, sticky="w", padx=8, pady=(12, 4))

        sep = ctk.CTkFrame(f, fg_color="#e8e8e8", height=1)
        sep.grid(row=1, column=0, columnspan=6, sticky="ew", padx=8)

    def _render_rows(self):
        f = self._table_frame
        for widget in f.winfo_children():
            info = widget.grid_info()
            if info and int(info.get("row", 0)) >= 2:
                widget.destroy()

        query = self._search_var.get().lower().strip()
        filtered = [
            (i, item) for i, item in enumerate(self._items)
            if query in item["nome"].lower() or query in item["categoria"].lower()
        ] if query else list(enumerate(self._items))

        for row_idx, (real_idx, item) in enumerate(filtered):
            grid_row = row_idx * 2 + 2
            bg = "#fafafa" if row_idx % 2 == 0 else "white"

            name_frame = ctk.CTkFrame(f, fg_color="transparent")
            ctk.CTkLabel(name_frame, text=item["nome"],
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color="#1a1a1a", anchor="w").pack(anchor="w")
            if item.get("sub"):
                ctk.CTkLabel(name_frame, text=item["sub"],
                             font=ctk.CTkFont(size=11), text_color="#999",
                             anchor="w").pack(anchor="w")
            name_frame.grid(row=grid_row, column=0, sticky="w", padx=(16, 8), pady=10)

            ctk.CTkLabel(f, text=item["categoria"],
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color="#1a1a1a").grid(row=grid_row, column=1,
                                                     sticky="w", padx=8, pady=10)

            qty_ctrl = QuantityControl(f, item["quantidade"],
                                       on_change=lambda v, idx=real_idx: self._qty_changed(idx, v))
            qty_ctrl.grid(row=grid_row, column=2, sticky="w", padx=8, pady=10)

            ctk.CTkLabel(f, text=item["unidade"],
                         font=ctk.CTkFont(size=13),
                         text_color="#555").grid(row=grid_row, column=3,
                                                  sticky="w", padx=8, pady=10)

            StatusBadge(f, status_from_qty(item["quantidade"])).grid(
                row=grid_row, column=4, sticky="w", padx=8, pady=10)

            action_frame = ctk.CTkFrame(f, fg_color="transparent")
            ctk.CTkButton(action_frame, text="✏", width=30, height=30,
                          corner_radius=6, fg_color="transparent",
                          hover_color="#f0f0f0", text_color="#555",
                          font=ctk.CTkFont(size=15),
                          command=lambda idx=real_idx: self._edit_item(idx)).pack(side="left")
            ctk.CTkButton(action_frame, text="🗑", width=30, height=30,
                          corner_radius=6, fg_color="transparent",
                          hover_color="#ffe0e0", text_color="#e74c3c",
                          font=ctk.CTkFont(size=15),
                          command=lambda idx=real_idx: self._delete_item(idx)).pack(side="left")
            action_frame.grid(row=grid_row, column=5, sticky="w", padx=8, pady=10)

            sep = ctk.CTkFrame(f, fg_color="#eeeeee", height=1)
            sep.grid(row=grid_row + 1, column=0, columnspan=6, sticky="ew", padx=8)

    def _qty_changed(self, idx: int, value: int):
        self._items[idx]["quantidade"] = value
        self._render_rows()

    def _open_add_dialog(self):
        AddItemDialog(self, on_save=self._save_new_item)

    def _save_new_item(self, data: dict):
        self._items.append(data)
        self._render_rows()

    def _edit_item(self, idx: int):
        AddItemDialog(self, on_save=lambda d, i=idx: self._save_edit(i, d),
                      item=self._items[idx])

    def _save_edit(self, idx: int, data: dict):
        self._items[idx] = data
        self._render_rows()

    def _delete_item(self, idx: int):
        nome = self._items[idx]["nome"]
        if messagebox.askyesno("Confirmar exclusão",
                               f'Tem certeza que deseja excluir "{nome}"?',
                               parent=self):
            del self._items[idx]
            self._render_rows()


if __name__ == "__main__":
    app = EstoqueApp()
    app.mainloop()
