from tkinter import *
import customtkinter
from customtkinter import *
from tkinter import messagebox
import sqlite3


def create_tables():
    db_conn = sqlite3.connect("estoque.db")
    db_cursor = db_conn.cursor()
    
    db_cursor.execute('''CREATE TABLE IF NOT EXISTS sessoes (
                                id INTEGER PRIMARY KEY,
                                nome TEXT NOT NULL)''')
    
    db_cursor.execute('''CREATE TABLE IF NOT EXISTS produtos (
                                id INTEGER PRIMARY KEY,
                                nome TEXT NOT NULL,
                                sessao_id INTEGER NOT NULL,
                                FOREIGN KEY(sessao_id) REFERENCES sessoes(id))''')
    
    db_cursor.execute('''CREATE TABLE IF NOT EXISTS estoque (
                                id INTEGER PRIMARY KEY,
                                produto_id INTEGER NOT NULL,
                                quantidade INTEGER NOT NULL,
                                FOREIGN KEY(produto_id) REFERENCES produtos(id))''')
    
    db_conn.commit()
    db_conn.close()


def obter_sessoes():
    db_conn = sqlite3.connect("estoque.db")
    db_cursor = db_conn.cursor()
    
    db_cursor.execute("SELECT id, nome FROM sessoes")
    sessoes = db_cursor.fetchall()
    
    db_conn.close()
    return sessoes


def adicionar_sessao(entry_sessao, lista_estoque):
    sessao = entry_sessao.get()
    
    if sessao:
        db_conn = sqlite3.connect("estoque.db")
        db_cursor = db_conn.cursor()
        
        try:
            # Verificar se a sessão já existe
            db_cursor.execute("SELECT id FROM sessoes WHERE nome=?", (sessao,))
            sessao_info = db_cursor.fetchone()
            if not sessao_info:
                # Se a seção não existir, adicioná-la
                db_cursor.execute("INSERT INTO sessoes (nome) VALUES (?)", (sessao,))
                db_conn.commit()
            else:
                messagebox.showwarning("Aviso", "Esta sessão já existe.")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
        
        db_conn.close()
        mostrar_estoque(lista_estoque)
        entry_sessao.delete(0, END)
    else:
        messagebox.showerror("Erro", "Por favor, preencha o campo de sessão.")


def adicionar_produto(entry_produto, entry_quantidade, entry_sessao, lista_estoque): 
    produto = entry_produto.get()
    quantidade = entry_quantidade.get()
    sessao = entry_sessao.get()
    
    if produto and quantidade and sessao:
        db_conn = sqlite3.connect("estoque.db")
        
        db_cursor = db_conn.cursor()
        
        # Verificar se a sessão existe
        db_cursor.execute("SELECT id FROM sessoes WHERE nome=?", (sessao,))
        sessao_info = db_cursor.fetchone()
        if not sessao_info:
            messagebox.showwarning("Erro", "A sessão especificada não existe.")
            db_conn.close()
            
            return
        
        sessao_id = sessao_info[0]
        
        if produto and quantidade:
            # Verificar se o produto existe na seção
            db_cursor.execute("SELECT id FROM produtos WHERE nome=? AND sessao_id=?", (produto, sessao_id))
            produto_info = db_cursor.fetchone()
            if not produto_info:
                # Se o produto não existir na seção, adicioná-lo
                db_cursor.execute("INSERT INTO produtos (nome, sessao_id) VALUES (?, ?)", (produto, sessao_id))
                produto_id = db_cursor.lastrowid
            else:
                produto_id = produto_info[0]
            
            # Verificar se o produto já existe no estoque
            db_cursor.execute("SELECT quantidade FROM estoque WHERE produto_id=?", (produto_id,))
            quantidade_existente = db_cursor.fetchone()
            
            if quantidade_existente:
                nova_quantidade = quantidade_existente[0] + int(quantidade)
                db_cursor.execute("UPDATE estoque SET quantidade=? WHERE produto_id=?", (nova_quantidade, produto_id))
            else:
                db_cursor.execute("INSERT INTO estoque (produto_id, quantidade) VALUES (?, ?)",
                                  (produto_id, quantidade))   
        
        db_conn.commit()
        db_conn.close()
        
        mostrar_estoque(lista_estoque)
        entry_produto.delete(0, END)
        entry_quantidade.delete(0, END)
        entry_sessao.delete(0, END)
    else:
        messagebox.showwarning("Erro", "Por favor, preencha todos os campos.")

