# Entendimento do negócio — NPS Preditivo

## Resumo

A empresa só mede a satisfação depois do fim da jornada de compra, quando a falha já aconteceu e o cliente já formou opinião sobre a loja. O projeto ataca o problema em duas frentes. A primeira identifica as falhas de entrega e atendimento que mais geram detratores. A segunda estima, logo após a entrega, o risco de cada cliente se tornar detrator, a tempo de agir. O foco é o detrator: recuperar um pesa no NPS tanto quanto conquistar um promotor, e é nele que se espera achar uma falha que a operação consegue corrigir. O sucesso se mede pela queda da proporção de detratores num piloto com grupo de controle, sem aumento do custo de atendimento e sem queda na taxa de resposta da pesquisa.

Marcações como `[linha de base: Etapa 4]` indicam números que dependem da análise dos dados e serão preenchidos na etapa indicada.

## 1. O problema de negócio

A empresa cresceu em pedidos, entregas e contatos com clientes, e o NPS passou a variar muito entre perfis de consumidores. Clientes com indicadores operacionais parecidos terminam ora promotores, ora detratores. A empresa só descobre o resultado quando a pesquisa é respondida, depois do encerramento da jornada, e aí a experiência daquele pedido já não tem conserto. A área de Experiência do Cliente não consegue agir antes de o cliente virar detrator porque só mede a satisfação no fim da jornada. Com isso, corrige falhas quando o cliente já decidiu se volta e o que vai dizer da loja. A decisão em aberto é em quais falhas agir primeiro, e em quais pedidos, para reduzir detratores antes da pesquisa.

São dois problemas encadeados. O diagnóstico pergunta quais fatores operacionais separam promotores de detratores; a antecipação pede estimar o risco de detrator antes da pesquisa. O segundo depende do primeiro. Um score de risco sem diagnóstico gera uma lista de clientes sem dizer o que fazer com cada um, e é o diagnóstico que mostra quais informações existem antes da pesquisa e podem entrar no modelo sem vazamento de dados.

| Dentro do escopo | Fora do escopo |
| --- | --- |
| Fatores de pedido, entrega e atendimento presentes na base | Produto e categoria, que a base não traz |
| Perfil do cliente: idade, região e tempo de relacionamento | Canal de venda, transportadora e forma de pagamento; a base traz só o número de parcelas |
| Associação entre falhas e detratores | Prova de causa, que exige piloto com grupo de controle |
| Score de risco calculado logo após a entrega | Tendência e sazonalidade, porque a base não tem data do pedido |
| Recomendações por área, apoiadas nos achados | Motivo declarado da nota, porque a base não traz o comentário da pesquisa |
| Desenho do uso do score e de um piloto | Implantação do modelo em produção |

## 2. Metas e critérios de sucesso

**Meta de negócio.** Reduzir a proporção de detratores de `[linha de base: Etapa 4]` para `[alvo: Etapa 4]` em dois trimestres a partir do início do piloto, sem piorar as métricas de proteção. O NPS geral é acompanhado junto, mas a meta é a proporção de detratores, que as ações propostas movem diretamente.

**Meta analítica.** Entregar o diagnóstico das falhas operacionais associadas aos detratores, com peso e frequência de cada uma. E entregar um score de risco de detrator, calculado logo após a entrega, que supere o modelo ingênuo e a melhor regra simples da análise exploratória.

**Critérios de sucesso**, definidos antes da análise dos dados para que a régua não se ajuste ao resultado:

| Tipo | Critério | Como se mede | Quando |
| --- | --- | --- | --- |
| Analítico | A análise exploratória responde às quatro perguntas da Parte 3 | Cada resposta com o número e o tamanho do grupo que a sustentam | Análise exploratória (Etapa 4) |
| Analítico | Cada hipótese da seção 8 recebe um veredito | Confirmada, refutada ou inconclusiva, com o número que decide | Análise exploratória (Etapa 4) |
| Modelo | O score supera o modelo ingênuo e a melhor regra simples | PR-AUC e % dos detratores que caem entre os 20% de maior risco, no mesmo conjunto de teste | Modelo (Etapa 6) |
| Negócio | Agir nos clientes de risco reduz a proporção de detratores | Comparação com um grupo de controle sorteado | Piloto, depois do projeto |

