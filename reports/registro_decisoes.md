# Registro de decisões

Decisões que afetam escopo, dados, métricas ou método do projeto. Cada entrada registra contexto, alternativas avaliadas, justificativa e consequências. Uma decisão aceita não é editada: se for revista, a revisão entra como nova decisão, e a anterior passa a constar como substituída.

## D-01: Base de dados fora do controle de versão

- **Status:** aceita em 23/10/2026
- **Contexto:** a base é um arquivo CSV publicado num repositório público do GitHub, que é a fonte oficial dos dados.
- **Decisão:** o arquivo não é versionado. A pasta `data/` fica no `.gitignore`, e o comando `python -m src.dataset` baixa a base da fonte oficial para `data/raw/` e confere o SHA-256 antes do uso.
- **Alternativas consideradas:** versionar o CSV em `data/raw/`; versionar com DVC ou Git LFS.
- **Justificativa:** a fonte oficial continua única, sem cópias que possam divergir, e o hash garante que toda execução use o mesmo arquivo. DVC e Git LFS acrescentariam infraestrutura sem ganho para um arquivo estático e público.
- **Consequências:** um clone novo não traz a base, e a reprodução começa pelo download, que exige acesso à internet. Se a fonte alterar o arquivo, a conferência do hash interrompe a execução, e a nova versão só entra no projeto por meio de uma nova decisão.

## D-02: Proporção de detratores como indicador-alvo

- **Status:** aceita em 26/10/2026
- **Contexto:** o NPS agrega promotores e detratores num único número, e o mesmo valor pode resultar de distribuições muito diferentes. As ações ao alcance da operação, como reduzir atrasos, acelerar a resolução e compensar falhas, atuam sobre pedidos com experiência ruim.
- **Decisão:** a meta de negócio é a proporção de detratores. O NPS segue como indicador de acompanhamento.
- **Alternativas consideradas:** usar o NPS como meta; usar a nota média.
- **Justificativa:** converter um detrator em neutro tem no NPS o mesmo efeito que converter um neutro em promotor, e é no detrator que se espera encontrar falhas operacionais corrigíveis. A nota média trata uma escala ordinal como contínua e não corresponde a nenhum indicador acompanhado pela empresa.
- **Consequências:** segmentos são comparados por proporção de detratores e NPS, nunca pela nota média. A definição operacional de detrator, incluindo a regra para notas com casa decimal, fica para a Etapa 2.

## D-03: Critérios de sucesso fixados antes da análise

