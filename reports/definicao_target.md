# Definição da variável-alvo

## Resumo

A variável-alvo é o `nps_score`, convertido em `is_detractor` (nota abaixo de 7, sem arredondamento) para o modelo de risco. Foi escolhido por ser o indicador que a empresa quer melhorar, comparável com o mercado e coletado por pedido. A nota é registrada na pesquisa enviada após o fim da jornada; por isso, o modelo usa apenas informações disponíveis logo após a entrega. O principal risco é o vazamento de dados, tratado ao manter fora do modelo o CSAT, a recompra e qualquer registro posterior à pesquisa (D-06).

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

Duas distinções orientam o uso da variável. O `nps_score` é a nota de cada cliente, e o NPS é a métrica do grupo. O modelo estima o risco de cada cliente, enquanto a gestão acompanha o NPS e a proporção de detratores ([D-02](registro_decisoes.md#d-02-proporção-de-detratores-como-indicador-alvo)). O NPS também mede intenção de recomendar, que é próxima de satisfação, mas não igual. Um cliente satisfeito pode não recomendar por não ter a quem, e a nota não diz qual falha pesou.

A definição operacional abaixo vale para todo o projeto, da preparação dos dados ao modelo:

| Atributo | Regra | Uso |
| --- | --- | --- |
| `nps_category` | Detrator se `nps_score` < 7; neutro se 7 ≤ `nps_score` < 9; promotor se `nps_score` ≥ 9 | Cálculo do NPS e comparação de segmentos |
| `is_detractor` | 1 se `nps_score` < 7; 0 nos demais casos | Variável-alvo do modelo de risco |

A base registra notas com uma casa decimal, como 6,9, e as faixas do NPS foram definidas para notas inteiras. As faixas são aplicadas direto sobre a nota original, sem arredondamento ([D-05](registro_decisoes.md#d-05-corte-direto-nas-faixas-do-nps-para-notas-com-casa-decimal)). Um 8,6 ainda não chegou a 9 e segue neutro; um 6,9 fica como detrator, o lado conservador quando o objetivo é não deixar cliente em risco sem atenção. Arredondar criaria promotores e neutros que a nota não atingiu e inflaria o NPS. Na Etapa 3, as duas regras levaram à mesma conclusão: pelo corte direto, 84,4% dos pedidos são de detratores e o NPS é −80,0; pelo arredondamento, seriam 79,0% e −72,8 ([notebook de qualidade, seção 3](../notebooks/01_qualidade_e_tratamento.ipynb)). A D-05 se mantém. Com o detrator como grande maioria, a análise exploratória revê as métricas da D-03 antes de fixar os alvos do modelo.

## 3. Momento da coleta e variáveis disponíveis

O NPS é coletado depois do encerramento da jornada de compra, segundo o briefing, e se refere ao pedido avaliado: o dicionário descreve a nota como "coletada após a experiência de compra". O momento de coleta do CSAT não é informado.

Como o score de risco é calculado logo após a entrega ([D-04](registro_decisoes.md#d-04-score-de-risco-calculado-após-a-entrega)), só pode entrar no modelo o que já existe nesse momento. A tabela mostra quando cada variável passa a existir e o uso permitido:

| Momento | Variáveis | Uso no modelo |
| --- | --- | --- |
| Cadastro e histórico | `customer_age`, `customer_region`, `customer_tenure_months` | Entram |
| Checkout | `order_value`, `items_quantity`, `discount_value`, `payment_installments`, `freight_value` | Entram |
| Entrega | `delivery_time_days`, `delivery_delay_days`, `delivery_attempts` | Entram |
| Atendimento, durante a jornada | `customer_service_contacts`, `complaints_count`, `resolution_time_days` | Entram com o que foi registrado até a predição |
| Pesquisa, após o fim da jornada | `nps_score` | É a variável-alvo |
| Não informado | `csat_internal_score` | Fica fora; serve para validar a variável-alvo |
| Até 30 dias após o pedido | `repeat_purchase_30d` | Fica fora: é consequência da experiência |
| Identificação | `customer_id`, `order_id` | Ficam fora; `customer_id` serve para separar treino e teste por cliente, se houver clientes com mais de um pedido |

Duas premissas sustentam a tabela:

- **CSAT:** o dicionário não informa quando ele é coletado. Na dúvida, ele é tratado como coletado junto com a pesquisa ou depois dela; fica fora do modelo e serve para validar a variável-alvo.
- **Atendimento:** contatos, reclamações e tempo de resolução são tratados como registros anteriores à pesquisa e independentes entre si, sem garantia de que se refiram ao pedido avaliado ([D-09](registro_decisoes.md#d-09-registros-de-atendimento-lidos-como-independentes)). Em produção, só entra o que estiver registrado no momento da predição. Na base histórica os valores são finais, o que pode deixar a avaliação do modelo otimista; a Etapa 6 mede esse efeito treinando também sem `resolution_time_days`.

A lista de variáveis permitidas está formalizada na [D-06](registro_decisoes.md#d-06-variáveis-permitidas-no-modelo-de-risco).

## 4. Riscos de uso inadequado

Cada risco abaixo vem acompanhado da decisão do projeto que o previne.

| Risco | Como aparece | Como o projeto evita |
| --- | --- | --- |
| Vazamento de dados | Um modelo treinado com CSAT ou recompra acerta quase tudo no teste e falha na operação, porque essas variáveis só existem depois da pesquisa | D-06: só entram variáveis disponíveis no momento da predição |
| Causalidade reversa | Reclamação e recompra podem ser efeito da insatisfação, e não causa: o cliente reclama porque já está insatisfeito | Achados descritos como associação; a reclamação é analisada junto com a falha que a originou, como o atraso |
| Nota tratada como número contínuo | A média esconde o NPS: se todos dão 8, a média é 8 e o NPS é 0; se metade dá 9 e metade dá 7, a média continua 8, mas o NPS é +50 | D-02: segmentos comparados por proporção de detratores e NPS, nunca pela nota média |
| Não resposta | Só tem nota quem respondeu, e quem responde tende a ter opinião mais forte | A Etapa 3 não encontrou notas ausentes: a base traz só quem respondeu, e a taxa de resposta segue como métrica de proteção ([seção 2 do entendimento do negócio](entendimento_negocio.md#2-metas-e-critérios-de-sucesso)) |
| Nota influenciada pelo último evento | A nota pesa o que aconteceu por último e o humor do dia, não a jornada inteira | A nota é lida como avaliação daquele pedido, e a ação é por faixa de risco, não por nota exata |
| Uso diferente da escala | Regiões e perfis dão notas diferentes para a mesma experiência | Regiões comparadas dentro da mesma faixa de atraso (H7 do [entendimento do negócio](entendimento_negocio.md#8-hipóteses-para-a-análise-exploratória)) e erro do modelo verificado por grupo |
| NPS como meta de equipe | A nota sobe sem melhora real, por exemplo com pedido explícito de nota 10 ou escolha de quem recebe a pesquisa | Métricas de proteção; a equipe avaliada não escolhe quem recebe a pesquisa |
| Clientes com vários pedidos | Clientes frequentes pesam mais na análise, e o mesmo cliente pode cair no treino e no teste | A Etapa 3 não encontrou `customer_id` repetido: cada cliente tem um único pedido, e treino e teste não precisam ser separados por cliente |
| Uso discriminatório de idade e região | Clientes tratados de forma desigual por atributos pessoais | Idade e região usadas só no diagnóstico e na checagem de erro do modelo por grupo, conforme a LGPD |
| Valores finais de atendimento na base histórica | O tempo de resolução registrado pode incluir o que aconteceu depois da predição, e a avaliação do modelo fica otimista | Teste do modelo sem `resolution_time_days` na Etapa 6 (D-06) |

O vazamento é o risco de maior impacto, porque só aparece quando o modelo já está em operação; a D-06 é a principal proteção contra ele.
