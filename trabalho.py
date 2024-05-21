import tkinter as tk
from tkinter import messagebox
import sqlite3

def create_tables(): #Lohan
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

def obter_sessoes(): #joao 
    pass

def adicionar_sessao(): #lohan 
    pass

def adicionar_produto(): #paulo
    pass

def mostrar_estoque(): #paulo
    pass

def remover_sessao(): #lucas
    pass

def main():  #rafael interface do programa
    root = tk.Tk()
    root.title("Sistema de Estoque")

    root.iconbitmap("un.ico")
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

    btn_adicionar = tk.Button(root, text="Adicionar ou Remover Produto", font=("Arial", 15), bg='white', command=)
    btn_adicionar.grid(row=3, column=0, columnspan=2, padx=20, pady=20)

    btn_adicionar_sessao = tk.Button(root, text="Adicionar Sessão", font=("Arial", 15), bg='white', command=)
    btn_adicionar_sessao.grid(row=4, column=0, columnspan=2, padx=20, pady=20)

    btn_remover_sessao = tk.Button(root, text="Remover Sessão", font=("Arial", 15), bg='white', command=)
    btn_remover_sessao.grid(row=5, column=0, columnspan=2, padx=20, pady=20)

    lista_estoque = tk.Listbox(root, font=("Arial", 13), height=22, width=55)
    lista_estoque.grid(row=6, column=0, columnspan=2, padx=20, pady=20, sticky="sn")

    #mostrar_estoque()

    root.mainloop()

if __name__ == "__main__":
    main()