Os alvos numéricos dependem da proporção de detratores na base, que define o desempenho do modelo ingênuo. Por isso, são fixados ao fim da análise exploratória, antes do treino de qualquer modelo. O corte de 20% supõe a capacidade de contato do atendimento e precisa ser validado com a área.

**Métricas de proteção**, que não podem piorar enquanto a meta melhora:

- **Taxa de resposta da pesquisa.** Se cair, o NPS pode subir só porque quem daria nota baixa deixou de responder.
- **Custo de atendimento e de compensação por pedido.** Contato proativo e cupom custam dinheiro, e a melhora precisa caber na margem.
- **Prazo prometido no checkout e taxa de conversão.** Alongar a promessa de entrega reduz o atraso no papel e afasta o cliente antes da compra.

A meta analítica indica onde e com quem agir. A meta de negócio mede se a ação funcionou, e as métricas de proteção confirmam que a melhora veio da experiência do cliente, não de um atalho.

## 3. Por que o NPS importa para um e-commerce

O NPS nasce de uma pergunta: de 0 a 10, qual a probabilidade de o cliente recomendar a empresa a um amigo ou colega (Reichheld, 2003). Notas 9 e 10 são promotores; 7 e 8, neutros; 0 a 6, detratores. O NPS é o percentual de promotores menos o de detratores, de −100 a +100; os neutros contam no total, mas não entram na subtração. Como a base registra notas com uma casa decimal, a regra para classificar uma nota como 6,9 fica para a definição da target (Etapa 2).

A conta explica o foco no detrator. Em 200 respostas com 90 promotores, 60 neutros e 50 detratores, o NPS é +20. Se 10 detratores passarem a neutros, ele vai a +25, o mesmo efeito de 10 neutros virarem promotores. E é no detrator que se espera achar a falha concreta, como atraso ou atendimento lento, que a operação sabe corrigir.

No e-commerce, a métrica pesa mais. O concorrente está a uma busca de distância, então a fidelidade depende mais da última experiência do que no varejo físico, onde localização e hábito também seguram o cliente. A opinião fica pública em avaliações, redes sociais e sites de reclamação, lidos por quem ainda vai comprar. E a falha que mais gera reclamação no setor é uma das que a base mede. No consumidor.gov.br, não entrega ou demora na entrega liderou os problemas apontados no comércio eletrônico em 2025, com 23,09% (Senacon, 2025). O NPS ainda chega antes da receita: a nota sai dias depois da entrega, enquanto a perda só aparece na próxima compra que não acontece.

O NPS da base é transacional. O dicionário descreve a nota como "coletada após a experiência de compra", uma por pedido. Ela avalia aquele pedido, não o relacionamento com a marca, que é o objeto do NPS relacional. Isso favorece o projeto, porque a nota reage às falhas da operação, e exige cuidado na comparação com benchmarks, muitos deles relacionais (seção 6).

A métrica tem limites. Reichheld (2003) apresenta a pergunta de recomendação como melhor preditora de lealdade e crescimento do que as pesquisas tradicionais de satisfação. Keiningham et al. (2007) testaram essa afirmação com dados de 21 empresas e mais de 15.500 entrevistas do *Norwegian Customer Satisfaction Barometer*. Nos setores que o próprio Reichheld cita como exemplo, não conseguiram replicar a superioridade do NPS. O projeto trata o NPS como o indicador de gestão que a empresa escolheu, não como garantia de crescimento. Na prática, o NPS diz quanto, mas não diz por quê, o que obriga a cruzar a nota com os dados da operação. E o mesmo NPS esconde distribuições diferentes: NPS 0 pode ser 100% de neutros ou metade de promotores e metade de detratores. Por isso a proporção de detratores é acompanhada ao lado dele.

## 4. Áreas que se beneficiam e decisões apoiadas

A tabela liga cada área à decisão que a análise apoia, às variáveis que a sustentam e ao formato em que o resultado chega a quem decide.

