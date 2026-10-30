# Model card: risco de detrator

Ficha do modelo de risco de detrator: o que ele estima, para que serve, como foi avaliado, onde erra e como não deve ser usado. Os números vêm do [notebook de modelagem](../notebooks/03_modelagem.ipynb), e as decisões citadas estão no [registro de decisões](registro_decisoes.md).

## Resumo

Regressão logística que estima, logo após a entrega, a probabilidade de o cliente responder à pesquisa de NPS como detrator. Na operação, ela ordena, para a lista diária de contato, os pedidos com até 2 dias de atraso, em que a regra de dias de atraso só separa zero, um e dois dias. No teste, com 500 pedidos que não participaram de nenhuma escolha, a ROC-AUC foi de 0,869, contra 0,784 da regra, e o modelo atendeu aos três critérios da [D-15](registro_decisoes.md#d-15-alvos-do-modelo-e-da-meta-de-negócio); nos pedidos com até 2 dias de atraso, a diferença para a regra sobe de 0,085, em todos os pedidos, para 0,120. A base é simulada, e os números valem como demonstração de método; se a lista reduz os detratores, só o piloto com grupo de controle vai mostrar.

## 1. Uso pretendido

- **O que estima.** A probabilidade de o cliente responder à pesquisa de NPS como detrator, com nota abaixo de 7 ([D-05](registro_decisoes.md#d-05-corte-direto-nas-faixas-do-nps-para-notas-com-casa-decimal) e [D-13](registro_decisoes.md#d-13-variável-alvo-mantida-como-detrator-contra-os-demais)), calculada logo após a entrega ([D-04](registro_decisoes.md#d-04-score-de-risco-calculado-após-a-entrega)).
- **Para que serve.** Ordenar, uma vez por dia, os pedidos com até 2 dias de atraso para a lista de contato do atendimento. Os pedidos com 3 dias de atraso ou mais seguem a regra de dias de atraso, e a capacidade do dia se divide entre os dois segmentos ([D-19](registro_decisoes.md#d-19-uso-do-score-por-segmento-de-atraso-com-a-ação-definida-pela-falha-do-pedido)).
- **Quem usa.** Atendimento e logística, pela lista do dia que o comando `python -m src.modeling.predict` gera a partir dos pedidos entregues.
- **Fora do uso.** Escolher a ação, que segue a falha registrada no pedido; tratar clientes de forma diferente por região, idade ou tempo de relacionamento; medir o efeito de uma ação, o que só o piloto com grupo de controle faz ([D-20](registro_decisoes.md#d-20-piloto-com-grupo-de-controle-para-medir-o-efeito-das-ações)).

## 2. Dados

- **Base.** 2.500 pedidos, um por cliente, numa base tratada como simulada ([D-10](registro_decisoes.md#d-10-base-tratada-como-simulada)): os números valem como demonstração de método.
- **Separação.** 2.000 pedidos de treino e 500 de teste, sorteados com semente fixa e estratificados pela variável-alvo antes da análise exploratória ([D-11](registro_decisoes.md#d-11-teste-separado-antes-da-análise-exploratória)).
- **Variáveis.** As 14 colunas de cadastro, pedido, entrega e atendimento que existem logo após a entrega ([D-06](registro_decisoes.md#d-06-variáveis-permitidas-no-modelo-de-risco)). Ficam fora a nota, que define o alvo, o CSAT, a recompra e os identificadores.

## 3. Modelo

- **Algoritmo e hiperparâmetros.** Regressão logística com regularização L2, C de 0,1445 e até 1.000 iterações, no scikit-learn 1.9.1. O C saiu de 20 valores sorteados entre 0,001 e 100, em escala logarítmica, e ficou longe dos limites da faixa.
- **Preparação.** Padronização das variáveis numéricas e uma coluna por região, dentro do pipeline: em cada ajuste, a preparação aprende só com os pedidos daquele ajuste.
- **Escolha.** Regressão logística e gradient boosting, com 20 combinações de hiperparâmetros cada, comparados por validação cruzada estratificada de 5 partes no treino. Vence o de maior ROC-AUC ou, a até 0,01 dele, o mais simples, sem reamostragem nem pesos de classe ([D-18](registro_decisoes.md#d-18-plano-de-modelagem-fixado-antes-do-treino)).
- **Versão.** O comando `python -m src.modeling.train` grava o modelo em `models/modelo_detrator.joblib` e, ao lado, um JSON com o modelo escolhido, os hiperparâmetros, as variáveis, a ROC-AUC na validação cruzada, o SHA-256 da base e a versão do scikit-learn.

## 4. Avaliação

O teste, com 500 pedidos separados antes da análise exploratória, foi usado uma única vez, depois da revisão da seção 9 do notebook ([D-11](registro_decisoes.md#d-11-teste-separado-antes-da-análise-exploratória)). O modelo supera a regra de dias de atraso pelos três critérios da [D-15](registro_decisoes.md#d-15-alvos-do-modelo-e-da-meta-de-negócio): ROC-AUC 0,085 acima da dela, com intervalo bootstrap de 95% de 0,044 a 0,129, e PR-AUC também acima. Com 500 pedidos, o intervalo não descarta um ganho real um pouco menor que a margem de 0,05. Nos 301 pedidos de teste com até 2 dias de atraso, a diferença sobe para 0,120, com intervalo de 0,056 a 0,183. No topo de 20%, modelo e regra só reúnem detratores, e precisão e captura não separam os dois ([D-12](registro_decisoes.md#d-12-métricas-do-modelo-revistas-para-a-proporção-de-detratores)).

Na primeira linha da tabela, o modelo é medido pelas previsões fora da amostra da validação cruzada, e as referências, que não têm nada a ajustar, no treino inteiro.

| Medida | Modelo | Regra de dias de atraso | Modelo ingênuo |
| --- | --- | --- | --- |
| ROC-AUC na validação cruzada do treino | 0,896 | 0,803 | 0,500 |
| ROC-AUC no teste | 0,869 | 0,784 | 0,500 |
| PR-AUC no teste | 0,974 | 0,939 | 0,844 |
| ROC-AUC no teste, pedidos com até 2 dias de atraso | 0,793 | 0,673 | 0,500 |

## 5. Robustez

Na validação cruzada, sem `complaints_count`, a ROC-AUC cai 0,022, com intervalo de 0,012 a 0,031, e a vantagem sobre a regra passa de 0,093 para 0,071; sem `resolution_time_days`, cai 0,017, e a vantagem fica em 0,076. O ganho não depende de uma variável só, e a ressalva da [D-16](registro_decisoes.md#d-16-modelagem-mantida-com-ganho-exigido-sobre-a-regra) não se aplica. Só com cadastro e pedido, o cenário de um score no checkout, a ROC-AUC fica em 0,527, perto do modelo ingênuo: quase todo o sinal está na entrega e no atendimento. Treinado também com o CSAT, que a [D-06](registro_decisoes.md#d-06-variáveis-permitidas-no-modelo-de-risco) deixa de fora, o modelo fica em 0,895, sem ganho: nesta base, o CSAT não acrescenta informação às outras variáveis. Pela importância por permutação, o modelo se apoia nos dias de atraso e nas reclamações e, bem atrás, no tempo de resolução; idade, região e tempo de relacionamento quase não mudam a ordenação.

## 6. Calibração e erro por grupo

Calibração e erro por grupo são medidos nas previsões fora da amostra da validação cruzada. Em nove das dez faixas de risco, com 200 pedidos cada, a probabilidade prevista cai dentro do intervalo de Wilson de 95% da proporção observada; a exceção é a segunda faixa de menor risco, com 62,8% previstos e 55,0% observados. O escore de Brier é de 0,087, contra 0,132 do modelo ingênuo, e a probabilidade serve para estimar quantos detratores a lista alcança, sem recalibração. Por grupo, o risco previsto fica a menos de meio ponto da proporção observada em todas as regiões; na idade, a maior diferença é de quatro pontos, com o risco subestimado na faixa de 35 a 44 anos, perto do que grupos de algumas centenas de pedidos explicam. A ROC-AUC vai de 0,872 a 0,935 entre regiões e faixas de idade, e o modelo praticamente não usa idade nem região.

## 7. Limitações e riscos

- **Base simulada.** O desempenho medido aqui não se transfere para uma operação real; o piloto é a validação real ([D-10](registro_decisoes.md#d-10-base-tratada-como-simulada) e [D-20](registro_decisoes.md#d-20-piloto-com-grupo-de-controle-para-medir-o-efeito-das-ações)).
- **Valores finais de atendimento.** A base traz o tempo de resolução e as reclamações registrados até o fim, e não no momento da predição, o que deixa a avaliação otimista; a seção 5 mede o modelo sem cada um deles.
- **Reclamação como sintoma.** A reclamação expressa a insatisfação em vez de originá-la, e o modelo que depende dela antecipa a nota mais do que explica a falha ([D-16](registro_decisoes.md#d-16-modelagem-mantida-com-ganho-exigido-sobre-a-regra)).
- **Sem data do pedido.** Não há como treinar no passado e testar no futuro; a estabilidade no tempo só aparece em produção.
- **Ciclo de realimentação.** As ações mudam as notas de quem as recebe, e um retreino com esses clientes aprenderia o efeito da ação junto com o risco.

## 8. Monitoramento e retreino

- Todo mês, comparar o risco previsto com as notas que chegam e medir a ROC-AUC do modelo e da regra de dias de atraso nos mesmos pedidos; retreinar quando o modelo deixar de superar a regra ([seção 8 da estratégia preditiva](estrategia_preditiva.md#8-riscos-e-limites)).
- Retreinar com os clientes do grupo de controle permanente, que não recebem ação ([D-20](registro_decisoes.md#d-20-piloto-com-grupo-de-controle-para-medir-o-efeito-das-ações)).
- A cada retreino, refazer a calibração e o erro por região e faixa de idade, e registrar a versão no JSON ao lado do modelo.
