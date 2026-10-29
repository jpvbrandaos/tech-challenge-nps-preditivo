# Dicionário de dados

| Coluna | Descrição | Momento da jornada |
| --- | --- | --- |
| customer_id | Identificador único do cliente | Identificação |
| order_id | Identificador único do pedido | Identificação |
| customer_age | Idade do cliente | Cadastro |
| customer_region | Região geográfica do cliente | Cadastro |
| customer_tenure_months | Tempo de relacionamento do cliente com a empresa (em meses) | Cadastro |
| order_value | Valor total do pedido | Checkout |
| items_quantity | Quantidade de itens no pedido | Checkout |
| discount_value | Valor de desconto aplicado ao pedido | Checkout |
| payment_installments | Número de parcelas do pagamento | Checkout |
| delivery_time_days | Tempo total de entrega (em dias) | Entrega |
| delivery_delay_days | Quantidade de dias de atraso na entrega | Entrega |
| freight_value | Valor do frete | Checkout |
| delivery_attempts | Número de tentativas de entrega | Entrega |
| customer_service_contacts | Número de contatos do cliente com o atendimento | Atendimento |
| resolution_time_days | Tempo para resolução de problemas (em dias) | Atendimento |
| complaints_count | Número de reclamações registradas pelo cliente | Atendimento |
| repeat_purchase_30d | Indica se houve recompra em até 30 dias após o pedido (0 = não, 1 = sim) | Após a pesquisa |
| csat_internal_score | Score interno de satisfação do cliente | Não informado |
| nps_score | Nota de satisfação do cliente (NPS), de 0 a 10, coletada após a experiência de compra | Pesquisa |

## Leituras adotadas no projeto

Em três pontos, a base não corresponde à descrição acima, e o projeto adota outra leitura:

- `delivery_time_days` é a previsão de entrega informada ao cliente, e `delivery_delay_days`, os dias além dela ([D-07](../reports/registro_decisoes.md#d-07-tempo-de-entrega-lido-como-previsão)).
- `order_value` é o valor do pedido já com o desconto aplicado; o preço cheio é `order_value` + `discount_value` ([D-08](../reports/registro_decisoes.md#d-08-valor-do-pedido-lido-como-líquido-do-desconto)).
- `customer_service_contacts`, `complaints_count` e `resolution_time_days` são registros independentes, sem regra de coerência entre eles ([D-09](../reports/registro_decisoes.md#d-09-registros-de-atendimento-lidos-como-independentes)).

A base é tratada como simulada, e as conclusões valem como demonstração de método ([D-10](../reports/registro_decisoes.md#d-10-base-tratada-como-simulada)).

## Atributos da base tratada

Calculados por `build_features`, em [`src/features.py`](../src/features.py), e salvos em `data/processed/base_tratada.csv` pelo comando `python -m src.features`. As faixas são fechadas à direita: 2 dias de atraso caem em "1 a 2 dias".

| Atributo | Definição | Pergunta que responde |
| --- | --- | --- |
| nps_category | Detrator se `nps_score` < 7; neutro de 7 até antes de 9; promotor a partir de 9, sem arredondar (D-05) | Qual é o NPS de cada segmento? |
| is_detractor | 1 se `nps_category` é detrator; 0 nos demais casos | Variável-alvo do modelo de risco |
| is_late | 1 se `delivery_delay_days` > 0 | Quantos pedidos passam da previsão? |
| delay_bucket | Faixas de atraso: sem atraso, 1 a 2 dias, 3 a 4 dias, 5 dias ou mais | Quanto atraso o cliente tolera? |
| actual_delivery_days | `delivery_time_days` + `delivery_delay_days` (D-07) | Quanto o cliente esperou de fato? |
| discount_pct | `discount_value` ÷ (`order_value` + `discount_value`) (D-08) | O desconto relativo pesa na nota? |
| freight_pct | `freight_value` ÷ `order_value` | Frete caro frustra? |
| avg_item_value | `order_value` ÷ `items_quantity` | Qual é o valor médio por item? |
| had_contact | 1 se `customer_service_contacts` > 0 | O cliente precisou do atendimento? |
| multiple_attempts | 1 se `delivery_attempts` > 1 | A entrega exigiu nova tentativa? |
| tenure_bucket | Faixas de relacionamento: até 1 ano, 1 a 3 anos, 3 a 5 anos, mais de 5 anos | Clientes antigos toleram mais falhas? |
| age_bucket | Faixas de idade: 18 a 24, 25 a 34, 35 a 44, 45 a 54, 55 ou mais | Que perfis concentram detratores? |
| friction_score | Soma de quatro falhas, de 0 a 4: atraso, nova tentativa, contato com o atendimento e resolução acima de 7 dias (D-09) | Quanto cada falha a mais pesa na nota? |