- **Status:** aceita em 26/10/2026
- **Contexto:** métricas e limiares escolhidos depois de ver os resultados tendem a se ajustar a eles, o que compromete a avaliação.
- **Decisão:** os critérios de sucesso ficam registrados na [seção 2 do entendimento do negócio](entendimento_negocio.md#2-metas-e-critérios-de-sucesso) antes de qualquer análise. O modelo é avaliado por PR-AUC e pela proporção de detratores capturados entre os 20% de maior risco, sempre contra o modelo ingênuo e a melhor regra simples da análise exploratória. Os valores-alvo são fixados ao fim da análise exploratória, antes do treino de qualquer modelo.
- **Alternativas consideradas:** definir métricas e alvos depois da modelagem; usar acurácia ou ROC-AUC como métrica principal.
- **Justificativa:** a operação vai agir sobre uma lista priorizada de clientes, e PR-AUC e captura no topo medem a qualidade dessa lista. Se os detratores forem minoria, a acurácia favorece o modelo que nunca aponta risco, e a ROC-AUC pode ser alta mesmo com precisão baixa no topo do ranking.
- **Consequências:** trocar de métrica ou de corte depois de ver os resultados exige nova decisão justificada. O corte de 20% reflete uma capacidade de contato ainda não validada com o atendimento.

## D-04: Score de risco calculado após a entrega

- **Status:** aceita em 26/10/2026
- **Contexto:** a pesquisa de NPS só chega depois do fim da jornada. Para agir antes dela, o risco precisa ser estimado quando as falhas da operação já são conhecidas e ainda há tempo de intervir.
- **Decisão:** o score de risco de detrator é calculado logo após a entrega, com dados de cadastro, pedido, entrega e atendimento registrados até esse momento.
- **Alternativas consideradas:** calcular no checkout, só com dados de cadastro e pedido.
- **Justificativa:** após a entrega, atrasos e tentativas frustradas já aconteceram, e ainda cabem contato e compensação antes da pesquisa. No checkout, o score ignoraria justamente as falhas que o diagnóstico precisa priorizar.
- **Consequências:** variáveis posteriores à pesquisa, como a recompra em 30 dias, ficam fora do modelo, e a lista de variáveis permitidas sai do mapa da jornada, na Etapa 2. O cenário de checkout pode servir de comparação, para medir quanto valem os dados de entrega e atendimento.

## D-05: Corte direto nas faixas do NPS para notas com casa decimal

- **Status:** aceita em 27/10/2026
- **Contexto:** a base registra notas com uma casa decimal, como 6,9, e as faixas do NPS foram definidas para notas inteiras de 0 a 10.
- **Decisão:** as faixas são aplicadas direto sobre a nota original: detrator abaixo de 7, neutro de 7 até antes de 9 e promotor a partir de 9, sem arredondamento.
- **Alternativas consideradas:** arredondar a nota para o inteiro mais próximo antes de classificar.
- **Justificativa:** o corte direto não altera o dado e não cria promotores nem neutros que a nota não atingiu: um 8,6 ainda não chegou a 9. Notas como 6,9 ficam como detrator, o lado conservador para um modelo cuja função é não deixar cliente em risco sem atenção. O arredondamento traz ainda uma armadilha de implementação: o `round` do Python arredonda 6,5 para 6 e 7,5 para 8.
- **Consequências:** `nps_category` e `is_detractor` seguem esta regra em todo o projeto. A Etapa 3 calcula a proporção de detratores pelas duas regras e registra a diferença.

## D-06: Variáveis permitidas no modelo de risco

- **Status:** aceita em 27/10/2026
- **Contexto:** o score é calculado logo após a entrega (D-04), e a base mistura informações anteriores e posteriores à pesquisa de NPS. O dicionário não informa quando o CSAT é coletado.
- **Decisão:** entram no modelo os dados de cadastro, pedido e entrega e os registros de atendimento existentes até o momento da predição. Ficam fora o `nps_score`, que é o alvo, o `csat_internal_score`, a `repeat_purchase_30d` e os identificadores.
- **Alternativas consideradas:** usar todas as variáveis da base; manter o CSAT como preditora.
- **Justificativa:** uma variável registrada depois da pesquisa antecipa o resultado que o modelo deveria prever: ele vai bem no teste e falha na operação. Como o momento do CSAT é desconhecido, excluí-lo é o lado seguro.
- **Consequências:** a Etapa 6 inclui um experimento de vazamento, que treina também com o CSAT para mostrar o desempenho artificialmente alto, e um teste sem `resolution_time_days`. O `customer_id` não entra como preditor, mas separa treino e teste por cliente se houver clientes com mais de um pedido.

## D-07: Tempo de entrega lido como previsão

- **Status:** aceita em 28/10/2026
- **Contexto:** o dicionário descreve `delivery_time_days` como "Tempo total de entrega (em dias)", e a premissa P3 supunha o atraso contido nele. Na seção 2.2 do [notebook de qualidade](../notebooks/01_qualidade_e_tratamento.ipynb), 121 pedidos (4,8%) têm atraso maior que o tempo de entrega, o que seria impossível se a coluna fosse o tempo total. A amostra da seção 2.3 mostra esses casos em prazos curtos, de 2 a 4 dias.
- **Decisão:** `delivery_time_days` é a previsão de entrega informada ao cliente, e `delivery_delay_days`, os dias além dessa previsão. O tempo real de entrega é a soma das duas.
- **Alternativas consideradas:** manter a leitura do dicionário e excluir os 121 pedidos como erro de registro; manter a leitura e apenas registrar a incoerência.
- **Justificativa:** lida como previsão, a coluna torna coerentes todos os pedidos, sem exclusão. Prazos curtos são os mais fáceis de estourar, o que explica onde os casos se concentram. Excluí-los tiraria da base justamente as entregas que mais passaram do prometido.
- **Consequências:** o atributo `promised_days`, previsto para derivar o prazo prometido, sai do plano, e entra `actual_delivery_days`, a previsão somada ao atraso. A premissa P3 é revista no entendimento do negócio, e o dicionário de dados registra a leitura.

## D-08: Valor do pedido lido como líquido do desconto

- **Status:** aceita em 28/10/2026
- **Contexto:** o dicionário descreve `order_value` como "Valor total do pedido", sem dizer se o desconto já está aplicado. Na seção 2.2 do [notebook de qualidade](../notebooks/01_qualidade_e_tratamento.ipynb), 35 pedidos (1,4%) têm desconto maior que o valor do pedido, e a amostra da seção 2.3 mostra apenas pedidos baratos.
- **Decisão:** `order_value` é o valor do pedido já com o desconto aplicado. O preço cheio é a soma de `order_value` e `discount_value`.
- **Alternativas consideradas:** ler o valor como bruto e excluir os 35 pedidos; manter a leitura do dicionário e apenas registrar a dúvida.
- **Justificativa:** a leitura líquida explica por que os casos aparecem em pedidos baratos: um desconto que pesa pouco num pedido caro passa do valor pago num pedido barato. Ela torna coerentes todos os pedidos, sem exclusão.
- **Consequências:** o `discount_pct` passa a ser o desconto dividido pelo preço cheio e fica sempre abaixo de 1. A regra "desconto maior que o valor do pedido" deixa de indicar erro. O dicionário de dados registra a leitura.

## D-09: Registros de atendimento lidos como independentes

- **Status:** aceita em 28/10/2026
- **Contexto:** as regras da seção 2.2 do [notebook de qualidade](../notebooks/01_qualidade_e_tratamento.ipynb) supunham que reclamações e tempo de resolução decorrem dos contatos com o atendimento. A base mostra outra coisa: 2.428 pedidos (97,1%) têm mais reclamações que contatos, e 511 (20,4%) têm tempo de resolução sem nenhum contato. Como cada cliente tem um único pedido (seção 2.1), a premissa P2, de que esses registros se referem ao pedido avaliado, não pode ser testada.
- **Decisão:** `customer_service_contacts`, `complaints_count` e `resolution_time_days` são lidos como registros independentes, sem regra de coerência entre eles. As análises descrevem as reclamações como registros do cliente, sem atribuí-las ao atendimento daquele pedido.
- **Alternativas consideradas:** ler as três colunas como registros do pedido e apenas anotar a incoerência; excluir os pedidos incoerentes.
- **Justificativa:** a incoerência atinge quase toda a base, então não é erro pontual, e sim outra definição das colunas. Excluir os pedidos esvaziaria a base, e manter a leitura do dicionário levaria a conclusões sobre um vínculo que os dados não mostram.
- **Consequências:** o atributo `had_complaint` sai do plano, porque quase todo cliente tem reclamação registrada (seções 1 e 2.6) e o indicador não distingue ninguém. No `friction_score` e na hipótese H8, a reclamação dá lugar ao contato com o atendimento. A premissa P2 é revista no entendimento do negócio.

## D-10: Base tratada como simulada

- **Status:** aceita em 28/10/2026
- **Contexto:** a premissa P5 tratava a base como registro real da operação até a Etapa 3 procurar sinais de simulação. Na seção 2.6 do [notebook de qualidade](../notebooks/01_qualidade_e_tratamento.ipynb), seis das dez variáveis discretas não se afastam de frequências iguais, idade e tempo de relacionamento têm distribuição plana, e relações que o negócio espera não aparecem: o valor do pedido não acompanha itens, desconto, frete ou parcelas, e o atraso não traz mais tentativas de entrega nem mais contatos com o atendimento.
- **Decisão:** a base é tratada como simulada. As conclusões do projeto valem como demonstração de método, e não como retrato de uma operação real.
- **Alternativas consideradas:** tratar a base como registro real; mencionar o alcance apenas nas limitações do README.
- **Justificativa:** recomendações apresentadas como fatos de uma operação que a base não representa levariam a decisões sem sustentação. Declarar o alcance preserva o que o trabalho tem de valor: o diagnóstico, as hipóteses, o modelo e a forma de avaliá-lo.
- **Consequências:** o README e a apresentação declaram o alcance. A análise exploratória descreve padrões desta base sem estendê-los ao e-commerce, e as recomendações saem como hipóteses a validar com dados reais. Relações ausentes, como as do valor do pedido, não são lidas como falta de efeito na operação real.

## D-11: Teste separado antes da análise exploratória

- **Status:** aceita em 29/10/2026
- **Contexto:** a análise exploratória escolhe faixas, cortes e regras simples, e a D-03 compara o modelo com a melhor dessas regras. Escolhidos com a base inteira, cortes e regras carregariam informação dos pedidos que depois medem o desempenho final, e a comparação ficaria otimista.
- **Decisão:** 20% dos pedidos formam o conjunto de teste, sorteados com semente fixa e estratificados pela variável-alvo por `src/split.py`, antes da análise exploratória. A análise e as escolhas que saem dela usam só o treino; o teste fica reservado para a avaliação final do modelo e das regras simples.
- **Alternativas consideradas:** explorar a base inteira e separar o teste só na modelagem; separar treino e teste por cliente.
- **Justificativa:** uma regra ajustada aos pedidos de teste parece melhor do que é, e o modelo passaria a ser comparado com uma referência inflada. A separação por cliente não muda nada nesta base, em que cada cliente tem um único pedido (seção 2.1 do [notebook de qualidade](../notebooks/01_qualidade_e_tratamento.ipynb)). A estratificação mantém a mesma proporção de detratores nos dois conjuntos.
- **Consequências:** os números da análise exploratória descrevem o treino, com 80% dos pedidos. A modelagem usa a mesma separação, pela mesma função, e a validação cruzada roda só no treino. Com 2.500 pedidos, o teste tem 500, o que limita a precisão das métricas finais: cada uma sai com intervalo de confiança.
