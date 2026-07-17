USE sabores_do_para;

INSERT INTO pedido (
    tipo_de_pedido,
    status_do_pedido,
    tempo_estimado,
    valor_total,
    taxa_entrega,
    origem,
    num_mesa,
    observacoes,
    id_cliente,
    id_funcionario
) VALUES
('delivery', 'entregue', 40, 27.00, 5.00, 'balcao', NULL, 'Entregar sem talheres',1,1),
('retirada', 'concluido', 25, 39.00, 0.00, 'balcao', NULL, 'Cliente retira às 12h',1,1),
('presencial', 'concluido', 20, 34.00, 0.00, 'mesa', 3, 'Mesa próxima à janela',1,1),
('delivery', 'em_preparo', 45, 52.00, 6.00, 'balcao', NULL, 'Adicionar maionese',1,1),
('presencial', 'recebido', 15, 20.00, 0.00, 'mesa', 5, NULL,1,1),
('delivery', 'confirmado', 35, 38.00, 5.00, 'balcao', NULL, 'Sem pimenta',1,1),
('retirada', 'pronto', 30, 17.00, 0.00, 'balcao', NULL, NULL,1,1),
('presencial', 'concluido', 25, 40.00, 0.00, 'mesa', 2, 'Pedido compartilhado',1,1),
('delivery', 'criado', 50, 54.00, 7.00, 'balcao', NULL, 'Troco para 100',1,1),
('presencial', 'em_preparo', 20, 19.00, 0.00, 'mesa', 1, NULL,1,1);