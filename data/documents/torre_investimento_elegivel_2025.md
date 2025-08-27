---
title: "Torre de Investimento Elegível 2025 — Guia de Apuração"
version: "v1.0"
date: "2025-08-18"
owner: "Equatorial Energia (autor: Lucas Eloi)"
tags: ["Torre Elegível", "AFFA", "PM", "IQO", "Capitalização", "VR_Distribuidora"]
---

# Torre de Investimento Elegível 2025 — Documento de Referência para RAG

> **Objetivo:** Este documento explica o processo de **apuração da Torre de Investimento Elegível 2025**, com foco nos indicadores, fórmulas de cálculo, exemplos práticos e glossário, para ser utilizado por um agente RAG na resolução de dúvidas.

---

## Sumário
- [1. Novo Indicador da Torre Elegível — Mudanças em relação a 2024](#1-novo-indicador-da-torre-elegível--mudanças-em-relação-a-2024)
- [2. Fórmula de cálculo do AFFA](#2-fórmula-de-cálculo-do-affa)
  - [2.1 50% Avanço Físico (AF)](#21-50-avanç o-físico-af)
  - [2.2 Capitalização Ajustada (CA) — Método](#22-capitalização-ajustada-ca--método)
- [3. Prazo Médio (PM)](#3-prazo-médio-pm)
  - [3.1 Prazo Médio de Obras (PMO) — Metodologia e Metas](#31-prazo-médio-de-obras-pmo--metodologia-e-metas)
- [4. Índice de Qualidade de Obras (IQO)](#4-índice-de-qualidade-de-obras-iqo)
- [5. VR_Distribuidora e VR_Ativo — Definições, Fórmulas e Exemplos](#5-vr_distribuidora-e-vr_ativo--definições-fórmulas-e-exemplos)
  - [5.1 Cálculo do VR_Distribuidora (exemplo EQTL-PA 2024)](#51-cálculo-do-vr_distribuidora-exemplo-eqtl-pa-2024)
  - [5.2 Formação do VR_Ativo (por TUC/PI)](#52-formação-do-vr_ativo-por-tucpi)
  - [5.3 Tabela — VR Unitário por Ativo (EQTL MA 2025)](#53-tabela--vr-unitário-por-ativo-eqtl-ma-2025)
  - [5.4 Exemplo de apuração de VRs por ativo — Obra RD](#54-exemplo-de-apuração-de-vrs-por-ativo--obra-rd)
- [6. Campos e Chaves — Explicações (SAP/Contábil)](#6-campos-e-chaves--explicações-sapcontábil)
- [7. Exemplo de classificação TUC — Poste de Concreto](#7-exemplo-de-classificação-tuc--poste-de-concreto)
- [8. Referências Rápidas (Q&A)](#8-referências-rápidas-qa)

---

## 1. Novo Indicador da Torre Elegível — Mudanças em relação a 2024

**Em 2024**, as frentes de meta eram:
1. **Avanço Físico** — Medido pelas áreas executoras, conforme o modelo de execução de obras.
2. **Financeiro Ajustado** — Ajustado pelo físico, gerando economia e melhorando o resultado.
3. **Aderência do AIC** — Curva ajustada pela não realização financeira (proporcional à curva de capitalização do giro).
4. **Duração de Obras** — Média de dias de duração das obras, ponderada pelo saldo do AIC de cada regional.

**Em 2025**, existem **três indicadores** e suas principais composições/ajustes:

### 1.1 AFFA — Avanço Físico e Financeiro Ajustado
- **Submetas em 2025**: Avanço Físico (AF), Financeiro Ajustado (FA) e **Capitalização Ajustada (CA)** *(novo)*.
- **Avanço Físico**: Calculado via **VR**, exceto **Obras AT** (nestas, medido por cronograma de capitalização).
- **Financeiro Ajustado**: Mantém a fórmula, aderente ao novo modelo de **AF**.
- **Capitalização Ajustada (novo)**: Indicador ajustado pelo físico para refletir economia.

### 1.2 PM — Prazo Médio *(novo desenho em 2025)*
- Em 2024: composto por **AIC** e **Duração de Obras**.
- Em 2025: **AIC foi removido** e foram adicionadas duas submetas, resultando em:
  - **Prazo Médio de Obras (PMO)**
  - **Prazo Médio de Investimentos (PMI)**
  - **Duração de Obras**

### 1.3 IQO — Qualidade das Obras *(novo em 2025)*
- Submetas: **Devolução**, **Fiscalização** e **Carta Diretriz**.
- Índice com metodologia adequada à realidade de cada área executora.

**Resumo 2025 — composição final**
1. **Avanço Físico** (via VR, exceto Obras AT, nestas por cronograma de capitalização)
2. **Financeiro Ajustado** (mesma fórmula, aderente ao novo AF)
3. **Capitalização Ajustada (novo)**
4. **Qualidade das Obras (novo)**
5. **Prazo Médio (novo)** — subdividido em **PMI (com estoque)** e **PMO**

---

## 2. Fórmula de cálculo do AFFA

O **AFFA** mede a eficiência na execução de projetos em relação ao orçamento.

```
AFFA = 50% * Avanço Físico (AF) + 25% * Financeiro Ajustado (FA) + 25% * Capitalização Ajustada (CA)
```

**O AFFA considera:**
- Avanço físico realizado na capitalização (**VR Real / VR Previsto**);
- Avanço financeiro ajustado;
- Capitalização ajustada;
- Compara desempenho real versus orçado, permitindo identificar desvios físicos e financeiros e sustentar ajustes de otimização.

### 2.1 50% Avanço Físico (AF)
**Definição resumida:** mede a realização física em **VRs** frente ao planejado (**R / P**).  
**Fórmula:** `AF = QTD VR Real (R) ÷ QTD VR Planejado (P)`.

### 2.2 Capitalização Ajustada (CA) — Método
**Etapas da metodologia:**
1. **Apuração do VR Real praticado:** `VR_Real_praticado (R$) = VOC (capitalização real) ÷ QTD VR Real (R)`  
2. **Fator de ajuste:** `Fator = VR_Real_praticado ÷ VR_D (VR_Distribuidora)`  
3. **Capitalização Ajustada:** `VOC_Ajustado = VOC ÷ Fator`  
4. **% aplicável para meta:** `% = VOC_Ajustado ÷ VOC`

---

## 3. Prazo Médio (PM)

**Objetivo:** medir o **tempo médio (em meses)** em que os recursos permanecem alocados antes da conclusão de obras/investimentos.

```
PM = 60% * Prazo Médio de Obras (PMO) + 40% * Prazo Médio de Investimentos (PMI)
```

- **PMO:** `Saldo de Obras em Curso no mês (AIC) ÷ Média das Adições dos últimos 12 meses`
- **PMI:** `(AIC Total + Estoque - ANE - Provisões) ÷ Média das Adições do AIC Total nos últimos 12 meses`

### 3.1 Prazo Médio de Obras (PMO) — Metodologia e Metas
**Metodologia:**  
- Padrão único de avaliação com **metas individualizadas por distribuidora**.  
- A **nota** é derivada da aderência entre o resultado do mês e a meta, posicionada em uma **régua (spread)** pré-definida.

**Metas por empresa (PMO):**
| Empresa | Meta de PMO (meses)  |
|---|---|
| MA | 7,20 |
| PA | 9,39 |
| PI | 7,74 |
| AL | 7,21 |
| RS | 10,25 |
| AP | 9,19 |
| GO | 7,68 |

**Régua de aderência (nota → % da meta):**
| Nota | % |
|---|---|
| 15 | 83,33 |
| 14 | 86,67 |
| 13 | 90,00 |
| 12 | 93,33 |
| 11 | 96,67 |
| 10 | 100,00 |
| 9 | 102,78 |
| 8 | 105,56 |
| 7 | 108,33 |
| 6 | 111,11 |
| 5 | 113,89 |
| 4 | 116,67 |
| 3 | 119,44 |
| 2 | 122,22 |
| 1 | 125,00 |

---

## 4. Índice de Qualidade de Obras (IQO)

**Objetivo:** avaliar a **qualidade das obras entregues** considerando três dimensões: **Devolução de Obras (IDO)**, **Obras Fiscalizadas (IFO)** e **Carta Diretriz (ICD)**.  
> *Observação:* **Carta Diretriz** aplica-se somente para **Obras RD** e **PLPT**.

**Fórmula do IQO:**
```
IQO = 25% * IDO + 25% * IFO + 50% * ICD
```

**Componentes:**
- `IDO = Nº de Obras Devolvidas ÷ Total de Obras`
- `IFO = Nº de Obras que atenderam ao As Built ÷ Total de Obras Fiscalizadas`
- `ICD = Índice de Cumprimento da Carta Diretriz`

---

## 5. VR_Distribuidora e VR_Ativo — Definições, Fórmulas e Exemplos

### 5.1 Cálculo do VR_Distribuidora (exemplo EQTL-PA 2024)
**Definição:** valor calculado por empresa com base no **preço médio dos postes de concreto** instalados no ano anterior; funciona como unidade padrão para comparação.
- **QPC_2024:** quantidade de postes de concreto capitalizados  
- **VOC_PC_2024:** valor total desses postes  
- **FAC:** fator de ajuste contratual  
- **FAD:** fator adicional estratégico

**Fórmula:**
```
VR_Distribuidora = (VOC_PC_2024 ÷ QPC_2024) × FAC × FAD
```

**Exemplo (EQTL Pará 2024):**
```
QPC_2024 = 53.368
VOC_PC_2024 = R$ 176.895.447,45
FAC = 104,518%  → 1,04518
FAD = 110%      → 1,10

VR_Distribuidora = (176.895.447,45 ÷ 53.368) × 1,04518 × 1,10
                 ≈ 3.314,64 × 1,04518 × 1,10
                 ≈ R$ 3.810,86
```

> Observação: para 2025, também é utilizado VR_Distribuidora **EQTL MA = R$ 5.702,46** (quando aplicável nos exemplos).

### 5.2 Formação do VR_Ativo (por TUC/PI)
O **VR_Ativo** (valor de referência unitário por ativo) é apurado a partir dos ativos capitalizados em 2024, organizados por **TUC** e **PI**, considerando:
1. **QTD_TUC_PI_2024** — quantidade total do ativo capitalizado no ano.  
2. **VOC_TUC_PI_2024** — valor original de construção total do ativo no período.  
3. **FAC** — fator de ajuste contratual (inclui Fator COGE e ajustes).  
4. **VR_Distribuidora** — valor médio de referência (derivado do ativo padrão: **Poste de Concreto**).

**Exemplo (TUC 565 — Transformador; PI 801.110.0023):**
```
QTD_TUC_PI_2024 = 2.993
VOC_TUC_PI_2024 = R$ 24.834.523,87
FAC = 106,6798% → 1,066798
VR_Distribuidora = R$ 5.702,46

1) Unitário: VOC/QTD = 24.834.523,87 ÷ 2.993 = R$ 8.297,54
2) Ajuste FAC: 8.297,54 × 1,066798 = R$ 8.851,80
3) Em VRs: 8.851,80 ÷ 5.702,46 ≈ 1,552  → **VR Unitário**
Resultado: cada TUC 565 capitalizado no PI 801.110.0023 contabiliza **1,552 VRs**.
```

### 5.3 Tabela — VR Unitário por Ativo (EQTL MA 2025)
| Empresa | Ano | A3 | TUC | Segmento | PI | Descrição do PI | Soma QTD (2024) | Soma VOC (2024) | VOC Unit. R$ + % Ajuste 2025 | VR Unitário por Ativo (TUC) | % Ajuste 2025 VOC | Tipo de Ativo |
|---|---:|---:|---:|---|---:|---|---:|---:|---:|---:|---:|---|
| Equatorial MA | 2025 | 1 | 190 | IOP | 8011100023 | Investimento Operacional RD | 24.766,42 | 2.904.122,86 | 127,03 | 0,0223 | 1,0833 | Condutor Nu |
| Equatorial MA | 2025 | 1 | 255 | IOP | 8011100023 | Investimento Operacional RD | 4.404,00 | 23.731.720,48 | 5.632,09 | 0,9877 | 1,0452 | Estrutura (Poste, Torre) - Concreto |
| Equatorial MA | 2025 | 4 | 255 | IOP | 8011100023 | Investimento Operacional RD | 3,00 | 3.875,20 | 1.350,08 | 0,2368 | 1,0452 | Estrutura (Poste metálico) |
| Equatorial MA | 2025 |  | 125 | IOP | 8011100023 | Investimento Operacional RD | 3,00 | 4.191,00 | 1.490,82 | 0,2614 | 1,0672 | Banco de Capacitores Paralelos |
| Equatorial MA | 2025 |  | 160 | IOP | 8011100023 | Investimento Operacional RD | 727,00 | 785.764,49 | 1.168,05 | 0,2048 | 1,0807 | Chave |
| Equatorial MA | 2025 |  | 190 | IOP | 8011100023 | Investimento Operacional RD | 90.660,25 | 4.306.445,31 | 52,81 | 0,0093 | 1,1118 | Condutor isolado |
| Equatorial MA | 2025 |  | 255 | IOP | 8011100023 | Investimento Operacional RD | 659,00 | 4.169.337,24 | 6.612,56 | 1,1596 | 1,0452 | Estrutura (Poste PFVD/MDR) |
| Equatorial MA | 2025 |  | 310 | IOP | 8011100023 | Investimento Operacional RD | 1.586,00 | 811.881,32 | 535,03 | 0,0938 | 1,0452 | Para-raios |
| Equatorial MA | 2025 |  | 340 | IOP | 8011100023 | Investimento Operacional RD | 50,00 | 3.000.454,96 | 63.551,44 | 11,1446 | 1,0590 | Regulador de Tensão |
| Equatorial MA | 2025 |  | 345 | IOP | 8011100023 | Investimento Operacional RD | 1,00 | 49.310,44 | 54.917,18 | 9,6304 | 1,1368 | Religador |
| Equatorial MA | 2025 |  | 565 | IOP | 8011100023 | Investimento Operacional RD | 2.993,00 | 24.834.523,87 | 8.851,79 | 1,5523 | 1,0668 | Transformador de Distribuição |
| Equatorial MA | 2025 |  | 605 | IOP | 8011100023 | Investimento Operacional RD | 182,00 | 148.217,16 | 939,52 | 0,1648 | 1,1537 | Unidade de Geração Solar Fotovoltaica |

### 5.4 Exemplo de apuração de VRs por Ativo — Obra RD
**Obra:** MA-2401012PMC1.4.0006.1 — **Valor total:** R$ 2.427.163,14  
**VRs (Base: tabela 2024 ajustada p/ 2025):**
- **Poste de Concreto (TUC 255):** Qtd 190 × **0,7017 VRs** = **133,32 VRs**
- **Transformador RD (TUC 565):** Qtd 18 × **4,4258 VRs** = **79,66 VRs**
- **Condutor Isolado (TUC 190):** Qtd 6.796 m × **0,0072 VRs** = **48,93 VRs**
- **Condutor Nu (TUC 190):** Qtd 2.269,4 kg × **0,0106 VRs** = **24,06 VRs**
- **Total Geral:** **285,97 VRs**

**Cálculo do Avanço Físico (AF):**
```
R = 285,97 (VR Real)          P = 309,85 (VR Planejado)
AF = R ÷ P = 285,97 ÷ 309,85 = 0,923 → 92,3%
```

**Capitalização Ajustada — Passo a passo:**
```
VOC (Real)        = R$ 2.427.163,14
VR_Real_praticado = R$ 8.487,27
VR_D              = R$ 5.702,46

Fator = VR_Real_praticado ÷ VR_D = 1,488
VOC_Ajustado = VOC ÷ Fator = 2.427.163,14 ÷ 1,488 = R$ 1.631.231,97
% aplicável para meta = VOC_Ajustado ÷ VOC = 67,2%
```

---

## 6. Campos e Chaves — Explicações (SAP/Contábil)

**Campos das linhas (exemplos de posições/colunas):**
- **06** — PEP SAP (identificação da obra)  
- **07** — Código do Material (SAP)  
- **08** — Descrição do tipo de ativo lançado (contabilidade / as built)  
- **09** — Quantidade de Ativos Capitalizados  
- **10** — **VOC** (Valor Original de Construção) do bem na capitalização (inclui: material, instalação/montagem, frete, componentes menores, rateios, serviços etc.)  
- **11** — **TUC** (*Tipo de Unidade de Cadastro*, conforme MCPSE/ANEEL)  
- **12–18** — **Atributos A1–A6** (características físicas/operacionais do bem)  
- **20** — **Chave** de rastreabilidade do ativo (para associação ao VR Unitário). Composições possíveis:  
  - `TU + A3 + PI`  
  - `TUC + PI`  
  - `TUC + PI + TI + PI`  
- **25** — **VALOR PI ATIVO (Unitário):** VR unitário do ativo (pela chave)  
- **26** — **VALOR PI ATIVO × QTD ATIVO:** total de VRs do ativo (unitário × quantidade)  
- **27** — **Segmentador:** segmentação baseada no **PI** (para meta, considera-se o PI e **não** o PEP)

**O que é Capitalização?**  
Registrar oficialmente no patrimônio os bens do sistema elétrico (postes, redes, transformadores, medidores, etc.), incluindo custos associados: instalação, frete/transporte, suporte técnico, rateios administrativos/operacionais, componentes menores e demais custos adicionais.

---

## 7. Exemplo de classificação TUC — Poste de Concreto
**TUC:** 255 — **Descrição:** ESTRUTURA - POSTE

**Atributos (exemplo):**
- **A1 (Tipo de bem):** 01 → Poste  
- **A2 (Tipo de poste):** 02 → Duplo T  
- **A3 (Tipo do material):** 01 → Concreto  
- **A4 (Altura):** 09 → 9 metros  
- **A5 (Carregamento/Esforço):** 16 → Classe 300 daN  
- **A6:** 00 → Sem classificação adicional

---

## 8. Referências Rápidas (Q&A)

**Q1. O que compõe o AFFA?**  
**R:** 50% AF + 25% FA + 25% CA.

**Q2. Como calculo AF?**  
**R:** `AF = VR Real ÷ VR Planejado` (ex.: 285,97 ÷ 309,85 = 92,3%).

**Q3. Como obtenho o VR_Distribuidora?**  
**R:** `(VOC_PC ÷ QPC_PC) × FAC × FAD` (ex.: R$ 3.810,86 para EQTL-PA/2024).

**Q4. O que muda em 2025 versus 2024?**  
**R:** Entrada de **Capitalização Ajustada** no AFFA, criação do **IQO**, e redesenho do **PM** (PMO + PMI + Duração).

**Q5. Quando usar VR versus cronograma de capitalização?**  
**R:** **VR** é padrão; **Obras AT** usam **cronograma de capitalização**.

**Q6. O que é a Chave do VR?**  
**R:** Composição que vincula o ativo à referência de VR Unitário (ex.: `TUC + PI`).

---

## 9. GLOSSÁRIO TÉCNICO

| Termo | Definição |
|-------|-----------|
| **VOC** | Valor Original Construção (material + custos associados) |
| **VOC_PC** | Valor Original Construção Poste Concreto (valor total dos postes de concreto no período) |
| **QPC** | Quantidade de Postes de Concreto Capitalizados (no período de cálculo) |
| **QTD_TUC_PI** | Quantidade Total do Ativo por TUC e PI (no período de referência) |
| **VOC_TUC_PI** | Valor Original Construção Total do Ativo por TUC e PI (no período) |
| **AIC** | Ativos Imobilizados em Curso |
| **FAC** | Fator Ajuste Contratual (inclui Fator COGE e outros ajustes) |
| **FAD** | Fator Adicional Estratégico |
| **TUC** | Tipo Unidade Cadastro (classificação da natureza e função técnica do ativo) |
| **PI** | Plano Investimento |
| **PMO** | Prazo Médio Obras |
| **PMI** | Prazo Médio Investimentos |
| **As Built** | Documentação final obra (conforme construído) |
| **ANE** | Ativo Não Elétrico |
| **VR** | Valor de Referência (unidade padrão para comparação de ativos) |
| **VR_Distribuidora** | Valor de Referência da Distribuidora (baseado em postes concreto) |
| **VR_Ativo** | Valor de Referência Unitário por Ativo específico |


---

> **Nota ao Agente RAG:** Priorize respostas curtas e objetivas; quando questionado sobre fórmulas, retorne o **passo a passo** e **exemplo numérico** mais próximo do contexto do usuário.
