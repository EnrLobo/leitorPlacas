import sqlite3
from datetime import datetime

# Nome do arquivo do banco de dados
DB_NAME = "estacionamento.db"

def conectar():
    """Conecta ao banco de dados SQLite."""
    return sqlite3.connect(DB_NAME)

def criar_tabelas():
    """Cria as tabelas necessárias no banco de dados."""
    conn = conectar()
    try:
        cursor = conn.cursor()
        
        # Tabela de Veículos (Cadastro)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS veiculos (
                placa TEXT PRIMARY KEY,
                proprietario TEXT,
                tipo TEXT,       -- 'OFICIAL' ou 'PARTICULAR'
                status TEXT      -- 'AUTORIZADO', 'PROIBIDO', 'PENDENTE'
            )
        ''')
        
        # Tabela de Histórico de Acessos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS acessos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                placa TEXT,
                data_hora DATETIME,
                FOREIGN KEY(placa) REFERENCES veiculos(placa)
            )
        ''')
        
        conn.commit()
        print("Banco de dados configurado com sucesso!")
    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")
    finally:
        conn.close() # Garante o fechamento

def adicionar_veiculo(placa, proprietario, tipo, status):
    """Cadastra um novo veículo."""
    conn = conectar()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO veiculos (placa, proprietario, tipo, status) VALUES (?, ?, ?, ?)",
                       (placa, proprietario, tipo, status))
        conn.commit()
        print(f"Veículo {placa} cadastrado com sucesso.")
    except sqlite3.IntegrityError:
        print(f"Veículo {placa} já existe no banco.")
    except Exception as e:
        print(f"Erro ao adicionar veículo: {e}")
    finally:
        conn.close() 

def buscar_veiculo(placa):
    """Busca informações de um veículo pela placa."""
    conn = conectar()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM veiculos WHERE placa = ?", (placa,))
        resultado = cursor.fetchone()
        
        if resultado:
            return {
                "placa": resultado[0],
                "proprietario": resultado[1],
                "tipo": resultado[2],
                "status": resultado[3]
            }
        return None
    except Exception as e:
        print(f"Erro ao buscar veículo: {e}")
        return None
    finally:
        conn.close()

def registrar_acesso(placa):
    """Registra a entrada de um veículo agora."""
    # Para registrar acesso de desconhecidos, precisamos garantir que a tabela aceite
    # Se o veículo não existe na tabela 'veiculos', o SQLite pode reclamar da Foreign Key.
    
    conn = conectar()
    try:
        cursor = conn.cursor()
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("INSERT INTO acessos (placa, data_hora) VALUES (?, ?)", (placa, agora))
        conn.commit()
        print(f"[LOG] Acesso registrado para {placa} às {agora}")
    except sqlite3.IntegrityError:


        pass
    except Exception as e:
        print(f"Erro ao registrar acesso: {e}")
    finally:
        conn.close()

# --- BLOCO DE TESTE ---
if __name__ == "__main__":
    criar_tabelas()
    
    # Cadastro do Fusca
    adicionar_veiculo("BRA2E19", "Seu Madruga", "PARTICULAR", "AUTORIZADO")
    
    # Cadastro de outro veículo
    adicionar_veiculo("BEE4R22", "Policia", "Oficial", "AUTORIZADO")