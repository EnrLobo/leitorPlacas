# Sistema de Controle de Acesso Veicular - IFSULDEMINAS

Este projeto consiste em um sistema de Visão Computacional desenvolvido em Python para o controle automatizado de acesso de veículos no campus do IFSULDEMINAS - Machado. O sistema realiza a leitura automática de placas (ANPR), validação de permissões e geração de relatórios administrativos.

**Projeto Final da disciplina de Computação Gráfica.**

##  Funcionalidades

O sistema atende aos seguintes requisitos:

- [x] **Identificação Automática:** Detecção e leitura de placas (padrão Mercosul) em tempo real ou via imagem.
- [x] **Correção Inteligente:** Algoritmo pós-OCR para corrigir erros comuns de leitura (ex: 2 vs Z, 1 vs I).
- [x] **Controle de Acesso:** Diferenciação entre veículos Oficiais, Particulares e Visitantes.
- [x] **Sistema de Alertas:** Alerta visual e no log para veículos com status "PROIBIDO" ou não cadastrados.
- [x] **Banco de Dados:** Registro automático de todos os acessos (Data/Hora/Placa) em SQLite.
- [x] **Relatórios:** Geração de planilhas CSV com histórico de acessos.
- [x] **Monitoramento:** Verificação de veículos que excederam o tempo limite de permanência.

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.x
* **Visão Computacional:** OpenCV (cv2)
* **OCR (Reconhecimento de Texto):** EasyOCR + Torch
* **Banco de Dados:** SQLite3
* **Interface:** CLI e Janelas nativas do OpenCV

## ⚙️ Instalação e Configuração

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/seu-usuario/ProjetoFinalCG.git](https://github.com/seu-usuario/ProjetoFinalCG.git)
    cd ProjetoFinalCG
    ```

2.  **Crie um ambiente virtual (recomendado):**
    ```bash
    python -m venv .venv
    # Windows:
    .venv\Scripts\activate
    # Linux/Mac:
    source .venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install opencv-python easyocr torch torchvision
    ```

##  Como Executar

### 1. Configurar o Banco de Dados
Execute o script de banco de dados pela primeira vez para criar as tabelas e cadastrar veículos de teste:
```bash
python database.py
```

### Rodar o Detector (Simulação de Câmera)
Para processar uma imagem e registrar a entrada:
```
python detector2.py
```
Nota: Altere a variável image_path no código para testar diferentes imagens.

## 3. Gerar Relatórios e Alertas
Para verificar o tempo de permanência ou exportar o histórico:
```
python gestao.py
```
Estrutura do Projeto

- detector2.py: Script principal. Realiza a detecção, OCR, correção lógica e exibe o resultado na tela.

- database.py: Gerencia a conexão com o SQLite, cria tabelas e insere registros.

- gestao.py: Módulo administrativo para gerar CSV e verificar alertas de tempo.

- haarcascade_*.xml: Modelo pré-treinado para detecção de placas.

### Autores
Arielce Junior, Enrique Lobo e Walter Dias.
