🛡️ Web Security Academy Solutions - Executor Automático

Este repositório contém scripts de automação para a resolução dos laboratórios da PortSwigger Web Security Academy.

O sistema conta com um gerador de fila (generate_labs_csv.py) e um executor centralizado (run_all.py) para gerenciar as instâncias ativas e executar as soluções sequencialmente.

⚙️ 1. Requisitos e Instalação

Siga o passo a passo abaixo para configurar o ambiente virtual (.venv) e instalar todas as dependências necessárias no Windows (PowerShell/VS Code).

Passo 1: Abrir a Pasta do Repositório

Abra a pasta do projeto no VS Code ou navegue até ela pelo terminal:

cd C:\Caminho\Para\web-security-academy-solutions


Passo 2: Criar o Ambiente Virtual (.venv)

No terminal do VS Code (PowerShell), crie o ambiente Python isolado:

python -m venv .venv


Passo 3: Ativar o Ambiente Virtual

Ative o ambiente criado:

.\.venv\Scripts\Activate.ps1


Nota: Se o PowerShell bloquear a execução do script por conta de políticas de execução, rode o comando abaixo no PowerShell como Administrador:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

Ao ativar, o terminal mostrará (.venv) no início da linha de comando.

Passo 4: Instalar as Dependências

Atualize o pip e instale todas as bibliotecas necessárias a partir do arquivo requirements.txt:

python -m pip install --upgrade pip
pip install -r requirements.txt


🚀 2. Guia de Uso da Automação

O fluxo de trabalho consiste em gerar/atualizar a fila, injetar as URLs ativas da PortSwigger e disparar a execução.

Passo A: Gerar ou Atualizar o labs_queue.csv

O gerador descobre automaticamente todos os scripts .py no seu repositório e cria/atualiza a fila mantendo a estrutura original:

python .\generate_labs_csv.py


Passo B: Injetar URLs na Fila

Para cadastrar as URLs das instâncias geradas na PortSwigger e marcar os laboratórios como pendente, execute no PowerShell (substituindo pelas suas URLs reais):

python -c "import csv; rows=list(csv.DictReader(open('labs_queue.csv',encoding='utf-8-sig'))); urls=['https://SUA_URL_1.web-security-academy.net/', 'https://SUA_URL_2.web-security-academy.net/']; [r.update({'url': u, 'status': 'pendente'}) for r, u in zip(rows[:len(urls)], urls)]; writer=csv.DictWriter(open('labs_queue.csv','w',newline='',encoding='utf-8-sig'), fieldnames=rows[0].keys()); writer.writeheader(); writer.writerows(rows); print(f'Sucesso! {len(urls)} laboratório(s) atualizados para pendente.')"


💡 Nota: Você pode enviar quantas URLs quiser dentro da lista urls=['...', '...']. O script irá atribuí-las sequencialmente aos scripts da fila.

Passo C: Testar a Fila (Modo Simulação)

Valide a fila e verifique se os scripts existem sem disparar os ataques de fato:

python .\run_all.py --dry-run


Passo D: Executar a Fila de Laboratórios

Com os laboratórios configurados como pendente, execute o gerenciador para resolver tudo em lote:

python .\run_all.py


Opções Adicionais do Executor:

Alterar o Tempo Limite (Timeout por script em segundos):

python .\run_all.py --timeout 180


Adicionar Tentativas Extras em caso de erro (0 a 2):

python .\run_all.py --retries 1


📌 3. Entendendo os Status no labs_queue.csv

Status

Descrição

aguardando_url

O script foi encontrado localmente, mas a URL da instância da PortSwigger ainda não foi informada.

pendente

A URL foi cadastrada e o laboratório está pronto para ser executado pelo run_all.py.

verificar

O script foi executado. É necessário confirmar manualmente na plataforma da PortSwigger se foi marcado como resolvido (Solved).

erro

Ocorreu uma falha na execução, tempo limite excedido ou a URL fornecida é inválida.

📊 4. Relatórios e Logs

Todas as ações e saídas de terminal do executor são registradas automaticamente na pasta de relatórios:

Arquivo de log detalhado: 04-reports/executor.log