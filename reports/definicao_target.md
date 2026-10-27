# Definição da variável-alvo

## Resumo
## 1. Variável que representa a satisfação

Três colunas da base medem algo próximo de satisfação. A comparação abaixo define o papel de cada uma no projeto.

| Candidata | O que mede | Quando é registrada | Papel no projeto |
| --- | --- | --- | --- |
| `nps_score` | Intenção de recomendar a empresa, de 0 a 10 | Na pesquisa enviada após o fim da jornada | Variável-alvo: é o indicador que a empresa quer melhorar |
| `csat_internal_score` | Satisfação do cliente, em escala interna não documentada | Não informado no dicionário de dados | Validação da variável-alvo; fica fora do modelo pelo risco de vazamento de dados |
| `repeat_purchase_30d` | Comportamento: se o cliente voltou a comprar em até 30 dias | Até 30 dias após o pedido, depois da pesquisa | Evidência do valor do NPS; fica fora do modelo por ser consequência da experiência |

A variável-alvo é o `nps_score`: é o indicador que a empresa quer melhorar e o único dos três que mede a opinião do cliente com escala e momento de coleta conhecidos. O CSAT e a recompra entram como validação e como evidência, não como alvo.

## 2. Por que o `nps_score`

O `nps_score` é o indicador que a empresa já acompanha e quer melhorar: o briefing descreve o problema como a variação do NPS entre perfis de clientes. É comparável com o mercado, desde que se respeite a diferença entre NPS transacional e relacional ([seção 3 do entendimento do negócio](entendimento_negocio.md#3-por-que-o-nps-importa-para-um-e-commerce)). E é coletado por pedido, o que permite ligar cada nota às falhas daquela jornada.

Duas distinções orientam o uso da variável. O `nps_score` é a nota de cada cliente, e o NPS é a métrica do grupo: o modelo estima o risco de cada cliente, enquanto a gestão acompanha o NPS e a proporção de detratores ([D-02](registro_decisoes.md#d-02-proporção-de-detratores-como-indicador-alvo)). O NPS também mede intenção de recomendar, que é próxima de satisfação, mas não igual: um cliente satisfeito pode não recomendar por não ter a quem, e a nota não diz qual falha pesou.

A definição operacional abaixo vale para todo o projeto, da preparação dos dados ao modelo:

| Atributo | Regra | Uso |
| --- | --- | --- |
| `nps_category` | Detrator se `nps_score` < 7; neutro se 7 ≤ `nps_score` < 9; promotor se `nps_score` ≥ 9 | Cálculo do NPS e comparação de segmentos |
| `is_detractor` | 1 se `nps_score` < 7; 0 nos demais casos | Variável-alvo do modelo de risco |

A base registra notas com uma casa decimal, como 6,9, e as faixas do NPS foram definidas para notas inteiras. As faixas são aplicadas direto sobre a nota original, sem arredondamento ([D-05](registro_decisoes.md#d-05-corte-direto-nas-faixas-do-nps-para-notas-com-casa-decimal)). Um 8,6 ainda não chegou a 9 e segue neutro; um 6,9 fica como detrator, o lado conservador quando o objetivo é não deixar cliente em risco sem atenção. Arredondar criaria promotores e neutros que a nota não atingiu e inflaria o NPS. A Etapa 3, de qualidade dos dados, mede a diferença entre as duas regras.

## 3. Momento da coleta e variáveis disponíveis
## 4. Riscos de uso inadequado
