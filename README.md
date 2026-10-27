🛡️ Web Security Academy Solutions - Executor Automático
Este repositório contém scripts de automação para a resolução dos laboratórios da PortSwigger Web Security Academy.

O sistema conta com um gerador de fila (generate_labs_csv.py), um mapeador inteligente de URLs (auto_map.py) e um executor centralizado (run_all.py) para gerenciar as instâncias ativas e executar as soluções sequencialmente.


⚙️ 1. Requisitos e Instalaçãoa
Siga o passo a passo abaixo para configurar o ambiente virtual (.venv) e instalar todas as dependências necessárias no Windows (PowerShell/VS Code).
Passo 1: Abrir a pasta do projeto
No VS Code, abra a pasta do repositório ou navegue até ela pelo terminal:

cd C:\Caminho\Para\web-security-academy-solutions
Passo 2: Criar o Ambiente Virtual (.venv)
No terminal do VS Code (PowerShell), crie o ambiente Python isolado para o projeto:

python -m venv .venv
Passo 3: Ativar o Ambiente Virtual
Ative o ambiente criado rodando o script de ativação:

.\.venv\Scripts\Activate.ps1

Nota: Se o PowerShell bloquear a execução do script por políticas de segurança, execute o comando abaixo no PowerShell como Administrador e tente novamente: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

Когда ativado com sucesso, o terminal exibirá (.venv) no início da linha.
Passo 4: Instalar as Dependências
Atualize o gerenciador de pacotes pip e instale as bibliotecas necessárias listadas no arquivo requirements.txt:

python -m pip install --upgrade pip

pip install -r requirements.txt


🚀 2. Guia de Uso da Automação
O fluxo de trabalho diário é dividido em quatro etapas simples: gerar a fila, mapear as URLs, validar e executar.


Passo A: Gerar ou Atualizar o labs_queue.csv
O script varre o repositório inteiro, localiza todos os pares de arquivos .py e .md e atualiza a fila de laboratórios:

python .\generate_labs_csv.py


Passo B: Mapear URLs Automaticamente (auto_map.py)
Para não precisar preencher manualmente as URLs das instâncias geradas na PortSwigger, utilize o mapeador inteligente:

python .\auto_map.py

Como usar: Cole as URLs das instâncias da PortSwigger (uma por linha) diretamente no terminal. Quando terminar de colar todos los links, aperte Enter duas vezes (em uma linha vazia). O script vai acessar os links, ler o título de cada página, identificar o laboratório correto e atualizá-lo para o status pendente no arquivo CSV.


Passo C: Testar a Fila (Modo Simulação)
Antes de disparar os scripts contra os alvos, utilize o modo --dry-run para validar se o executor localiza os caminhos e arquivos corretamente sem disparar os ataques:

python .\run_all.py --dry-run


Passo D: Executar a Fila de Laboratórios
Com os laboratórios configurados como pendente, execute o gerenciador principal para rodar todas as soluções em lote sequencialmente:

python .\run_all.py
⚙️ Parâmetros Opcionais do Executor:
Alterar o Tempo Limite (Timeout por script em segundos):

python .\run_all.py --timeout 180

Adicionar Tentativas Extras em caso de erro (0 a 2 tentativas):

python .\run_all.py --retries 1


📌 3. Entendendo os Status no labs_queue.csv
Status
Descrição
aguardando_url
O script foi encontrado localmente, mas a URL da instância da PortSwigger ainda não foi informada.
pendente
A URL foi mapeada com sucesso e o laboratório está pronto para ser executado pelo run_all.py.
verificar
O script foi executado. É necessário confirmar manualmente na plataforma da PortSwigger se o laboratório foi marcado como resolvido (Solved).
erro
Ocorreu uma falha na execução, o tempo limite foi excedido ou a URL fornecida é inválida.



📊 4. Relatórios e Logs
Todas as execuções, saídas de terminal e rastros de erros do executor são salvos automaticamente na pasta de relatórios:

Arquivo de Log Detalhado: 04-reports/executor.log
