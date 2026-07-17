CREATE DATABASE sabores_do_para_v2;

USE sabores_do_para_v2;

CREATE TABLE IF NOT EXISTS clientes(
id_cliente INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
nome VARCHAR(200) NOT NULL,
telefone VARCHAR(20) NOT NULL,
cpf CHAR(14) UNIQUE NOT NULL,
numero VARCHAR(10),
bairro VARCHAR(60) NOT NULL,
cidade VARCHAR(60) NOT NULL,
email VARCHAR(50) UNIQUE NOT NULL,
cep VARCHAR(8) NOT NULL,
complemento VARCHAR(100) NOT NULL,
logradouro VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS pedido (
id_pedido INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
tipo_de_pedido ENUM('presencial','delivery', 'retirada')  NOT NULL,
status_do_pedido ENUM('criado','confirmado','recebido','em_preparo','pronto', 'entregue','concluido','cancelado') NOT NULL DEFAULT 'criado',
data_do_pedido DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
tempo_estimado INT DEFAULT NULL,
timer_iniciado_em DATETIME NULL,
timer_status ENUM('normal','atrasado') DEFAULT NULL,
timer_concluido_em DATETIME DEFAULT NULL,
num_revertido INT DEFAULT 0,
valor_total DECIMAL(10,2) NOT NULL DEFAULT 0.00,
taxa_entrega DECIMAL(10,2) DEFAULT 0.00,
momento_cobranca ENUM('antecipado','na_entrega') DEFAULT NULL,
origem ENUM('balcao', 'mesa', 'delivery') NOT NULL,
num_mesa INT NULL,
observacoes TEXT,
id_cliente INT NOT NULL,
id_funcionario INT NOT NULL,
FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
FOREIGN KEY (id_funcionario) REFERENCES funcionario(id_funcionario),

INDEX idx_pedido_data (data_do_pedido),
INDEX idx_pedido_status (status_do_pedido)

);

CREATE TABLE IF NOT EXISTS produto (
id_produto INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
nome VARCHAR(200) NOT NULL,
preco DECIMAL(10,2)NOT NULL CHECK(preco > 0),
categoria VARCHAR(100) NOT NULL,
estoque INT DEFAULT 0,
descricao TEXT,
status VARCHAR(20) DEFAULT 'Ativo',
foto VARCHAR(500) DEFAULT NULL,
unidade VARCHAR(100) DEFAULT 'Porção'
);

CREATE TABLE IF NOT EXISTS item_pedido (
id_item INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
id_pedido INT NOT NULL,
id_produto INT NOT NULL,
quantidade INT NOT NULL DEFAULT 1,
preco_unitario DECIMAL(10,2) NOT NULL,
observacoes TEXT NULL,
FOREIGN KEY (id_pedido) REFERENCES pedido(id_pedido),
FOREIGN KEY (id_produto) REFERENCES produto(id_produto)
);

CREATE TABLE IF NOT EXISTS funcionario (
id_funcionario INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
nome VARCHAR(200) NOT NULL,
email VARCHAR(100) UNIQUE NOT NULL,
senha_hash VARCHAR(255) NOT NULL,
cargo VARCHAR(100) NOT NULL,
nivel_acesso ENUM('funcionario','administrador') NOT NULL DEFAULT 'funcionario',
ativo BOOLEAN DEFAULT TRUE,
data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
telefone VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS pagamento (
id_pagamento INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
valor DECIMAL(10,2) NOT NULL DEFAULT 0.00,
tipo_de_pagamento ENUM('dinheiro','pix','cartao') NOT NULL,
detalhes VARCHAR(100) NULL,
status_pagamento ENUM('pendente','pago','nao_efetuado','estornado') DEFAULT 'pendente',
data_pagamento DATETIME DEFAULT CURRENT_TIMESTAMP,
id_pedido INT NOT NULL,
id_taxa_cancelamento INT NULL,
FOREIGN KEY (id_pedido) REFERENCES pedido(id_pedido),
FOREIGN KEY (id_taxa_cancelamento) REFERENCES taxa_cancelamento(id_taxa_cancelamento),

INDEX idx_pagamento_status (status_pagamento)

);

CREATE TABLE IF NOT EXISTS taxa_cancelamento (
id_taxa_cancelamento INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
valor DECIMAL(10,2) NOT NULL DEFAULT 0.00,
id_cliente INT NOT NULL,
id_pedido INT NOT NULL,
FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
FOREIGN KEY (id_pedido) REFERENCES pedido(id_pedido)
);

CREATE TABLE IF NOT EXISTS historico_status (
id_historico INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
id_pedido INT NOT NULL,
status VARCHAR(30) NOT NULL,
id_funcionario INT NOT NULL,
data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (id_pedido) REFERENCES pedido(id_pedido),
FOREIGN KEY (id_funcionario) REFERENCES funcionario(id_funcionario),

INDEX idx_historico_pedido_data (id_pedido, data_hora)
);

CREATE TABLE IF NOT EXISTS estoque (
id_estoque INT AUTO_INCREMENT PRIMARY KEY,
nome VARCHAR(200) NOT NULL,
descricao VARCHAR(200) DEFAULT '',
quantidade INT NOT NULL DEFAULT 0,
unidade VARCHAR(20) NOT NULL,
categoria VARCHAR(100) NOT NULL,
quantidade_minima INT DEFAULT 0,
preco_unitario DECIMAL(10,2) DEFAULT 0
);

CREATE TABLE IF NOT EXISTS enderecos (
    id_endereco INT PRIMARY KEY AUTO_INCREMENT,
id_cliente INT NULL,
    apelido VARCHAR(100),           -- "Casa", "Trabalho", "Mãe"
    cep VARCHAR(10),
    logradouro VARCHAR(255),
    numero VARCHAR(20),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    complemento VARCHAR(255),
    principal BOOLEAN DEFAULT 0,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE CASCADE
);


ALTER TABLE pedido
ADD COLUMN id_entregador INT NULL AFTER taxa_entrega,
ADD CONSTRAINT fk_pedido_entregador 
    FOREIGN KEY (id_entregador) REFERENCES funcionario(id_funcionario);ALTER TABLE funcionario; 
    
    
ALTER TABLE funcionario 
ADD COLUMN is_entregador BOOLEAN DEFAULT FALSE AFTER cargo;

ALTER TABLE pedido
ADD COLUMN id_endereco INT NULL AFTER id_cliente,
ADD CONSTRAINT fk_pedido_endereco 
    FOREIGN KEY (id_endereco) REFERENCES enderecos(id_endereco);

CREATE TABLE IF NOT EXISTS taxa_entrega (
    id_taxa INT AUTO_INCREMENT PRIMARY KEY,
    bairro VARCHAR(100) NOT NULL,
    valor DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    ativo BOOLEAN DEFAULT 1,
    UNIQUE KEY uk_bairro (bairro)
);

INSERT IGNORE INTO taxa_entrega (bairro, valor) VALUES
    ('Marco', 5.00),
    ('Umarizal', 4.00),
    ('Pedreira', 6.00),
    ('Batista Campos', 5.00),
    ('Nazaré', 4.50),
    ('Telégrafo', 5.50),
    ('Cremação', 7.00),
    ('Marambaia', 8.00),
    ('Benguí', 7.50),
    ('Coqueiro', 9.00);