import tkinter as tk
from tkinter import messagebox, ttk
import psycopg2 as conector
from datetime import datetime

def conectar():
    conn = conector.connect(dbname='ceramica',
                            user='postgres',
                            password='1234',
                            host='localhost',
                            port='5432')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS movimentacao(
                        id SERIAL PRIMARY KEY,
                        tipo VARCHAR(50),
                        quantidade INTEGER,
                        data VARCHAR(20),
                        destino VARCHAR(100),
                        observacao TEXT)''')
    conn.commit()
    return conn

def registrar_movimentacao(tipo, quantidade, data, destino='', observacao=''):
    conn = conectar()
    cursor = conn.cursor()
    data = datetime.now().strftime('%d/%m/%y %H:%M')
    cursor.execute(
        "INSERT INTO estoque (tipo, quantidade, data, destino, observacao) VALUES (%s, %s, %s, %s, %s)",
        (tipo, quantidade, data, destino, observacao)
    )
    conn.commit()
    conn.close()

def calcular_saldo():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT COALESCE(SUM(CASE WHEN tipo='entrada' THEN quantidade ELSE -quantidade END), 0) FROM estoque")
    saldo = cursor.fetchone()[0]
    conn.close()
    return saldo

def obter_historico():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT tipo, quantidade, data, destino, observacao FROM movimentacao ORDER BY id DESC")
    dados = cursor.fetchall()
    conn.close()
    return dados

#================ INTERFACE ==============

class App:
    def __init__(self, root):
        self.root = root
        self.root.title('Gerenciador de Pallets')
        self.root.geometry('600x400')

        #saldo atual
        self.saldo_label = tk.Label(root, text=f"Saldo atual: {calcular_saldo()} pallets", font=('Arial', 14, 'bold'))
        self.saldo_label.pack(pady=10)

        #Botoes principais
        frame_botoes = tk.Frame(root)
        frame_botoes.pack(pady=10)

        tk.Button(frame_botoes, text='Registrar entrada', width=20, command=self.registrar_entrada).grid(row=0, column=0,padx=10)
        tk.Button(frame_botoes, text='Registrar saída', width=20, command=self.registrar_saida).grid(row=0, column=1, padx=10)
        tk.Button(frame_botoes, text='Ver hitórico', width=20, command=self.ver_historico).grid(row=0, column=2, padx=10)

    def atualizar_saldo(self):
        self.saldo_label.config(text=f"Saldo atual: {calcular_saldo()} pallets")

    def registrar_entrada(self):
        self.janela_movimentacao('entrada')

    def registrar_saida(self):
        self.janela_movimentacao('saida')

    def janela_movimentacao(self, tipo):
        win = tk.Toplevel(self.root)
        win.title(f'Registrar{tipo.capitalize()}')
        win.geometry('350x250')

        tk.Label(win, text='Quantidade:').pack(pady=5)
        quantidade_entry = tk.Entry(win)
        quantidade_entry.pack()

        tk.Label(win, text='Destino (somente para saida):').pack(pady=5)
        destino_entry = tk.Entry(win)
        destino_entry.pack()

        tk.Label(win, text='Observação:').pack(pady=5)
        obs_entry = tk.Entry(win)
        obs_entry.pack()

        def salvar():
            try:
                qtd = int(quantidade_entry.get())
                destino = destino_entry.get() if tipo == 'saida' else ''
                obs = obs_entry.get()
                registrar_movimentacao(tipo, qtd, destino, obs)
                messagebox.showinfo('Sucesso', f'{tipo.capitalize()} registrada com sucesso!')
                win.destroy()
                self.atualizar_saldo()
            except ValueError:
                messagebox.showerror('Erro', 'Qusntidade deve ser um numero inteiro.')

        tk.Button(win, text='Salvar', command=salvar).pack(pady=10)

    def ver_historico(self):
        dados = obter_historico()
        win = tk.Toplevel(self.root)
        win.title('Histórico de Movimentação')
        win.geometry('600x300')

        colunas = ('Tipo', 'Quantidade', 'Data', 'Destino', 'Observação')
        tree = ttk.Treeview(win, columns=colunas, show='headings')
        for col in colunas:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        for row in dados:
            tree.insert('', tk.END, values=row)

        tree.pack(expand=True, fill='both')

#execução
if __name__=='__main__':
    conectar()
    root = tk.Tk()
    app = App(root)
    root.mainloop()











