# README DO PROJETO
- Manual de uso
- Estrutura do projeto
# DOCUMENTAÇÃO OFICIAL DO PROJETO

# SABORES DO PARÁ

## Sistema de Gestão para Restaurantes e Lanchonetes

---

## Projeto Integrador – Programador de Sistemas

**Instituição:** SENAC

**Nome do Projeto:** Sabores do Pará

**Versão:** 1.0.0

**Tipo de Aplicação:** Sistema Desktop de Gestão Empresarial

**Arquitetura:** MVC (Model-View-Controller)

**Linguagem Principal:** Python

**Interface Gráfica:** CustomTkinter

**Banco de Dados:** Aiven Cloud Database (MySQL)

**Controle de Versão:** Git e GitHub

---

# SUMÁRIO

1. Apresentação do Projeto
2. Objetivos
3. Escopo do Sistema
4. Público-Alvo
5. Tecnologias Utilizadas
6. Arquitetura do Sistema
7. Estrutura do Repositório
8. Banco de Dados
9. Módulos do Sistema
10. Fluxo de Funcionamento
11. Componentes Compartilhados
12. Padrões de Desenvolvimento
13. Segurança
14. Controle de Versão
15. Testes
16. Roadmap
17. Conclusão

---

# 1. APRESENTAÇÃO DO PROJETO

O Sabores do Pará é um sistema desktop de gestão empresarial desenvolvido para auxiliar restaurantes, lanchonetes, cafeterias e estabelecimentos gastronômicos na organização e controle de suas operações.

O sistema foi criado com o objetivo de centralizar informações importantes da empresa em uma única plataforma, permitindo um gerenciamento mais eficiente dos processos administrativos e operacionais.

Além das funcionalidades de gestão, o projeto possui uma identidade visual inspirada na cultura amazônica, utilizando elementos gráficos relacionados à gastronomia regional e ao jambu, símbolo da culinária paraense.

---

# 2. OBJETIVOS

## Objetivo Geral

Desenvolver uma solução tecnológica capaz de organizar, automatizar e otimizar a gestão de restaurantes.

## Objetivos Específicos

* Gerenciar clientes
* Controlar produtos
* Controlar estoque
* Gerenciar pedidos
* Controlar funcionários
* Gerenciar pagamentos
* Gerar relatórios gerenciais
* Melhorar a tomada de decisões
* Reduzir erros operacionais

---

# 3. ESCOPO DO SISTEMA

O sistema contempla os seguintes processos empresariais:

### Gestão de Clientes

* Cadastro
* Consulta
* Atualização
* Exclusão

### Gestão de Produtos

* Cadastro de produtos
* Categorias
* Fotos
* Controle de preços

### Gestão de Estoque

* Controle de insumos
* Controle de quantidades
* Controle de custos
* Alertas de estoque

### Gestão de Funcionários

* Cadastro
* Controle de acesso
* Controle de permissões

### Gestão de Pedidos

* Pedidos presenciais
* Pedidos online
* Controle de status

### Gestão Financeira

* Registro de pagamentos
* Controle de vendas

### Relatórios Gerenciais

* Indicadores
* Gráficos
* Exportação PDF

---

# 4. PÚBLICO-ALVO

O sistema foi desenvolvido para atender:

* Restaurantes
* Lanchonetes
* Cafeterias
* Hamburguerias
* Casas de comida regional
* Pequenos e médios empreendimentos gastronômicos

---

# 5. TECNOLOGIAS UTILIZADAS

| Tecnologia      | Finalidade                |
| --------------- | ------------------------- |
| Python          | Desenvolvimento principal |
| CustomTkinter   | Interface gráfica moderna |
| Aiven for MySQL | Banco de dados em nuvem   |
| MySQL           | Gerenciamento dos dados   |
| PyMySQL         | Comunicação com o banco   |
| Pillow          | Manipulação de imagens    |
| Matplotlib      | Gráficos                  |
| ReportLab       | Geração de PDF            |
| OpenPyXL        | Exportação de planilhas   |
| Git             | Controle de versão        |
| GitHub          | Hospedagem do projeto     |

---

# 6. ARQUITETURA DO SISTEMA

O sistema utiliza o padrão arquitetural MVC (Model-View-Controller).

## Estrutura Conceitual

Usuário

↓

View

↓

Controller

↓

Model

↓

Database

↓

Aiven Cloud MySQL

---

## View

Responsável pela interface gráfica.

---

## Controller

Responsável pelas regras de negócio.

---

## Model

Responsável pela manipulação dos dados.

---

## Database

Responsável pela conexão e persistência dos dados.

---

# 7. ESTRUTURA DO REPOSITÓRIO

```text
restaurant_system/
│
├── app/
│   ├── controller/
│   ├── database/
│   ├── model/
│   ├── utils/
│   └── view/
│
├── tests/
│
├── main.py
├── README.md
├── requirements.txt
└── .env.example
```

---

# 8. BANCO DE DADOS

O sistema utiliza um banco de dados MySQL hospedado na plataforma Aiven Cloud.

Essa abordagem permite acesso remoto, maior disponibilidade dos dados e escalabilidade futura.

## Arquivos de Configuração

```text
app/database/connection.py
app/database/db_config.py
```

## Variáveis de Ambiente

```text
.env
.env.example
```

## Scripts SQL Existentes

* criar_banco.sql
* adicionando_fk.sql
* dados_clientes.sql
* dados_produtos.sql
* dados_estoque.sql
* dados_funcionario.sql
* dados_pedido.sql
* dados_pagamento.sql
* dados_itens_pedidos.sql
* dados_historico_status.sql
* dados_taxa_cancelamento.sql
* migrate_tempo_estimado_int.sql