| Área | Decisão que o insight apoia | Variáveis da base | Ação possível | Como recebe |
| --- | --- | --- | --- | --- |
| Logística | Quanto atraso o cliente tolera e onde o prazo prometido está irreal | `delivery_time_days`, `delivery_delay_days`, `delivery_attempts`, `customer_region` | Rever o SLA com as transportadoras da região que mais atrasa e recalibrar o prazo exibido no checkout | Painel mensal por região |
| Atendimento | Que prazo de resolução adotar e que casos tratar primeiro | `customer_service_contacts`, `resolution_time_days`, `complaints_count` | Fila prioritária para pedidos atrasados com contato aberto | Lista diária de pedidos em risco |
| Pricing e comercial | Política de frete e uso de desconto como compensação | `freight_value`, `discount_value`, `order_value`, `payment_installments` | Devolver o frete de pedidos atrasados em vez de oferecer cupom genérico | Revisão trimestral da política comercial |
| Marketing e CRM | Quem convidar a indicar a loja e quem incluir em recuperação | `nps_score`, `customer_tenure_months`, `repeat_purchase_30d` | Programa de indicação para promotores, oferecido logo após a pesquisa | Segmentos atualizados semanalmente no CRM |
| Produto | Se vale registrar produto e categoria junto com a nota | Nenhuma variável direta | Incluir categoria, SKU e motivo da nota na pesquisa | Relatório trimestral |
| Estratégia (liderança de CX) | Em que área investir primeiro | Todas, pela matriz de impacto × frequência | Ordenar o roadmap por detratores evitáveis e custo de cada ação | Resumo trimestral |

Produto aparece no enunciado, mas não na base. A análise só pode tratá-lo de forma indireta. Detratores sem nenhuma falha de entrega ou atendimento (H9) apontam para causas fora da operação medida, como o próprio produto ou a expectativa criada na venda. No consumidor.gov.br, produto danificado ou que não funciona somou 7,77% dos problemas apontados no comércio eletrônico em 2025 (Senacon, 2025). Isso justifica passar a registrar produto e categoria junto com a nota.

A prioridade entre as áreas cabe à liderança de Experiência do Cliente, com dois números por ação: quantos detratores ela pode evitar e quanto custa.

## 5. Como o NPS impacta recompra, boca a boca e market share

O enunciado pede uma reflexão e dispensa dados externos. O raciocínio segue esta cadeia:

**experiência operacional → NPS → recompra e boca a boca → receita e custo de aquisição → market share**

Cada elo é uma associação esperada, não uma causa comprovada. A base permite medir o primeiro elo e parte do segundo.

**Recompra.** O promotor tende a voltar porque a última compra reduziu o risco da próxima: ele sabe que a entrega chega e que, se algo der errado, o problema se resolve. O detrator tende a testar outra loja, e no e-commerce isso custa uma busca. Cada cliente perdido precisa ser reposto com investimento em aquisição, e a perda aparece duas vezes: na receita que não volta e no custo de conquistar o substituto.

**Boca a boca.** O promotor indica a loja sem custo para a empresa. O detrator também fala, e a reclamação em avaliações, redes sociais ou no Reclame Aqui continua visível para quem pesquisa a loja muito depois do pedido. A experiência ruim tende a circular mais que a boa, porque dá ao cliente um motivo concreto para contar e encontra canais prontos para isso.

**Market share.** Com a troca de loja a um clique, a participação de mercado tende a migrar para quem retém mais clientes e recebe mais indicações. Por isso o que conta é o NPS da empresa em relação ao dos concorrentes que disputam o mesmo cliente, não o número isolado. Reichheld (2003) defende a ligação entre recomendação e crescimento, e Keiningham et al. (2007) não a encontram com a força alegada, o que mantém esse elo como hipótese a acompanhar.

**Evidência na base:** recompra em 30 dias por categoria de NPS, `[resultado: Etapa 4]`.

## 6. Indicadores de mercado complementares

Os indicadores externos posicionam a empresa diante do mercado; os internos completam o NPS dentro de casa. As referências numéricas são ordens de grandeza e valem com a ressalva de método de cada fonte.

**Indicadores externos (mercado)**