def remover_qtd(entry_produto, entry_quantidade, entry_sessao, lista_estoque):
    produto = entry_produto.get()
    quantidade = entry_quantidade.get()
    sessao = entry_sessao.get()
    
    if produto and quantidade and sessao:
        db_conn = sqlite3.connect("estoque.db")
        db_cursor = db_conn.cursor()
        
        # Verificar se a sessão existe
        db_cursor.execute("SELECT id FROM sessoes WHERE nome=?", (sessao,))
        sessao_info = db_cursor.fetchone()
        if not sessao_info:
            messagebox.showwarning("Erro", "A sessão especificada não existe.")
            db_conn.close()
            return
        
        sessao_id = sessao_info[0]
        
        # Verificar se o produto existe na sessão
        db_cursor.execute("SELECT id FROM produtos WHERE nome=? AND sessao_id=?", (produto, sessao_id))
        produto_info = db_cursor.fetchone()
        if not produto_info:
            messagebox.showwarning("Erro", "O produto especificado não existe na sessão.")
            db_conn.close()
            return
        
        produto_id = produto_info[0]
        
        # Verificar a quantidade existente no estoque
        db_cursor.execute("SELECT quantidade FROM estoque WHERE produto_id=?", (produto_id,))
        quantidade_existente = db_cursor.fetchone()
        
        if quantidade_existente:
            nova_quantidade = quantidade_existente[0] - int(quantidade)
            if nova_quantidade < 0:
                messagebox.showwarning("Erro", "A quantidade a remover é maior que a quantidade disponível no estoque.")
                db_conn.close()
                return
            
            db_cursor.execute("UPDATE estoque SET quantidade=? WHERE produto_id=?", (nova_quantidade, produto_id))
            
            if nova_quantidade == 0:
                db_cursor.execute("UPDATE estoque SET quantidade=0 WHERE produto_id=?", (produto_id,))
        
        db_conn.commit()
        db_conn.close()
        
        mostrar_estoque(lista_estoque)
        entry_produto.delete(0, END)
        entry_quantidade.delete(0, END)
        entry_sessao.delete(0, END)
    else:
        messagebox.showwarning("Erro", "Por favor, preencha todos os campos.")


def mostrar_estoque(lista_estoque):
    lista_estoque.delete(0, END)
    
    sessoes = obter_sessoes()
    
    if not sessoes:
        lista_estoque.insert(END, "Nenhuma sessão encontrada.")
        return
    
    for sessao in sessoes:
        lista_estoque.insert(END, (f" "))
        lista_estoque.insert(END, (f"------------------------------ {sessao[1]} ------------------------------ "))
        lista_estoque.insert(END, (f" "))
        
        db_conn = sqlite3.connect("estoque.db")
        db_cursor = db_conn.cursor()
        
        db_cursor.execute(
            "SELECT produtos.nome, estoque.quantidade FROM produtos INNER JOIN estoque ON produtos.id = estoque.produto_id WHERE produtos.sessao_id=?",
            (sessao[0],))
        produtos = db_cursor.fetchall()
        
        if not produtos:
            lista_estoque.insert(END, "Nenhum produto encontrado nesta sessão.")
        else:
            for produto in produtos:
                lista_estoque.insert(END, (f"{produto[0]} > {produto[1]} unidades"))
        
        db_conn.close()
    
