import sqlite3
import csv
from datetime import datetime, timedelta

# --- CONFIGURAÇÕES ---
DB_NAME = "estacionamento.db"
TEMPO_LIMITE_MINUTOS = 1 # 1 minuto para conseguir testar rápido!
# No mundo real, seria algo como: TEMPO_LIMITE_MINUTOS = 240 (4 horas)

def conectar():
    return sqlite3.connect(DB_NAME)

def gerar_relatorio_csv():
    """Req. 5: Gera um arquivo Excel/CSV com todo o histórico."""
    conn = conectar()
    cursor = conn.cursor()
    
    # Busca tudo da tabela de acessos junto com os dados do veículo
    cursor.execute('''
        SELECT a.id, a.placa, v.proprietario, v.tipo, a.data_hora 
        FROM acessos a
        LEFT JOIN veiculos v ON a.placa = v.placa
        ORDER BY a.data_hora DESC
    ''')
    dados = cursor.fetchall()
    conn.close()
    
    # Nome do arquivo com a data de hoje
    nome_arquivo = f"relatorio_acessos_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    
    with open(nome_arquivo, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';') # Ponto e vírgula abre bem no Excel
        writer.writerow(["ID", "Placa", "Proprietário", "Tipo", "Data/Hora Entrada"])
        writer.writerows(dados)
        
    print(f"\n✅ Relatório gerado com sucesso: {nome_arquivo}")
    print("Abra este arquivo no Excel para ver os dados.")

def verificar_tempo_permanencia():
    """Req. 6: Alerta sobre veículos que estouraram o tempo."""
    conn = conectar()
    cursor = conn.cursor()
    
    # Pega o último acesso de cada veículo
    cursor.execute('''
        SELECT a.placa, v.proprietario, MAX(a.data_hora) as ultima_entrada
        FROM acessos a
        LEFT JOIN veiculos v ON a.placa = v.placa
        GROUP BY a.placa
    ''')
    registros = cursor.fetchall()
    conn.close()
    
    print("\n--- 🚨 VERIFICAÇÃO DE TEMPO DE PERMANÊNCIA ---")
    encontrou_alerta = False
    
    agora = datetime.now()
    
    for placa, proprietario, data_str in registros:
        # Converte a string do banco de volta para objeto de data
        data_entrada = datetime.strptime(data_str, "%Y-%m-%d %H:%M:%S")
        
        # Calcula quanto tempo passou
        diferenca = agora - data_entrada
        minutos_passados = diferenca.total_seconds() / 60
        
        if minutos_passados > TEMPO_LIMITE_MINUTOS:
            encontrou_alerta = True
            print(f"⚠️  ALERTA: Veículo {placa} ({proprietario})")
            print(f"    Entrou às: {data_str}")
            print(f"    Tempo decorrido: {int(minutos_passados)} minutos (Limite: {TEMPO_LIMITE_MINUTOS} min)")
            print("-" * 30)
            
    if not encontrou_alerta:
        print("✅ Nenhum veículo excedeu o tempo limite.")

# --- MENU PRINCIPAL ---
if __name__ == "__main__":
    while True:
        print("\n=== SISTEMA DE GESTÃO - IFSULDEMINAS ===")
        print("1. 📄 Gerar Relatório de Acessos (CSV)")
        print("2. ⏰ Verificar Alertas de Tempo")
        print("3. ❌ Sair")
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == '1':
            gerar_relatorio_csv()
        elif opcao == '2':
            verificar_tempo_permanencia()
        elif opcao == '3':
            break
        else:
            print("Opção inválida.")