## Entidades do Banco

### Clientes

* Nome
* CPF
* Telefone
* Endereço
* E-mail

### Produtos

* Nome
* Categoria
* Descrição
* Preço
* Imagem

### Estoque

* Produto
* Quantidade
* Unidade
* Custo

### Funcionários

* Nome
* Cargo
* Usuário
* Permissões

### Pedidos

* Cliente
* Data
* Status
* Valor Total

### Pagamentos

* Forma de pagamento
* Valor
* Data

---

# 9. MÓDULOS DO SISTEMA

## Login

Arquivos:

* login_view.py
* login_controller.py
* login_model.py

Funções:

* Autenticação
* Controle de acesso

---

## Splash Screen

Arquivo:

* splash_view.py

Função:

* Tela de carregamento inicial

---

## Painel de Controle

Arquivo:

* tela_painel_controle.py

Função:

* Central de navegação do sistema

---

## Clientes

Arquivos:

* clientes_view.py
* clientes_cad_view.py
* cliente_controller.py
* crud_clientes.py

Funções:

* Cadastro
* Consulta
* Edição
* Exclusão

---

## Produtos

Arquivos:

* produto_view_novo.py
* produto_controller.py
* produto_model.py

Funções:

* Cadastro
* Imagens
* Categorias
* Controle de preços

---

## Estoque

Arquivos:

* estoque_view.py
* estoque_controller.py
* estoque_model.py

Funções:

* Controle de insumos
* Quantidade
* Custos
* Alertas

---

## Funcionários

Arquivos:

* funcionarios_view.py
* tela_funcionarios_cad.py
* funcionario_controller.py
* painel_funcionarios_model.py

Funções:

* Cadastro
* Controle de permissões

---

## Caixa

Arquivo:

* caixa_view.py

Funções:

* Registro de vendas
* Pagamentos

---

## Relatórios

Arquivos:

* relatorio_view.py
* relatorio_controller.py
* relatorio_model.py
* pdf_relatorio_controller.py

Funções:

* Indicadores
* Gráficos
* Exportação PDF

---

# 10. FLUXO DE FUNCIONAMENTO

## Cadastro de Cliente

Usuário

↓

Clientes View

↓

Cliente Controller

↓

CRUD Clientes

↓

Banco de Dados

---

## Cadastro de Produto

Usuário

↓

Produto View

↓

Produto Controller

↓

Produto Model

↓

Banco de Dados

---

## Fluxo do Pedido

Pedido Recebido

↓

Em Preparação

↓

Pronto

↓

Saiu para Entrega

↓

Finalizado

---

# 11. COMPONENTES COMPARTILHADOS

## estilos.py

* Cores
* Fontes
* Temas

## componentes.py

* Campos
* Botões
* Cards

## validacoes.py

* CPF
* E-mail
* Telefone

## pdf_generator.py

* Relatórios PDF

## menu_config.py

* Configuração do menu lateral

## botaolateralmenus.py

* Navegação entre telas

## usuario_atual.py

* Controle do usuário logado

## helpers.py

* Funções auxiliares

## gradiente_panel.py

* Componentes visuais com gradiente

---

# 12. PADRÕES DE DESENVOLVIMENTO

## Convenções de Arquivos

### Controller

cliente_controller.py

produto_controller.py

estoque_controller.py

### Model

produto_model.py

pedido_model.py

estoque_model.py

### View

clientes_view.py

estoque_view.py

relatorio_view.py

---

## Convenções de Métodos

salvar()

editar()

excluir()

buscar()

listar()

---

# 13. SEGURANÇA

O projeto adota:

* Controle de autenticação
* Banco hospedado em nuvem (Aiven)
* Variáveis de ambiente
* Separação MVC
* Validação de entradas
* Controle de permissões

---

# 14. CONTROLE DE VERSÃO

Ferramentas utilizadas:

* Git
* GitHub

Branch principal:

main

Boas práticas:

* Commits descritivos
* Atualizações frequentes
* Versionamento contínuo

---

# 15. TESTES

Pasta:

```text
tests/
```

Objetivos:

* Garantir estabilidade
* Identificar falhas
* Validar funcionalidades

---

# 16. ROADMAP

## Versão 1.1

* Dashboard avançado

## Versão 1.2

* Melhorias no módulo de pedidos

## Versão 1.3

* Tema Escuro inspirado no Açaí

## Versão 2.0

* Aplicativo Mobile

## Versão 2.1

* API REST

## Versão 2.2

* Sistema multilíngue
* Português
* Inglês
* Espanhol

## Versão 2.3

* Recursos de acessibilidade
* Libras
* Alto contraste
* Leitor de tela

---

# 17. CONCLUSÃO

O Sabores do Pará foi desenvolvido para oferecer uma solução moderna, organizada e escalável para gestão de restaurantes e lanchonetes.

A utilização da arquitetura MVC, banco de dados em nuvem através do Aiven Cloud Database, interface desenvolvida em CustomTkinter e integração de recursos gerenciais torna o projeto uma solução robusta e preparada para futuras expansões.

Mais do que um sistema de gestão, o projeto representa a união entre tecnologia, inovação e valorização da cultura gastronômica amazônica.

---

**Documento Oficial do Projeto**

**Sabores do Pará – Sistema de Gestão para Restaurantes e Lanchonetes**

**Versão 1.0.0**

**SENAC – Programador de Sistemas – Projeto Integrador**