def remover_sessao(entry_sessao, lista_estoque):
        sessao = entry_sessao.get()
        
        if sessao:
            db_conn = sqlite3.connect("estoque.db")
            db_cursor = db_conn.cursor()
            
            db_cursor.execute("SELECT id FROM sessoes WHERE nome=?", (sessao,))
            sessao_info = db_cursor.fetchone()
            if sessao_info:
                sessao_id = sessao_info[0]
                db_cursor.execute("DELETE FROM estoque WHERE produto_id IN (SELECT id FROM produtos WHERE sessao_id=?)",
                                  (sessao_id,))
                db_cursor.execute("DELETE FROM produtos WHERE sessao_id=?", (sessao_id,))
                db_cursor.execute("DELETE FROM sessoes WHERE id=?", (sessao_id,))
                db_conn.commit()
                db_conn.close()
                mostrar_estoque(lista_estoque)
                entry_sessao.delete(0, END)
            else:
                messagebox.showerror("Erro", "A sessão especificada não existe.")
        else:
            messagebox.showerror("Erro", "Por favor, especifique a sessão que deseja remover.")


def remover_produto(entry_produto, entry_sessao, entry_quantidade, lista_estoque):
    produto = entry_produto.get()
    
    if produto:
        db_conn = sqlite3.connect("estoque.db")
        db_cursor = db_conn.cursor()
        db_cursor.execute("SELECT id FROM produtos WHERE nome=?", (produto,))
        produto_info = db_cursor.fetchone()
        
        if produto_info:
            produto_id = produto_info[0]
            db_cursor.execute("DELETE FROM estoque WHERE produto_id=?", (produto_id,))
            db_cursor.execute("DELETE FROM produtos WHERE id=?", (produto_id,))

            db_conn.commit()
            db_conn.close()
            mostrar_estoque(lista_estoque)
            entry_sessao.delete(0, END)
            entry_produto.delete(0, END)
            entry_quantidade.delete(0, END)
        else:
            messagebox.showerror("Erro", "O produto especificado não existe.")
    else:
        messagebox.showerror("Erro", "Por favor, especifique o produto que deseja remover.") 


def remover_sessao(entry_sessao, entry_produto, entry_quantidade, lista_estoque):
    sessao = entry_sessao.get()
    
    if sessao:
        db_conn = sqlite3.connect("estoque.db")
        db_cursor = db_conn.cursor()
        
        db_cursor.execute("SELECT id FROM sessoes WHERE nome=?", (sessao,))
        sessao_info = db_cursor.fetchone()
        if sessao_info:
            sessao_id = sessao_info[0]
            db_cursor.execute("DELETE FROM estoque WHERE produto_id IN (SELECT id FROM produtos WHERE sessao_id=?)",
                              (sessao_id,))
            db_cursor.execute("DELETE FROM produtos WHERE sessao_id=?", (sessao_id,))
            db_cursor.execute("DELETE FROM sessoes WHERE id=?", (sessao_id,))
            db_conn.commit()
            db_conn.close()
            mostrar_estoque(lista_estoque)
            entry_sessao.delete(0, END)
            entry_produto.delete(0, END)
            entry_quantidade.delete(0, END)
        else:
            messagebox.showerror("Erro", "A sessão especificada não existe.")
    else:
        messagebox.showerror("Erro", "Por favor, especifique a sessão que deseja remover.")


