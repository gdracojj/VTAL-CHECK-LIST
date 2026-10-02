# ControlOps

> Plataforma de monitoramento e análise operacional desenvolvida em Python, com foco em processamento de dados, validação de escalas, identificação de divergências e geração de indicadores operacionais.

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-orange)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-API-green)
![Node.js](https://img.shields.io/badge/Node.js-Integration-brightgreen)
![Data Engineering](https://img.shields.io/badge/focus-Data%20Engineering-purple)

---

## Sobre o projeto

O **ControlOps** é uma solução de monitoramento e análise operacional desenvolvida para processar registros de escalas, assunções de serviço e ocorrências operacionais.

O sistema realiza a ingestão e o tratamento de dados, cruza informações de colaboradores, postos, escalas e regras operacionais e identifica situações como:

- assunções regulares;
- atrasos;
- adiantamentos;
- divergências de colaborador;
- divergências de posto;
- postos sem assunção;
- registros incompletos.

O projeto foi reconstruído de forma independente a partir de um problema operacional vivenciado profissionalmente.

**Todos os dados utilizados no projeto são fictícios e sintéticos.**

Nenhum dado real de colaboradores, empresas, clientes, postos ou operações é utilizado na versão atual.

---

## Objetivo

O objetivo do ControlOps é demonstrar, na prática, como um problema operacional pode ser transformado em uma solução baseada em dados.

O projeto combina conceitos de:

- Data Engineering;
- Data Analytics;
- Python;
- APIs REST;
- processamento e normalização de dados;
- regras de negócio;
- matching de informações;
- armazenamento estruturado;
- dashboards operacionais;
- automação.

A proposta é construir um fluxo no qual dados operacionais brutos sejam transformados em informações estruturadas para apoiar o acompanhamento da operação.

---

## Contexto do problema

Em uma operação com diferentes postos e colaboradores, uma parte relevante do controle operacional consiste em verificar se as informações recebidas correspondem ao que estava previsto na escala.

Um registro pode apresentar, por exemplo:

```text
Orion Telecom
Posto: OR-AC-OPS-001
Data: 04/09/2026
Assunção de serviço: Vitória Almeida assumindo
Assumindo serviço 18h00 às 06h00
```

O sistema precisa interpretar essas informações e compará-las com os dados estruturados da operação.

A partir desse cruzamento, é possível identificar se:

- o posto existe;
- o colaborador corresponde ao esperado;
- o horário corresponde à escala;
- a data está de acordo com a escala;
- houve atraso ou adiantamento;
- existe alguma divergência;
- algum posto esperado não possui registro de assunção.

---

# Arquitetura

A arquitetura atual segue uma separação entre ingestão, processamento, validação e apresentação:

```text
WhatsApp / Dados de entrada
          │
          ▼
     Node.js
   client.js
          │
          ▼
      FastAPI
      main.py
          │
          ▼
       parser.py
          │
          ▼
      matcher.py
          │
          ▼
      storage.py
          │
          ▼
      Dashboard
```

### Fluxo de processamento

```text
Dados brutos
     ↓
Ingestão
     ↓
Parsing
     ↓
Normalização
     ↓
Matching
     ↓
Regras de negócio
     ↓
Classificação
     ↓
Armazenamento
     ↓
API
     ↓
Dashboard
```

---

# Componentes

## Node.js

O diretório `whatsapp/` contém a camada responsável pela integração com a fonte de mensagens.

O cliente utiliza:

- Node.js;
- whatsapp-web.js;
- QR Code para autenticação.

Essa camada representa a etapa de ingestão dos dados.

---

## FastAPI

O `app/main.py` funciona como ponto central da aplicação.

Responsabilidades:

- inicialização da API;
- recebimento de mensagens;
- processamento dos registros;
- geração dos relatórios;
- exposição dos endpoints;
- integração com o dashboard.

---

## Parser

O `app/parser.py` transforma mensagens não estruturadas em dados estruturados.

Informações extraídas podem incluir:

```text
group
raw
post_raw
incoming
outgoing
assumption_time
date
received_at
```

Por exemplo:

```text
Mensagem
    ↓
"Posto: OR-AC-OPS-001"
"Vitória Almeida assumindo"
"18h00 às 06h00"
    ↓
Dados estruturados
```

---

## Matcher

O `app/matcher.py` realiza o cruzamento entre os dados processados e a escala operacional.

O componente considera:

- posto;
- colaborador;
- horário;
- data;
- escala;
- paridade do dia;
- similaridade de nomes;
- aliases de postos.

A comparação utiliza similaridade textual para lidar com pequenas diferenças na forma como os nomes podem aparecer nas mensagens.

---

# Modelo de escala

O projeto utiliza uma escala sintética para representar uma operação com colaboradores em turnos diurnos e noturnos.

Cada posto possui colaboradores associados a diferentes ciclos:

```text
                 POSTO
                   │
          ┌────────┴────────┐
          │                 │
       DIURNO            NOTURNO
          │                 │
      06:00–18:00       18:00–06:00
          │                 │
     ┌────┴────┐       ┌────┴────┐
   Pares     Ímpares  Pares     Ímpares
```

A alternância é representada pelo campo:

```json
"dias": "pares"
```

ou:

```json
"dias": "impares"
```

Dessa forma, o sistema consegue determinar qual colaborador deveria estar associado ao posto em determinada data.

---

# Classificação operacional

O ControlOps trabalha com diferentes situações de operação.

| Situação | Descrição |
|---|---|
| `REGULAR` | Colaborador, posto e horário correspondem ao esperado |
| `ADIANTADO` | Assunção ocorreu antes do horário previsto |
| `ATRASADO` | Assunção ocorreu depois do horário previsto |
| `DIVERGÊNCIA` | Informações recebidas não correspondem à escala |
| `SEM ASSUNÇÃO` | Posto esperado não possui registro identificado |
| `POSTO_NAO_LOCALIZADO` | Posto não foi encontrado na escala |
| `HORÁRIO NÃO IDENTIFICADO` | Não foi possível identificar o horário da mensagem |

Exemplo:

```text
Escala:

Posto: OR-AC-OPS-001
Colaborador: Lucas Almeida
Horário: 06:00

Mensagem:

Posto: OR-AC-OPS-001
Colaborador: Lucas Almeida
Horário: 06:30

Resultado:

ATRASADO 30 min
```

---

# Dados sintéticos

O projeto foi estruturado para trabalhar com dados fictícios.

O contexto utilizado atualmente é:

```text
Empresa fictícia:
Orion Telecom
```

Os colaboradores, postos, escalas e mensagens presentes no projeto são dados sintéticos.

Isso permite demonstrar a arquitetura e as regras de negócio sem expor informações operacionais ou dados pessoais reais.

---

# Testes

O projeto possui uma estrutura para geração de mensagens sintéticas e testes do parser.

O gerador localizado em:

```text
tests/generate_messages.py
```

cria mensagens com diferentes situações:

```text
correta
horario
nome
posto
inexistente
incompleta
```

Exemplo:

```text
Status: correta

Orion Telecom
Posto: OR-AC-OPS-001
Data: 04/09/2026
Assunção de serviço: Vitória Almeida assumindo
Assumindo serviço 18h00 às 06h00
```

Também são gerados casos propositalmente inconsistentes para validar o comportamento do sistema.

---

## Executando os testes

Para gerar as mensagens sintéticas:

```bash
python tests/generate_messages.py
```

Para executar o teste do parser:

```bash
python tests/test_parser.py
```

Os resultados são armazenados em:

```text
data/test_messages_1000.json
data/parser_failures.json
```

---

# API

A aplicação utiliza FastAPI para disponibilizar os dados processados.

## Dashboard

```http
GET /
```

Retorna o dashboard principal da aplicação.

---

## Relatório operacional

```http
GET /api/report?plantao=diurno_a
```

Exemplo de resposta:

```json
{
  "ok": true,
  "plantao": "diurno_a",
  "total_roster": 15,
  "identified_total": 12,
  "counts": {
    "REGULAR": 8,
    "ADIANTADO": 1,
    "ATRASADO": 2,
    "SEM ASSUNÇÃO": 3,
    "DIVERGÊNCIA": 1,
    "IDENTIFICADA": 12
  },
  "results": []
}
```

---

## Mensagens

```http
GET /api/messages
```

Retorna os registros armazenados.

---

## Adicionar mensagem

```http
POST /api/messages
```

Exemplo:

```json
{
  "group": "OR-AC-OPS-001",
  "message": "Orion Telecom...",
  "received_at": "2026-09-04T06:00:00"
}
```

---

## Atualizar relatório

```http
POST /api/refresh
```

Atualiza o processamento dos dados.

---

## Limpar mensagens

```http
POST /api/clear
```

Remove os registros armazenados para permitir novos testes.

---

# Dashboard

O projeto possui um dashboard operacional desenvolvido para facilitar a visualização dos resultados.

O dashboard apresenta informações como:

- quantidade de postos;
- assunções identificadas;
- assunções regulares;
- atrasos;
- adiantamentos;
- divergências;
- postos sem assunção;
- busca e filtros;
- detalhes das ocorrências;
- seleção de plantão;
- atualização dos dados.

A interface foi construída com foco em visualização operacional e tomada de decisão baseada nos dados processados.

---

# Estrutura do projeto

```text
ControlOps/
│
├── app/
│   ├── main.py
│   ├── parser.py
│   ├── matcher.py
│   ├── compare.py
│   ├── storage.py
│   ├── dashboard.html
│   │
│   ├── templates/
│   │   └── dashboard.html
│   │
│   └── static/
│
├── data/
│   ├── escala.json
│   ├── aliases.json
│   └── messages.json
│
├── tests/
│   ├── test_parser.py
│   └── generate_messages.py
│
├── whatsapp/
│   └── client.js
│
├── package.json
├── requirements.txt
├── .gitignore
└── README.md
```

---

# Tecnologias

## Backend

- Python
- FastAPI
- Pydantic

## Processamento de dados

- JSON
- Python
- RapidFuzz
- regras de negócio
- normalização de dados
- matching textual

## Integração

- Node.js
- whatsapp-web.js

## Frontend

- HTML
- CSS
- JavaScript

## Ferramentas

- Git
- GitHub
- Linux
- Fedora

---

# Data Engineering

O ControlOps também funciona como um projeto prático de Data Engineering.

O fluxo possui características comuns de um pipeline de dados:

```text
INGESTÃO
   ↓
DADOS BRUTOS
   ↓
EXTRAÇÃO
   ↓
TRANSFORMAÇÃO
   ↓
NORMALIZAÇÃO
   ↓
VALIDAÇÃO
   ↓
MATCHING
   ↓
DADOS ESTRUTURADOS
   ↓
ANALYTICS
   ↓
DASHBOARD
```

Entre os conceitos aplicados estão:

- ingestão de dados;
- processamento de dados não estruturados;
- transformação;
- normalização;
- validação;
- enriquecimento;
- matching;
- regras de negócio;
- armazenamento;
- APIs;
- geração de indicadores.

---

# Evolução planejada

O projeto foi estruturado para permitir evolução gradual.

## Fase 1 — Base

- [x] Estrutura do projeto
- [x] Parser de mensagens
- [x] Escala sintética
- [x] Matching de colaboradores
- [x] Regras de horário
- [x] API FastAPI
- [x] Dashboard
- [x] Testes sintéticos

## Fase 2 — Dados

- [ ] Migração do armazenamento JSON para PostgreSQL
- [ ] Modelagem das tabelas
- [ ] Histórico de eventos
- [ ] Logs de processamento
- [ ] Queries analíticas

## Fase 3 — Data Engineering

- [ ] Pipeline de ingestão estruturado
- [ ] ETL/ELT
- [ ] processamento incremental
- [ ] tratamento de dados históricos
- [ ] validação automatizada
- [ ] monitoramento do pipeline

## Fase 4 — Analytics

- [ ] KPIs operacionais
- [ ] histórico de atrasos
- [ ] indicadores por posto
- [ ] indicadores por colaborador
- [ ] análise temporal
- [ ] dashboards analíticos

## Fase 5 — Inteligência

- [ ] detecção de padrões
- [ ] identificação de anomalias
- [ ] classificação automatizada
- [ ] modelos preditivos
- [ ] recursos de IA para apoio operacional

---

# Decisões de arquitetura

Uma das decisões do projeto é separar as responsabilidades entre componentes.

Por exemplo:

```text
parser.py
```

é responsável pela interpretação da mensagem.

```text
matcher.py
```

é responsável pelo cruzamento com a escala.

```text
storage.py
```

é responsável pelo armazenamento.

```text
main.py
```

é responsável pela API e pela orquestração da aplicação.

Essa separação facilita a manutenção, os testes e a evolução da aplicação.

---

# Aprendizados

O desenvolvimento do ControlOps envolve problemas comuns em projetos reais de dados:

- dados não estruturados;
- inconsistência de nomes;
- diferentes formatos de horário;
- dados incompletos;
- identificação de entidades;
- regras de negócio;
- validação de dados;
- integração entre sistemas;
- transformação de dados;
- necessidade de rastreabilidade.

Mais do que simplesmente construir uma aplicação, o projeto busca demonstrar o processo de transformar um problema operacional em um pipeline de dados estruturado.

---

# Privacidade e dados

O ControlOps utiliza exclusivamente dados fictícios e sintéticos na versão publicada neste repositório.

O projeto não deve conter:

- nomes reais de colaboradores;
- números de telefone;
- mensagens reais;
- informações de clientes;
- credenciais;
- dados operacionais confidenciais;
- arquivos proprietários.

Qualquer dado utilizado para demonstração deve ser criado especificamente para o projeto.

---

# Princípios do projeto

O desenvolvimento do ControlOps segue alguns princípios:

### Separação de responsabilidades

Cada componente deve possuir uma responsabilidade clara.

### Dados antes da interface

O dashboard é uma camada de apresentação dos dados processados, não o núcleo da aplicação.

### Regras explícitas

As regras operacionais devem ser implementadas de forma clara e testável.

### Dados sintéticos

O projeto deve permanecer independente de informações proprietárias.

### Evolução incremental

A arquitetura deve permitir a evolução de armazenamento local para bancos de dados e pipelines mais robustos.

---

# Status

**Em desenvolvimento.**

O núcleo do projeto já contempla:

- ingestão;
- parsing;
- normalização;
- matching;
- regras de escala;
- API;
- armazenamento;
- dashboard;
- geração de dados sintéticos;
- testes automatizados do parser.

As próximas etapas estão relacionadas principalmente à evolução da camada de dados, persistência em PostgreSQL, construção de pipelines e expansão dos recursos analíticos.

---

# Autor

**Gabriel Silva**

Projeto desenvolvido como estudo prático de:

**Data Engineering · Data Analytics · Python · APIs · Automação · IA**

---

## Licença

Este projeto é destinado a fins educacionais e de portfólio.
