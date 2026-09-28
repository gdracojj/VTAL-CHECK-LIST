# VTAL CCOR V2

> **Automação da conferência de assunções de serviço da operação VTAL.**

[![Status](https://img.shields.io/badge/status-em%20desenvolvimento-orange)](https://github.com/gdracojj/VTAL-CHECK-LIST)
[![Versão](https://img.shields.io/badge/vers%C3%A3o-2.0-blue)](https://github.com/gdracojj/VTAL-CHECK-LIST)
[![Licença](https://img.shields.io/badge/licen%C3%A7a-MIT-green)](#-licen%C3%A7a)

## 🚀 Sobre o Projeto

O **VTAL CCOR V2** foi desenvolvido para centralizar e automatizar a conferência de mensagens de **assunção de serviço** recebidas dos grupos operacionais do WhatsApp.

O problema operacional tratado é a necessidade de consultar diversos grupos, identificar quem assumiu o posto, comparar a informação recebida com a escala e localizar rapidamente atrasos, divergências e registros incompletos. A V2 organiza esse fluxo em um único sistema, separando a entrada das mensagens, o processamento dos dados e a apresentação dos resultados.

### Principais funcionalidades

- **Dashboard web** para visualização consolidada das assunções.
- **Leitura e interpretação de mensagens** por meio do parser da aplicação.
- **Identificação de posto, horário e informações do colaborador** a partir do texto recebido.
- **Comparação aproximada de nomes** usando `RapidFuzz` e `token_set_ratio`.
- **Comparação entre assunção recebida e escala cadastrada** em JSON.
- **Classificação dos resultados** em categorias como `REGULAR`, `ADIANTADO`, `ATRASADO`, `SEM ASSUNÇÃO`, `DIVERGÊNCIA` e `IDENTIFICADA`.
- **Pesquisa no dashboard** por posto, nome ou motivo.
- **Filtros por status** diretamente no painel.
- **Alternância de tema claro/escuro** com persistência no navegador.
- **Exibição de horário de Brasília** no dashboard.
- **Página de teste de mensagens** acessível pela rota `/teste`.
- **Integração inicial com WhatsApp Web** usando `whatsapp-web.js`.
- **Persistência local da sessão do WhatsApp** com `LocalAuth`.
- **Captura de mensagens de grupos**, identificados pelo sufixo `@g.us`.

## 🛠️ Tecnologias e Arquitetura

### Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python |
| API / servidor web | FastAPI |
| Servidor ASGI | Uvicorn |
| Templates | Jinja2 |
| Validação / modelos | Pydantic |
| Matching de nomes | RapidFuzz |
| Frontend | HTML, CSS e JavaScript |
| Integração WhatsApp | Node.js + `whatsapp-web.js` |
| QR Code | `qrcode-terminal` |
| Versionamento | Git + GitHub |

### Arquitetura

O projeto utiliza uma arquitetura separada em duas partes principais:

```text
                   ┌─────────────────────┐
                   │      WhatsApp       │
                   │   WhatsApp Web     │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │  whatsapp/client.js │
                   │   Node.js          │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │     FastAPI V2      │
                   │     app/main.py     │
                   └──────────┬──────────┘
                              │
                  ┌───────────┼───────────┐
                  ▼           ▼           ▼
             ┌────────┐ ┌──────────┐ ┌──────────┐
             │ parser │ │ matcher  │ │ storage  │
             └────┬───┘ └────┬─────┘ └────┬─────┘
                  │          │            │
                  └──────────┼────────────┘
                             ▼
                      ┌─────────────┐
                      │ escala.json │
                      └──────┬──────┘
                             │
                             ▼
                      ┌─────────────┐
                      │  Dashboard  │
                      └─────────────┘
```

### Estrutura de diretórios

```text
vtal_ccor_v2/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── matcher.py
│   ├── parser.py
│   ├── storage.py
│   ├── dashboard.html
│   ├── static/
│   └── templates/
│       └── dashboard.html
│
├── data/
│   └── escala.json
│
├── tests/
│
├── whatsapp/
│   └── client.js
│
├── converter_escala.py
├── requirements.txt
├── package.json
├── package-lock.json
├── README.md
├── README_INTEGRACAO.md
└── .gitignore
```

> `node_modules/`, `.wwebjs_auth/` e `.wwebjs_cache/` são diretórios locais e não devem ser versionados no Git.

## ⚙️ Configuração e Instalação

### Pré-requisitos

- **Python 3.x** com `pip`.
- **Node.js** instalado no sistema.
- **npm** para instalação das dependências JavaScript.
- **Git**.
- Uma conta de WhatsApp capaz de utilizar o WhatsApp Web para a integração via `whatsapp-web.js`.

### 1. Clonar o repositório

```bash
git clone https://github.com/gdracojj/VTAL-CHECK-LIST.git
cd VTAL-CHECK-LIST
```

### 2. Criar e ativar o ambiente virtual Python

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Windows CMD:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instalar dependências Python

```bash
pip install -r requirements.txt
```

### 4. Instalar dependências do WhatsApp

```bash
npm install
```

Caso o PowerShell bloqueie `npm.ps1`, utilize:

```powershell
npm.cmd install
```

### 5. Iniciar o backend

```bash
uvicorn app.main:app --reload
```

Após a inicialização, o painel fica disponível normalmente em:

```text
http://127.0.0.1:8000
```

### 6. Iniciar o cliente WhatsApp

Em outro terminal:

```bash
node whatsapp/client.js
```

No primeiro uso, o cliente exibe um **QR Code** no terminal. O código deve ser escaneado pelo WhatsApp em **Dispositivos conectados**.

Depois da autenticação, a sessão local é mantida pelo `LocalAuth`.

### Variáveis de ambiente

Não foi identificado, no material do projeto disponível para esta documentação, um arquivo `.env` ou um conjunto de variáveis de ambiente obrigatório para a execução básica.

As configurações observadas são feitas diretamente nos arquivos da aplicação, incluindo o `client.js` para a autenticação local do WhatsApp.

## 📦 Como Usar

### Acesso ao dashboard

Com o FastAPI em execução, abra:

```text
http://127.0.0.1:8000/
```

O dashboard apresenta um resumo dos resultados e uma tabela com:

- status;
- posto;
- colaborador esperado;
- informação recebida;
- horário real;
- horário previsto;
- motivo da classificação.

O painel também permite:

- filtrar por status;
- pesquisar por texto;
- limpar os filtros;
- alternar o tema visual;
- abrir a página de testes.

### Página de testes

A interface disponibiliza a rota:

```text
http://127.0.0.1:8000/teste
```

Ela é acessível pelo botão **Testar mensagens** presente no dashboard.

### Consulta da API

A aplicação expõe o endpoint:

```text
/api/messages
```

Exemplo de consulta:

```bash
curl http://127.0.0.1:8000/api/messages
```

> A interface e o backend são responsáveis pela interpretação das mensagens; o cliente WhatsApp deve funcionar como camada de entrada.

### Fluxo principal de uma assunção

```text
Mensagem de grupo
        ↓
whatsapp/client.js
        ↓
Recepção da mensagem
        ↓
Parser
        ↓
Extração de dados
        ↓
Matcher
        ↓
Comparação com data/horário/posto/nome esperado
        ↓
Classificação
        ↓
Storage
        ↓
Dashboard
```

### Escala

A referência operacional utilizada pelo sistema fica em:

```text
data/escala.json
```

O arquivo contém os registros estruturados utilizados pelo matcher para identificar o colaborador/posto esperado.

O utilitário:

```text
converter_escala.py
```

é utilizado no fluxo de conversão da escala para um formato estruturado compatível com a aplicação.

### Matching de nomes

A comparação aproximada utiliza `RapidFuzz` com `token_set_ratio`, permitindo tolerar diferenças de escrita entre a mensagem e o cadastro da escala.

## 🧪 Testes

O repositório possui um diretório dedicado:

```text
tests/
```

Além disso, durante o desenvolvimento foi utilizado um conjunto sintético de **1.000 mensagens** para validar a lógica de identificação e classificação.

Resultado registrado desse conjunto de validação:

```text
Esperados: 44
Identificados: 44
Pendentes: 0

TOTAL: 1000
REGULARES: 431
ATRASOS: 110
DIVERGÊNCIA DE NOME: 221
POSTO NÃO LOCALIZADO: 124
INCOMPLETAS: 114
```

Esses números são referentes ao conjunto sintético de desenvolvimento e não representam indicadores da operação real.

> O conteúdo atual disponível para análise não permitiu confirmar um comando único e oficial de execução da suíte localizada em `tests/`. Por isso, este README não inventa um comando como `pytest` sem confirmar a configuração do repositório.

## 📄 Licença

Este projeto utiliza a licença **MIT** para fins de documentação do repositório, conforme orientação de documentação quando não há um arquivo de licença específico confirmado.

Consulte o arquivo `LICENSE` do repositório caso uma licença formal seja adicionada posteriormente.