| Indicador | O que mede | Por que complementa o NPS | Referência atual | Fonte |
| --- | --- | --- | --- | --- |
| Benchmark de NPS do setor | NPS médio das marcas de um segmento | Diz se o NPS da empresa é alto ou baixo diante dos concorrentes | 64 no segmento E-commerce e Marketplace, em 590 mil avaliações de clientes dos últimos 12 meses. É NPS relacional: não se compara direto com o da base | Meio & Mensagem (2026), dados da Opinion Box |
| Reputação no Reclame Aqui | Índices de resposta e de solução, nota do consumidor e % que voltaria a fazer negócio | Mostra a insatisfação que ficou pública e chega a quem ainda vai comprar | Reputação de 0 a 10, considerada ótima a partir de 8 | Seu Crédito Digital (2026) |
| Reclamações no consumidor.gov.br | Volume, índice de solução e prazo de resposta, por empresa e por segmento | Mede a insatisfação em canal oficial, de forma comparável entre empresas | Índice de solução de 79,76% no comércio eletrônico em 2025, contra 81,43% na plataforma toda | Senacon (2025) |
| SLA logístico do mercado | Prazo e frete médios praticados, por região | O cliente julga o prazo pelo que outras lojas entregam | Na Semana do Consumidor de 2026, prazo médio de 3 dias e frete médio de R$ 34; no Norte, até 11 dias e R$ 66,98. Semana promocional, que não representa o ano | Economic News Brasil (2026), dados da nstech |
| Preço e condições da concorrência | Preço, frete, prazo e parcelamento de concorrentes para itens equivalentes | A satisfação depende da alternativa que o cliente tinha | Sem fonte pública; exige monitoramento de preços próprio ou contratado | Não se aplica |

**Indicadores internos complementares**

| Indicador | O que mede | Por que complementa o NPS |
| --- | --- | --- |
| CSAT | Satisfação com uma interação ou etapa da jornada | Mostra em que ponto da jornada a nota se forma. Na base, `csat_internal_score` serve para validar a target, não para prever (Etapa 2) |
| CES e resolução no primeiro contato | Esforço do cliente para resolver uma demanda e % de casos resolvidos sem novo contato | Explicam detratores que passaram pelo atendimento, em que o peso pode estar no esforço e não no número de contatos (H3) |
| Taxa de resposta da pesquisa | % de clientes convidados que respondem | Mostra se o NPS mudou porque a experiência mudou ou porque mudou quem responde |
| Churn, LTV e CAC | Perda de clientes, valor do cliente ao longo do tempo e custo de conquistar um novo | Traduzem o NPS em dinheiro: quanto vale evitar um detrator |

## 7. Premissas, restrições e riscos

O enunciado e o dicionário de dados deixam pontos em aberto. Cada um vira uma premissa escrita, com o trecho que a sustenta e o momento do teste, conforme a decisão D-02 do [registro de decisões](registro_decisoes.md). A maior parte dos testes acontece na Etapa 3, de qualidade e tratamento dos dados.

**Premissas**

| # | Premissa | O que a sustenta | Como e quando se verifica |
| --- | --- | --- | --- |
| P1 | A nota avalia a experiência daquele pedido, não o relacionamento com a marca | Dicionário: nota "coletada após a experiência de compra", uma por `order_id` | Não se verifica na base; orienta a comparação com benchmarks |
| P2 | As variáveis de entrega e atendimento se referem ao pedido avaliado, não ao histórico do cliente | Estão na linha do pedido, mas o dicionário fala em contatos "do cliente" e reclamações "registradas pelo cliente" | Etapa 3: ver se essas contagens se repetem entre pedidos do mesmo cliente |
| P3 | `delivery_delay_days` conta os dias além do prazo prometido e está contido em `delivery_time_days` | Dicionário: "Quantidade de dias de atraso na entrega" | Etapa 3: atraso nunca maior que o tempo de entrega; checagem de valores negativos |
| P4 | Só tem nota quem respondeu à pesquisa, e as conclusões valem para quem responde | Enunciado: o NPS é coletado "após o encerramento da jornada de compra", sem dizer quem é convidado | Etapa 3: notas ausentes em `nps_score` |
| P5 | A base é tratada como registro real da operação. Com sinais de simulação, as conclusões passam a valer como demonstração de método | O case é acadêmico e não identifica a empresa | Etapa 3: distribuições e relações regulares demais |

As premissas sobre o uso das variáveis no modelo, como o momento de coleta do CSAT e as notas com casa decimal, ficam na definição da target (Etapa 2).

**Restrições**

- **De dados.** Sem data do pedido, não há como analisar tendência e sazonalidade nem validar o modelo no tempo. A base também não traz produto, categoria, canal de venda, transportadora, forma de pagamento (só o número de parcelas), comentário da pesquisa nem dados de quem não respondeu.
- **Legais.** Idade e região, ligadas a `customer_id`, são dados pessoais sob a LGPD (Brasil, 2018). O tratamento deve respeitar finalidade e necessidade e não pode ter fins discriminatórios ilícitos ou abusivos (art. 6º, incisos I, III e IX). Por isso, esses atributos servem ao diagnóstico e à checagem de erros do modelo por grupo, e nenhuma ação dá tratamento pior a um cliente por causa deles.
- **De projeto.** Prazo da fase, trabalho individual sem revisão de pares (compensado por pull requests revisadas e checklists), nenhuma consulta aos professores (D-02) e base fora do Git, obtida por script que confere a integridade do arquivo (D-01).

