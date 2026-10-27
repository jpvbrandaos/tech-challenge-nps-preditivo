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
## 3. Momento da coleta e variáveis disponíveis
## 4. Riscos de uso inadequado
