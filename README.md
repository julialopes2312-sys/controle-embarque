# Controle de Embarque — App Flask

Sistema de controle de embarque e folga de inspetores offshore.

## Requisitos
- Python 3.8+
- pip

## Instalação e execução

```bash
# 1. Entre na pasta do projeto
cd app_inspetores

# 2. (Opcional) Crie um ambiente virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Rode o app
python app.py
```

Acesse no navegador: **http://localhost:5000**

## Funcionalidades

- **Dashboard** — resumo de embarcados, folga, afastados e lista de quem está a bordo agora
- **Inspetores** — listagem com filtros por status e modalidade, busca por nome/unidade
  - Registrar embarque / desembarque com data, coordenador responsável e observação
  - Editar status manualmente
  - Cadastrar novo inspetor (com opção de criar nova unidade na hora)
  - Remover inspetor
- **Unidades** — cadastro, edição e exclusão de unidades
- **Exportar CSV** — baixa todos os inspetores em arquivo .csv

## Banco de dados

O banco `inspetores.db` (SQLite) é criado automaticamente na primeira execução com dados iniciais.
Para resetar o banco, basta apagar o arquivo `inspetores.db` e reiniciar o app.

## Estrutura

```
app_inspetores/
├── app.py              ← Backend Flask + API REST
├── requirements.txt    ← Dependências
├── inspetores.db       ← Banco SQLite (gerado automaticamente)
└── templates/
    └── index.html      ← Interface web
```