**Riscos**

| Risco | O que acontece se ocorrer | Como reduzir |
| --- | --- | --- |
| Ler associação como causa | Recomendações que não mudam o NPS | Linguagem de associação nos achados; efeito confirmado só em piloto com grupo de controle |
| Base simulada | Achados que não se repetem em dados reais | Procurar sinais de simulação na Etapa 3 e declarar o alcance das conclusões |
| Sinal fraco para um bom modelo | Modelo que não supera uma regra simples | Critérios fixados antes (seção 2); se a regra vencer, ela vira a recomendação |
| Vazamento de dados | Modelo excelente no teste e inútil na operação | Só variáveis disponíveis antes da pesquisa; CSAT e recompra ficam de fora (Etapa 2) |
| Viés de não resposta | NPS da base diferente do NPS de todos os clientes | Medir notas ausentes e acompanhar a taxa de resposta |
| NPS vira meta de equipe | A nota sobe sem melhora real, por exemplo com pedido explícito de nota 10 | Métricas de proteção; a equipe avaliada não escolhe quem recebe a pesquisa |

## 8. Hipóteses para a análise exploratória

Cada hipótese pode ser confirmada ou derrubada pela base e traz o mecanismo que a justifica e a ação que muda se ela se confirmar. H1 a H7 cobrem entrega, atendimento, preço e perfil; H8 e H9 tentam explicar a frase central do case, a de clientes com indicadores parecidos que terminam em lados opostos. A prioridade é alta quando o impacto esperado é alto e a base permite o teste completo.

| # | Hipótese | Mecanismo | Como testar | Se confirmada, que ação | Prioridade |
| --- | --- | --- | --- | --- | --- |
| H1 | O risco de detrator cresce com o atraso e salta a partir de certo número de dias | O cliente se programa pela data prometida; passado um limite, o atraso vira quebra de promessa | % de detratores por dia de atraso; árvore de decisão rasa para achar o corte | Prometer prazos abaixo do ponto de ruptura e avisar o cliente antes de cruzá-lo | Alta |
| H2 | Uma nova tentativa de entrega piora a nota mesmo com o pedido no prazo | A tentativa frustrada passa trabalho ao cliente: esperar de novo, reagendar ou buscar o pacote | % de detratores por número de tentativas, só em pedidos sem atraso | Agendamento da entrega e retirada em ponto parceiro | Média |
| H3 | O tempo até a resolução pesa mais que o número de contatos | Procurar o atendimento não frustra por si; esperar pela solução, sim | % de detratores por faixa de tempo de resolução, entre pedidos com o mesmo número de contatos | Meta de prazo de resolução e fila prioritária para pedidos com falha | Alta |
| H4 | Clientes antigos toleram mais falhas que clientes novos | O histórico bom funciona como crédito, e a falha é lida como exceção | % de detratores por atraso × tempo de relacionamento | Priorizar contato proativo com clientes novos que tiveram falha | Média |
| H5 | Frete caro somado a atraso é a combinação que mais gera detratores | Quem paga mais pelo frete paga pelo prazo, e o atraso quebra o que foi pago | % de detratores por frete relativo ao valor do pedido × atraso | Devolver o frete quando o pedido atrasar | Média |
| H6 | Desconto não compensa falha operacional | O desconto pesa na compra; a nota reflete a entrega, que vem depois | % de detratores por faixa de desconto, só em pedidos com falha | Corrigir a causa em vez de oferecer cupom genérico | Média |
| H7 | Diferenças de NPS entre regiões vêm da logística, não do perfil regional | Regiões mais distantes têm prazos maiores e mais atrasos | % de detratores por região dentro da mesma faixa de atraso | Tratar como problema de malha logística e de SLA por região | Alta |
| H8 | Falhas acumuladas no mesmo pedido pesam mais que a soma das falhas isoladas | Uma falha costuma ser perdoada; a segunda confirma que a loja não é confiável | % de detratores pelo número de falhas no pedido (atraso, nova tentativa, reclamação, resolução longa), para ver se o risco acelera | Acionar recuperação quando o pedido acumular a segunda falha | Alta |
| H9 | Uma parcela dos detratores não teve nenhuma falha registrada na base | Há causas que a base não mede, como produto, expectativa e preço | % de detratores sem falha de entrega ou atendimento; o teste é parcial, porque a causa não aparece | Registrar produto, categoria e motivo da nota | Média |

