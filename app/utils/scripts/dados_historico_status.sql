-- HISTÓRICO DE STATUS
INSERT INTO historico_status (
    id_pedido,
    status,
    id_funcionario
) VALUES

-- Pedido 1
(1, 'criado', 2),
(1, 'confirmado', 2),
(1, 'em_preparo', 3),
(1, 'entregue', 4),

-- Pedido 2
(2, 'criado', 2),
(2, 'confirmado', 2),
(2, 'concluido', 2),

-- Pedido 3
(3, 'criado', 2),
(3, 'confirmado', 2),
(3, 'pronto', 3),
(3, 'concluido', 2),

-- Pedido 4
(4, 'criado', 2),
(4, 'confirmado', 2),
(4, 'em_preparo', 3),

-- Pedido 5
(5, 'criado', 2),
(5, 'recebido', 2),

-- Pedido 6
(6, 'criado', 2),
(6, 'confirmado', 2),

-- Pedido 7
(7, 'criado', 2),
(7, 'confirmado', 2),
(7, 'pronto', 3),

-- Pedido 8
(8, 'criado', 2),
(8, 'confirmado', 2),
(8, 'concluido', 2),

-- Pedido 9
(9, 'criado', 2),

-- Pedido 10
(10, 'criado', 2),
(10, 'confirmado', 2),
(10, 'em_preparo', 3);