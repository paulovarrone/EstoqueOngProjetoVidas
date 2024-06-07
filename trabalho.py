import tkinter as tk
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
                # Se a sessão não existir, adicioná-la
                db_cursor.execute("INSERT INTO sessoes (nome) VALUES (?)", (sessao,))
                db_conn.commit()
            else:
                messagebox.showwarning("Aviso", "Esta sessão já existe.")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
        
        db_conn.close()
        mostrar_estoque(lista_estoque)
        entry_sessao.delete(0, tk.END)
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
            # Verificar se o produto existe na sessão
            db_cursor.execute("SELECT id FROM produtos WHERE nome=? AND sessao_id=?", (produto, sessao_id))
            produto_info = db_cursor.fetchone()
            if not produto_info:
                # Se o produto não existir na sessão, adicioná-lo
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
                db_cursor.execute("INSERT INTO estoque (produto_id, quantidade) VALUES (?, ?)", (produto_id, quantidade))
                nova_quantidade = int(quantidade)

            if nova_quantidade == -1:
                # Se a nova quantidade for -1, remover o produto
                db_cursor.execute("DELETE FROM estoque WHERE produto_id=?", (produto_id,))
                db_cursor.execute("DELETE FROM produtos WHERE id=?", (produto_id,))
            elif nova_quantidade == 0:
                db_cursor.execute("UPDATE estoque SET quantidade=0 WHERE produto_id=?", (produto_id,))
            
        db_conn.commit()
        db_conn.close()

        mostrar_estoque(lista_estoque)
        entry_produto.delete(0, tk.END)
        entry_quantidade.delete(0, tk.END)
        entry_sessao.delete(0, tk.END)
    else:
        messagebox.showwarning("Erro", "Por favor, preencha todos os campos.")

def mostrar_estoque(lista_estoque):
    lista_estoque.delete(0, tk.END)

    sessoes = obter_sessoes()
    
    if not sessoes:
        lista_estoque.insert(tk.END, "Nenhuma sessão encontrada.")
        return

    for sessao in sessoes:
        lista_estoque.insert(tk.END, (f" "))
        lista_estoque.insert(tk.END, (f"------------------------------ {sessao[1]} ------------------------------ "))
        lista_estoque.insert(tk.END, (f" "))
        
        db_conn = sqlite3.connect("estoque.db")
        db_cursor = db_conn.cursor()

        db_cursor.execute("SELECT produtos.nome, estoque.quantidade FROM produtos INNER JOIN estoque ON produtos.id = estoque.produto_id WHERE produtos.sessao_id=?", (sessao[0],))
        produtos = db_cursor.fetchall()

        if not produtos:
            lista_estoque.insert(tk.END, "Nenhum produto encontrado nesta sessão.")
        else:
            for produto in produtos:
                lista_estoque.insert(tk.END, (f"{produto[0]} > {produto[1]} unidades"))

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
            db_cursor.execute("DELETE FROM estoque WHERE produto_id IN (SELECT id FROM produtos WHERE sessao_id=?)", (sessao_id,))
            db_cursor.execute("DELETE FROM produtos WHERE sessao_id=?", (sessao_id,))
            db_cursor.execute("DELETE FROM sessoes WHERE id=?", (sessao_id,))
            db_conn.commit()
            db_conn.close()
            mostrar_estoque(lista_estoque)
            entry_sessao.delete(0, tk.END)
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
        
        db_cursor.execute("SELECT sessoes.nome FROM produtos INNER JOIN sessoes ON produtos.sessao_id = sessoes.id WHERE produtos.nome=?", (produto_nome,))
        sessao_nome = db_cursor.fetchone()
        
        db_conn.close()
        
        if sessao_nome:
            entry_produto.delete(0, tk.END)
            entry_produto.insert(0, produto_nome)
            
            entry_quantidade.delete(0, tk.END)
            entry_quantidade.insert(0, quantidade)
            
            entry_sessao.delete(0, tk.END)
            entry_sessao.insert(0, sessao_nome[0])

def main():
    root = tk.Tk()
    root.title("Sistema de Estoque")

    # root.iconbitmap("./un.ico")
    root['bg'] = '#0b5884'
    root.resizable(0, 0)

    create_tables()

    label_produto = tk.Label(root, text="Produto:", font=("Arial", 15), bg='white')
    label_produto.grid(row=0, column=0, padx=20, pady=20)

    entry_produto = tk.Entry(root, font=("Arial", 15))
    entry_produto.grid(row=0, column=1, padx=20, pady=20)

    label_quantidade = tk.Label(root, text="Quantidade:", font=("Arial", 15), bg='white')
    label_quantidade.grid(row=1, column=0, padx=20, pady=20)

    entry_quantidade = tk.Entry(root, font=("Arial", 15))
    entry_quantidade.grid(row=1, column=1, padx=20, pady=20)

    label_sessao = tk.Label(root, text="Sessão:", font=("Arial", 15), bg='white')
    label_sessao.grid(row=2, column=0, padx=20, pady=20)

    entry_sessao = tk.Entry(root, font=("Arial", 15))
    entry_sessao.grid(row=2, column=1, padx=20, pady=20)

    btn_adicionar = tk.Button(root, text="Adicionar ou Remover Produto", font=("Arial", 15), bg='white', command=lambda: adicionar_produto(entry_produto, entry_quantidade, entry_sessao, lista_estoque))
    btn_adicionar.grid(row=3, column=0, columnspan=2, padx=20, pady=20)

    btn_adicionar_sessao = tk.Button(root, text="Adicionar Sessão", font=("Arial", 15), bg='white', command=lambda: adicionar_sessao(entry_sessao, lista_estoque))
    btn_adicionar_sessao.grid(row=4, column=0, columnspan=2, padx=20, pady=20)

    btn_remover_sessao = tk.Button(root, text="Remover Sessão", font=("Arial", 15), bg='white', command=lambda: remover_sessao(entry_sessao, lista_estoque))
    btn_remover_sessao.grid(row=5, column=0, columnspan=2, padx=20, pady=20)

    lista_estoque = tk.Listbox(root, font=("Arial", 13), height=22, width=55)
    lista_estoque.grid(row=6, column=0, columnspan=2, padx=20, pady=20, sticky="sn")
    lista_estoque.bind('<<ListboxSelect>>', lambda event: carregar_produto_selecionado(event, lista_estoque, entry_produto, entry_quantidade, entry_sessao))

    mostrar_estoque(lista_estoque)

    root.mainloop()

if __name__ == "__main__":
    main()