Na análise exploratória (Etapa 4), cada hipótese termina como confirmada, refutada ou inconclusiva, com o número que sustenta o veredito.

## Glossário

| Termo | Definição |
| --- | --- |
| NPS (Net Promoter Score) | Percentual de promotores menos percentual de detratores, de −100 a +100 |
| Promotor | Cliente que dá nota 9 ou 10 à pergunta de recomendação |
| Neutro | Cliente que dá nota 7 ou 8; conta no total, mas não entra na subtração do NPS |
| Detrator | Cliente que dá nota de 0 a 6 |
| NPS transacional | NPS medido logo após uma compra ou um atendimento, sobre aquela experiência |
| NPS relacional | NPS medido periodicamente, sobre o relacionamento com a marca |
| CSAT (Customer Satisfaction Score) | Nota de satisfação com uma interação ou etapa da jornada |
| CES (Customer Effort Score) | Medida do esforço que o cliente fez para resolver uma demanda |
| SLA (Service Level Agreement) | Nível de serviço acordado, como o prazo máximo de entrega |
| Churn | Proporção de clientes que deixam de comprar num período |
| LTV (Lifetime Value) | Receita ou margem que um cliente gera ao longo do relacionamento |
| CAC (Custo de Aquisição de Cliente) | Gasto médio para conquistar um cliente novo |
| Score de risco | Probabilidade estimada de um cliente se tornar detrator |
| Modelo ingênuo | Referência mínima que ignora as variáveis, como dar o mesmo risco a todos os clientes |
| PR-AUC | Medida de 0 a 1 da capacidade do modelo de encontrar detratores sem gerar alarmes falsos demais |
| Métrica de proteção | Indicador que não pode piorar enquanto a meta melhora |
| Vazamento de dados | Uso, no modelo, de informação que só existe depois do momento da previsão |
| Grupo de controle | Clientes sorteados para não receber a ação, o que permite medir o efeito dela |

## Referências

- Brasil (2018). *Lei nº 13.709, de 14 de agosto de 2018: Lei Geral de Proteção de Dados Pessoais (LGPD)*. https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm. Acesso em 26/10/2026.
- Economic News Brasil (2026). *Vendas no e-commerce e varejo sobem 18%, mas frete define quem compra*. 06/04/2026. Dados da nstech, pela plataforma Frete Rápido. https://economicnewsbrasil.com.br/2026/04/06/frete-decide-compra-e-commerce-semana-consumidor/. Acesso em 26/10/2026.
- Keiningham, T. L.; Cooil, B.; Andreassen, T. W.; Aksoy, L. (2007). A longitudinal examination of Net Promoter and firm revenue growth. *Journal of Marketing*, 71(3). https://doi.org/10.1509/jmkg.71.3.39. Consultado o resumo. Acesso em 26/10/2026.
- Meio & Mensagem (2026). *As marcas mais recomendadas do Brasil, pelo NPS Benchmarking*. Por Giovana Oréfice, 18/05/2026. Dados do NPS Benchmarking 2026, da Opinion Box. https://www.meioemensagem.com.br/marketing/as-marcas-mais-recomendadas-do-brasil-segundo-o-nps-benchmarking-2026. Acesso em 26/10/2026.
- Reichheld, F. F. (2003). The one number you need to grow. *Harvard Business Review*, 81(12), 46–54. https://hbr.org/2003/12/the-one-number-you-need-to-grow. Consultado o resumo. Acesso em 26/10/2026.
- Senacon (2025). *Boletim Consumidor.gov.br 2025*. Secretaria Nacional do Consumidor, Ministério da Justiça e Segurança Pública. https://www.gov.br/mj/pt-br/assuntos/seus-direitos/consumidor/defesadoconsumidor/Biblioteca/boletins-1/boletim-consumidor-gov-br-2025-vfinal.pdf. Acesso em 26/10/2026.
- Seu Crédito Digital (2026). *Reclame Aqui: como é calculado o nível de reputação das empresas?* Por Ana Luisa, atualizado em 19/01/2026. https://seucreditodigital.com.br/reclame-aqui-como-e-calculado-o-nivel-de-reputacao/. Acesso em 26/10/2026.
