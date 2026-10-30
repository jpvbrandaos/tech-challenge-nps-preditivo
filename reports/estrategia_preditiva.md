# Estratégia preditiva

## Resumo

O modelo estima, logo após a entrega, a probabilidade de cada cliente responder à pesquisa de NPS como detrator, e a empresa usa essa probabilidade para decidir em quem agir antes da pesquisa. A abordagem é a classificação binária, e não a regressão da nota, porque a meta de negócio é a proporção de detratores e a decisão da operação é agir ou não sobre um cliente. A análise exploratória delimita onde o modelo pode ajudar. Com três dias de atraso ou mais, mais de nove em cada dez clientes já são detratores, e a regra de dias de atraso basta para apontá-los. Nos demais pedidos, seis em cada dez, a proporção de detratores vai de cerca de um em cada cinco a quase nove em cada dez conforme o atraso e o atendimento, e é ali que o modelo precisa superar a regra. O efeito das ações não aparece nos dados históricos e só se mede num piloto com grupo de controle.

## 1. A pergunta que o modelo responde

> Logo após a entrega, com o que já se sabe do pedido, da entrega e do atendimento, qual é a chance de este cliente responder à pesquisa como detrator?

A resposta é uma probabilidade por cliente, calculada uma vez por dia para os pedidos entregues e antes do envio da pesquisa. Três perguntas ficam fora do alcance do modelo:

- **Se agir reduz o risco.** O modelo aprende associações. O efeito de uma ação só se mede comparando clientes que a receberam com clientes sorteados para não receber ([seção 7](#7-como-medir-o-resultado)).
- **Por que o cliente deu a nota.** A base não traz o comentário da pesquisa, o produto nem a categoria ([seção 1 do entendimento do negócio](entendimento_negocio.md#1-o-problema-de-negócio)).
- **O risco de quem não responde à pesquisa.** A base só tem quem respondeu (premissa P4 do [entendimento do negócio](entendimento_negocio.md#7-premissas-restrições-e-riscos)).

## 2. Momento da predição

O score é calculado logo após a entrega ([D-04](registro_decisoes.md#d-04-score-de-risco-calculado-após-a-entrega)). Nesse momento, atraso, tentativas de entrega e contatos com o atendimento já aconteceram, e ainda há tempo para agir antes da pesquisa. Antes da entrega, o score ignoraria as falhas que mais pesam; depois da pesquisa, a nota já estaria dada.

Um segundo cenário, no checkout, usa só cadastro e pedido e serve de comparação. Na análise exploratória, nenhuma variável de cadastro ou de pedido mostrou associação com os detratores depois da correção de Holm (seção 4 da [análise exploratória](../notebooks/02_eda.ipynb)), e a expectativa é de um score de checkout perto do modelo ingênuo. A distância entre os dois cenários mede quanto valem os dados de entrega e de atendimento.

## 3. Regressão ou classificação

| Abordagem | O que entrega | A favor | Contra |
| --- | --- | --- | --- |
| Regressão da nota, de 0 a 10 | Nota esperada de cada cliente | Usa toda a escala | Trata como contínua uma escala ordinal ([D-02](registro_decisoes.md#d-02-proporção-de-detratores-como-indicador-alvo)); o erro, em pontos de nota, não diz quem cruza o corte de 7, que define o detrator |
| Classificação binária | Probabilidade de detrator | Corresponde à meta, a proporção de detratores, e à decisão de agir ou não; a probabilidade ordena a lista do dia | Não separa neutro de promotor, diferença que não muda a meta |
| Classificação em três classes | Probabilidades de detrator, neutro e promotor | Reproduz a fórmula do NPS | Os promotores são 90 pedidos no treino e cerca de 20 no teste (seção 2 da análise exploratória), pouco para treinar e avaliar a classe |

A escolha é a classificação binária, com `is_detractor` como alvo ([D-13](registro_decisoes.md#d-13-variável-alvo-mantida-como-detrator-contra-os-demais)). Do lado técnico, ela aplica o corte de 7 sem arredondamento ([D-05](registro_decisoes.md#d-05-corte-direto-nas-faixas-do-nps-para-notas-com-casa-decimal)), não depende de tratar a nota como número contínuo e produz uma probabilidade que ordena os clientes e pode ser calibrada. Do lado do negócio, mede o que a meta mede e alimenta uma decisão binária: o cliente entra ou não na lista do dia.

Dois pontos completam a escolha. O detrator é a classe majoritária, com 84,4% dos pedidos de treino (seção 1), e por isso a métrica principal é a ROC-AUC, que não depende dessa proporção ([D-12](registro_decisoes.md#d-12-métricas-do-modelo-revistas-para-a-proporção-de-detratores)). E a regressão não fica descartada só por argumento: na Etapa 6 ela entra como comparação, ordenando os clientes pela nota prevista, e é medida pela mesma ROC-AUC ([D-17](registro_decisoes.md#d-17-classificação-binária-com-a-regressão-da-nota-como-comparação)).

## 4. Variáveis de entrada

Entram as variáveis que existem logo após a entrega ([D-06](registro_decisoes.md#d-06-variáveis-permitidas-no-modelo-de-risco)). A análise exploratória já indica onde está o sinal:

| Momento | Variáveis | O que a análise exploratória mostrou |
| --- | --- | --- |
| Cadastro | Idade, região, tempo de relacionamento | Sem associação depois da correção (seções 4 e 8). Região e idade servem também para conferir o erro do modelo por grupo, e nunca para tratar clientes de forma diferente |
| Pedido | Valor, itens, desconto, parcelas, frete | Sem associação depois da correção (seção 4) |
| Entrega | Previsão, dias de atraso, tentativas | O atraso é o fator de maior peso sob controle da operação, e o risco cresce a cada dia, sem ponto de ruptura (seções 4 a 6); as tentativas não mostram associação |
| Atendimento | Contatos, reclamações, tempo de resolução | Associados aos detratores, com as reclamações à frente do ranking (seção 4); o contato pesa mesmo com a entrega no prazo (seção 5) |

Ficam fora a nota, que é o alvo; o CSAT, que acompanha a nota de forma moderada e tem momento de coleta desconhecido; a recompra, que separa as categorias por completo e só existe depois da pesquisa (seção 2); e os identificadores. As variáveis sem associação entram mesmo assim, e a validação cruzada da Etapa 6 mostra se elas acrescentam algo em combinação com as outras.

## 5. Como o modelo será avaliado

- **Separação.** O teste, com 20% dos pedidos, foi reservado antes da análise exploratória e só é usado uma vez, no fim ([D-11](registro_decisoes.md#d-11-teste-separado-antes-da-análise-exploratória)). A comparação entre modelos usa validação cruzada estratificada de 5 partes no treino.
- **Métricas.** ROC-AUC como métrica principal e PR-AUC como apoio ([D-12](registro_decisoes.md#d-12-métricas-do-modelo-revistas-para-a-proporção-de-detratores)).
- **Referências.** O modelo ingênuo e a regra de dias de atraso ([D-14](registro_decisoes.md#d-14-dias-de-atraso-como-regra-de-referência)), com ROC-AUC de 0,500 e 0,803 no treino (seção 11).
- **Critério de sucesso.** No teste, ROC-AUC pelo menos 0,05 acima da regra, com o intervalo de confiança da diferença acima de zero, e PR-AUC não menor que a dela ([D-15](registro_decisoes.md#d-15-alvos-do-modelo-e-da-meta-de-negócio)).

O plano da Etapa 6 fica fixado antes do treino ([D-18](registro_decisoes.md#d-18-plano-de-modelagem-fixado-antes-do-treino)):

| Item | Plano |
| --- | --- |
| Candidatos | Regressão logística, legível e com probabilidades em geral bem calibradas, e gradient boosting de árvores, do scikit-learn, que capta cortes e interações |
| Ajuste | Busca aleatória pequena de hiperparâmetros, dentro da validação cruzada do treino |
| Escolha | Maior ROC-AUC na validação cruzada; entre modelos a até 0,01 do melhor, o mais simples |
| Classes | Sem reamostragem nem pesos: a ROC-AUC não depende do equilíbrio entre as classes, e as probabilidades precisam continuar fiéis para a lista e para a estimativa de impacto |
| Comparação | Regressão da nota, ordenando os clientes pela nota prevista ([D-17](registro_decisoes.md#d-17-classificação-binária-com-a-regressão-da-nota-como-comparação)) |
| Robustez | Sem `complaints_count` ([D-16](registro_decisoes.md#d-16-modelagem-mantida-com-ganho-exigido-sobre-a-regra)); sem `resolution_time_days` ([D-06](registro_decisoes.md#d-06-variáveis-permitidas-no-modelo-de-risco)); cenário de checkout; treino com o CSAT, para mostrar o desempenho artificial do vazamento; calibração; erro por região e faixa de idade |
| Leitura por segmento | ROC-AUC do modelo e da regra nos pedidos com até 2 dias de atraso, onde o ganho precisa aparecer ([D-19](registro_decisoes.md#d-19-uso-do-score-por-segmento-de-atraso-com-a-ação-definida-pela-falha-do-pedido)) |

## 6. Como a empresa usaria

O fluxo tem quatro momentos:

1. **Durante a entrega.** O pedido que passa da data prevista aciona um alerta para a transportadora e um aviso ao cliente com a nova previsão. É uma regra, sem modelo: na análise exploratória, o risco sobe a cada dia de atraso, sem um limite tolerado (seção 6).
2. **Logo após a entrega.** O score é calculado uma vez por dia para os pedidos entregues na véspera.
3. **Lista do dia.** Os pedidos se dividem em dois segmentos, e a capacidade de contato do atendimento se divide entre eles.
4. **Ação.** Cada cliente da lista recebe a ação ligada à falha registrada no pedido.

| Segmento | Peso no treino | Proporção de detratores | Como se ordena |
| --- | --- | --- | --- |
| Atraso de 3 dias ou mais | Quase quatro em cada dez pedidos | Mais de nove em cada dez, em qualquer combinação (seção 7) | Dias de atraso, pela regra; o modelo não tem o que acrescentar |
| Atraso de até 2 dias | Seis em cada dez pedidos | De cerca de um em cada cinco, no prazo e sem contato, a quase nove em cada dez com contato (seção 7) | Risco do modelo |

A lista não usa limiar de probabilidade: com 84,4% de detratores, um corte usual marcaria a maioria dos clientes, e a lista é cortada pela capacidade do dia. A capacidade, estimada em 20% dos pedidos e ainda a validar com o atendimento ([seção 2 do entendimento do negócio](entendimento_negocio.md#2-metas-e-critérios-de-sucesso)), se divide em partes iguais entre os dois segmentos durante o piloto. A divisão é deliberada: risco alto não garante que a ação funcione, e no segmento de atrasos longos o cliente pode já estar perdido. O piloto mede em qual segmento a ação reduz mais detratores por contato, e a divisão seguinte acompanha esse resultado ([D-19](registro_decisoes.md#d-19-uso-do-score-por-segmento-de-atraso-com-a-ação-definida-pela-falha-do-pedido)).

| Falha registrada no pedido | Ação | Área |
| --- | --- | --- |
| Atraso | Contato de recuperação que reconhece o atraso e confirma que o pedido chegou completo; a causa vai para a logística da rota | Atendimento e logística |
| Contato com o atendimento ou reclamação | Resolver no mesmo dia a falha que originou o contato | Atendimento |
| Resolução acima de 7 dias | Fechar o chamado em aberto e confirmar a solução com o cliente | Atendimento |

Quando o pedido tem mais de uma falha, vale a primeira da tabela, que segue a ordem de impacto da seção 5. A ação depende da falha registrada, e não de uma explicação do modelo: a regra é auditável e não muda quando o modelo é retreinado.

A análise exploratória também tirou ações da lista:

- **Cupom genérico como compensação.** Nos pedidos com falha, quem teve o maior desconto na compra foi detrator tanto quanto quem teve o menor (H6). O teste mediu o desconto dado na compra, e não um cupom de recuperação, que só o piloto pode avaliar.
- **Prioridade para clientes novos.** O atraso não pesa mais nos clientes novos que nos antigos (H4).
- **Devolução do frete no atraso.** O efeito do atraso não é maior com frete caro (H5).
- **Ação só na segunda falha.** As falhas se somam sem efeito extra (H8).
- **Ação por perfil de cliente.** Região, idade e tempo de relacionamento não mudam o risco (seção 8), e a LGPD veda o uso desses dados para fins discriminatórios ([seção 7 do entendimento do negócio](entendimento_negocio.md#7-premissas-restrições-e-riscos)).

## 7. Como medir o resultado

O piloto compara o processo da seção 6 com o processo atual ([D-20](registro_decisoes.md#d-20-piloto-com-grupo-de-controle-para-medir-o-efeito-das-ações)):

- **Desenho.** Os clientes são sorteados em dois grupos do mesmo tamanho: um segue o processo novo, com o alerta de atraso, o score e as ações; o outro segue o processo atual. O sorteio garante que a diferença entre os grupos venha do processo, e não da época ou do perfil dos clientes.
- **Duração e tamanho.** Dois trimestres, com pelo menos 254 clientes que responderam à pesquisa em cada grupo. É o mínimo para detectar a queda de 84,4% para 74,4% com 5% de significância e 80% de poder. Como só tem nota quem responde, o número de clientes sorteados é esse mínimo dividido pela taxa de resposta.
- **Resultado principal.** A diferença na proporção de detratores entre os grupos, com intervalo de confiança. O piloto atinge a meta se a queda estimada for de 10 pontos ou mais, com o intervalo acima de zero ([D-15](registro_decisoes.md#d-15-alvos-do-modelo-e-da-meta-de-negócio)).
- **Métricas de proteção.** Taxa de resposta da pesquisa, custo de atendimento e de compensação por pedido, prazo prometido e conversão, medidos nos dois grupos ([seção 2 do entendimento do negócio](entendimento_negocio.md#2-metas-e-critérios-de-sucesso)).
- **Leituras secundárias.** O efeito em cada segmento e em cada tipo de falha orienta a divisão da capacidade (seção 6). Com o tamanho mínimo, essas leituras indicam caminhos, mas não decidem sozinhas.
- **Depois do piloto.** Uma parcela fixa de 10% dos clientes, sorteada, segue sem ação. Ela mantém a medida do efeito ao longo do tempo e fornece dados para retreinar o modelo sem a influência das ações: a ação muda a nota de quem a recebe, e um modelo retreinado só com clientes tratados aprenderia o efeito da ação junto com o risco.

Cálculo do tamanho mínimo, com o statsmodels do projeto:

```python
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

# Queda de 84,4% para 74,4% de detratores, com 5% de significância e 80% de poder
effect = proportion_effectsize(0.844, 0.744)
NormalIndPower().solve_power(effect_size=effect, alpha=0.05, power=0.8)  # 253,3 por grupo
```

## 8. Riscos e limites

| Risco | Como aparece | Como a estratégia trata |
| --- | --- | --- |
| Base simulada | Desempenho que não se repete em dados reais | Os números do modelo valem como demonstração de método ([D-10](registro_decisoes.md#d-10-base-tratada-como-simulada)); o piloto é a validação real |
| Sem data do pedido | Não há como treinar no passado e testar no futuro | Em produção, comparar todo mês o risco previsto com as notas que chegam e retreinar quando a ROC-AUC do modelo cair abaixo da regra de atraso no mesmo mês |
| Ciclo de realimentação | As ações mudam as notas que o modelo usa para aprender | Controle permanente de 10% dos clientes ([seção 7](#7-como-medir-o-resultado)) |
| Reclamação como sintoma | O modelo depende de um sinal muito próximo da própria nota | Medida sem `complaints_count` na Etapa 6 ([D-16](registro_decisoes.md#d-16-modelagem-mantida-com-ganho-exigido-sobre-a-regra)) |
| Valores finais de atendimento | A base histórica traz o tempo de resolução final, e a avaliação fica otimista | Medida sem `resolution_time_days` ([D-06](registro_decisoes.md#d-06-variáveis-permitidas-no-modelo-de-risco)) |
| Uso discriminatório | Clientes tratados de forma desigual por idade ou região | A ação segue a falha do pedido, e o erro do modelo é conferido por grupo |
| Não resposta | A proporção de detratores melhora porque menos insatisfeitos respondem | Taxa de resposta como métrica de proteção |
