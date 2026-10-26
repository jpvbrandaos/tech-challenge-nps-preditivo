# Registro de decisões

Decisões relevantes do projeto, com o porquê de cada uma. Decisões novas entram no fim. Uma decisão revista não é apagada: ganha uma entrada nova que cita a anterior.

## D-01 — A base de dados não é versionada no Git

- **Data e etapa:** 23/10/2026, Etapa 0
- **Contexto:** a base é um arquivo CSV público, mantido no repositório da disciplina.
- **Decisão:** o arquivo fica fora do Git. A pasta `data/` está no `.gitignore`, e o README indica a fonte oficial e o comando que baixa o arquivo.
- **Alternativa descartada:** versionar o CSV em `data/raw/`.
- **Por quê:** dados e código têm ciclos de vida diferentes, e a fonte oficial continua sendo uma só, sem cópias que possam divergir.
- **Consequências:** um clone novo não traz a base. O comando `python -m src.dataset` baixa o arquivo para `data/raw/` e confere a integridade dele pelo SHA-256.

## D-02 — Dúvidas sobre a base viram premissas documentadas

- **Data e etapa:** 26/10/2026, Etapa 1
- **Contexto:** o enunciado e o dicionário de dados deixam pontos em aberto, como o momento de coleta do CSAT, a forma de cálculo do atraso e a classificação de notas com casa decimal. Consultar os professores é possível, mas as respostas chegariam em prazo incerto e ficariam fora do repositório.
- **Decisão:** cada ponto em aberto vira uma premissa escrita, com o trecho do enunciado ou do dicionário que a sustenta e a etapa em que será testada. As premissas de negócio estão na [seção 7 do entendimento do negócio](entendimento_negocio.md#7-premissas-restrições-e-riscos); as que tratam do uso das variáveis no modelo entram na definição da target (Etapa 2).
- **Alternativa descartada:** consultar os professores e esperar as respostas antes de seguir.
- **Por quê:** uma premissa escrita pode ser auditada e revista por quem lê o repositório, e o projeto não fica parado à espera de resposta.
- **Consequências:** toda premissa testável é testada assim que a base permitir. Premissa contrariada pelos dados gera uma decisão nova, que cita esta. As que não puderem ser testadas entram nas limitações do README.

## D-03 — Partes 1 e 2 entregues em Markdown, em `reports/`, com link no README

- **Data e etapa:** 26/10/2026, Etapa 1
- **Contexto:** o enunciado faz perguntas nas Partes 1 e 2, mas o formato de entrega cita só repositório, slides e vídeo, sem dizer onde ficam essas respostas.
- **Decisão:** cada parte vira um documento Markdown em `reports/`, com link no README: `entendimento_negocio.md` para a Parte 1 e `definicao_target.md` para a Parte 2. Os slides trazem a síntese.
- **Alternativa descartada:** responder só nos slides.
- **Por quê:** o avaliador lê o repositório. O Markdown aparece formatado no GitHub, fica versionado e comporta o raciocínio completo, que nos slides precisaria ser cortado.
- **Consequências:** documentos e slides precisam trazer os mesmos números e conclusões, e essa conferência entra na revisão final (Etapa 10).

## D-04 — A Parte 4 é feita, mesmo sendo opcional

- **Data e etapa:** 26/10/2026, Etapa 1
- **Contexto:** o enunciado declara a Parte 4 opcional, "sem impacto negativo para quem optar por não realizá-lo". O vídeo, porém, precisa destacar como o modelo pode apoiar decisões reais, e os slides pedem a pergunta que o modelo busca responder quando o desafio é feito.
- **Decisão:** fazer a Parte 4, no mínimo a estratégia preditiva (Etapa 5) e uma versão enxuta do modelo em Python (Etapa 6).
- **Alternativa descartada:** pular a Parte 4 e dedicar o tempo só às partes obrigatórias.
- **Por quê:** sem modelo, um dos pontos obrigatórios do vídeo fica vago, e antecipar o risco de detrator é metade do problema de negócio ([seção 1 do entendimento do negócio](entendimento_negocio.md#1-o-problema-de-negócio)).
- **Consequências:** as partes obrigatórias têm prioridade no cronograma. A Parte 4 começa depois da análise exploratória, com o escopo ajustado ao tempo que restar.
