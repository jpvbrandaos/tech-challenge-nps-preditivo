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