def carregar_produto_selecionado(event, lista_estoque, entry_produto, entry_quantidade, entry_sessao):

    selected_item = lista_estoque.curselection()

    if not selected_item:
        return
    
    index = selected_item[0]
    item_text = lista_estoque.get(index)

    
    
    if " > " in item_text:
        produto_nome, quantidade_text = item_text.split(" > ")
        quantidade = quantidade_text.split(" ")[0]
        
        db_conn = sqlite3.connect("estoque.db")
        db_cursor = db_conn.cursor()
        
        db_cursor.execute(
            "SELECT sessoes.nome FROM produtos INNER JOIN sessoes ON produtos.sessao_id = sessoes.id WHERE produtos.nome=?",
            (produto_nome,))
        sessao_nome = db_cursor.fetchone()
        
        db_conn.close()

        if sessao_nome:
            entry_produto.delete(0, END)
            entry_produto.insert(0, produto_nome)
            
            entry_quantidade.delete(0, END)
            entry_quantidade.insert(0, quantidade)
            
            entry_sessao.delete(0, END)
            entry_sessao.insert(0, sessao_nome[0])
    else:
        sessao_nome = item_text.replace('-', '')
        sessao_nome = sessao_nome.replace(' ', '')
        entry_sessao.delete(0, END)
        entry_sessao.insert(0, sessao_nome)
        entry_produto.delete(0, END)
        entry_quantidade.delete(0, END)

def main():
    root = CTk()
    root.title("Estoque Projeto Vidas - Vassouras")
    root.iconbitmap("icon.ico")
    root.geometry('600x600')
    customtkinter.set_appearance_mode('dark')
    customtkinter.set_default_color_theme('dark-blue')
    root.resizable(False, False)
    
    create_tables()
    
    label_produto = CTkLabel(root, text="Produto", font=("Arial", 15))
    label_produto.place(x=65, y=10)
    
    entry_produto = CTkEntry(root, font=("Arial", 15), width=200)
    entry_produto.place(x=65, y=45)
    
    label_quantidade = CTkLabel(root, text="Quantidade", font=("Arial", 15))
    label_quantidade.place(x=65, y=100)
    
    entry_quantidade = CTkEntry(root, font=("Arial", 15), width=200)
    entry_quantidade.place(x=65, y=135)
    
    label_sessao = CTkLabel(root, text="Sessão", font=("Arial", 15))
    label_sessao.place(x=65, y=190)
    
    entry_sessao = CTkEntry(root, font=("Arial", 15), width=200)
    entry_sessao.place(x=65, y=225)
    
    btn_adicionar = CTkButton(root, text="Adicionar Produto", font=("Arial", 15), width=155,
                              command=lambda: adicionar_produto(entry_produto, entry_quantidade, entry_sessao,
                                                                lista_estoque))
    btn_adicionar.place(x=360, y=45)

    btn_remover_qtd = CTkButton(root, text="Remover Quantidade", font=("Arial", 15), width=155,
                              command=lambda: remover_qtd(entry_produto, entry_quantidade, entry_sessao,
                                                            lista_estoque))

    btn_remover_qtd.place(x=360, y=90)
    
    btn_remover = CTkButton(root, text="Remover Produto", font=("Arial", 15), width=155,
                            command=lambda: remover_produto(entry_produto, entry_sessao, entry_quantidade, lista_estoque))
    
    btn_remover.place(x=360, y=135)
    
    btn_adicionar_sessao = CTkButton(root, text="Adicionar Sessão", font=("Arial", 15), width=155,
                                     command=lambda: adicionar_sessao(entry_sessao, lista_estoque))
    btn_adicionar_sessao.place(x=360, y=180)
    
    btn_remover_sessao = CTkButton(root, text="Remover Sessão", font=("Arial", 15), width=155,
                                   command=lambda: remover_sessao(entry_sessao, entry_produto, entry_quantidade,
                                                                  lista_estoque))
    btn_remover_sessao.place(x=360, y=225)
    
    lista_estoque = Listbox(root, font=("Arial", 13), height=15, width=70)
    lista_estoque.pack(side='bottom', expand=False, pady=20, padx=20, fill='x')

    lista_estoque.bind('<<ListboxSelect>>',
                       lambda event: carregar_produto_selecionado(event, lista_estoque, entry_produto, entry_quantidade,
                                                                  entry_sessao))
    
    mostrar_estoque(lista_estoque)
    
    root.mainloop()


if __name__ == "__main__":
    main()
