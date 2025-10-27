# Guia de Testes - Sistema RAG VOXMAP

## Checklist de Testes

Use este guia para validar que o sistema RAG está funcionando corretamente.

---

## 1. Verificação de Instalação

### ✅ Dependências Instaladas

```bash
pip list | grep qdrant
pip list | grep sentence-transformers
pip list | grep PyPDF2
```

**Esperado:**
```
qdrant-client     1.7.0 (ou superior)
sentence-transformers   2.2.2 (ou superior)
PyPDF2           3.0.0 (ou superior)
```

### ✅ Arquivos Presentes

Verifique se existem:
- [ ] `rag_module.py`
- [ ] `rag_config.py`
- [ ] `base_conhecimento/suporte_tecnico/` (com 2 arquivos .txt)
- [ ] `base_conhecimento/relacionamento/` (com 2 arquivos .txt)

---

## 2. Primeira Execução

### ✅ Inicialização do Sistema

```bash
streamlit run app_01.py
```

**Checklist visual:**
- [ ] Aplicação abre em http://localhost:8501
- [ ] Vê mensagem "🔧 Inicializando sistema RAG..." (primeira vez)
- [ ] Aguarda 1-2 minutos (download do modelo)
- [ ] Título mostra "📚 RAG Ativo"
- [ ] Sidebar tem seção "Base de Conhecimento (RAG)"
- [ ] Métrica mostra > 0 documentos

**Se falhar:**
- Veja mensagens de erro no terminal
- Verifique se .env tem OPENAI_API_KEY
- Consulte [RAG_README.md](RAG_README.md) → Troubleshooting

---

## 3. Testes Funcionais

### Caso de Uso 1: Suporte Técnico TI

**Configuração:**
1. Na sidebar, selecione: "Suporte Técnico TI"
2. Verifique se "Ativar RAG" está ON

**Perguntas de Teste:**

#### Teste 1.1: Problema de Rede
**Pergunta:** "Como resolver problema de internet lenta?"

**Esperado:**
- ✅ Resposta menciona: speedtest, drivers, canal Wi-Fi, Task Manager
- ✅ Sidebar mostra "Contexto usado": `guia_resolucao_problemas.txt`
- ✅ Score de relevância: >60%

**Se falhar:**
- Diminuir threshold para 0.3
- Verificar se documento está na pasta correta

---

#### Teste 1.2: Segurança
**Pergunta:** "Quais são os requisitos de senha corporativa?"

**Esperado:**
- ✅ Resposta menciona: 12 caracteres (admin), 8 (usuário), maiúscula, número, especial
- ✅ Contexto: `procedimentos_seguranca.txt`
- ✅ Score: >70%

---

#### Teste 1.3: Malware
**Pergunta:** "O que fazer se detectar malware no computador?"

**Esperado:**
- ✅ Resposta menciona: desconectar rede, não desligar, contatar TI
- ✅ Contexto: procedimentos de segurança
- ✅ Score: >60%

---

#### Teste 1.4: VPN
**Pergunta:** "Como funciona a VPN corporativa?"

**Esperado:**
- ✅ Resposta menciona: obrigatória, 2FA, 8 horas sessão
- ✅ Contexto: segurança ou procedimentos
- ✅ Score: >50%

---

### Caso de Uso 2: Relacionamento com Cliente

**Configuração:**
1. Na sidebar, selecione: "Relacionamento com Cliente"
2. Verifique se "Ativar RAG" está ON

**Perguntas de Teste:**

#### Teste 2.1: Devolução
**Pergunta:** "Qual o prazo para devolução de produtos?"

**Esperado:**
- ✅ Resposta menciona: 7 dias (arrependimento) ou 30 dias (tamanho/cor)
- ✅ Contexto: `politicas_atendimento.txt`
- ✅ Score: >80%

---

#### Teste 2.2: Cliente Furioso
**Pergunta:** "Como lidar com um cliente muito furioso?"

**Esperado:**
- ✅ Resposta menciona: manter calma, deixar desabafar, não levar para o pessoal
- ✅ Contexto: `gestao_conflitos.txt`
- ✅ Score: >70%

---

#### Teste 2.3: Canais de Atendimento
**Pergunta:** "Quais são os canais de atendimento disponíveis?"

**Esperado:**
- ✅ Resposta menciona: chat (8h-20h), telefone 0800, email (24h), WhatsApp
- ✅ Contexto: políticas de atendimento
- ✅ Score: >75%

---

#### Teste 2.4: Reembolso
**Pergunta:** "Em quanto tempo recebo o reembolso após devolução?"

**Esperado:**
- ✅ Resposta menciona: até 10 dias úteis, depende forma de pagamento
- ✅ Contexto: políticas de atendimento
- ✅ Score: >70%

---

## 4. Testes de Configuração

### Teste 4.1: Ajustar Top K

**Procedimento:**
1. Sidebar → Expandir "Configurações RAG"
2. Mudar "Documentos retornados" para 5
3. Fazer pergunta: "Como lidar com cliente difícil?"

**Esperado:**
- ✅ Sidebar mostra até 5 documentos no "Contexto usado"
- ✅ Resposta mais detalhada (mais contexto)

---

### Teste 4.2: Ajustar Threshold

**Procedimento:**
1. Mudar "Relevância mínima" para 0.8 (muito alto)
2. Fazer pergunta genérica: "Me ajude com atendimento"

**Esperado:**
- ✅ Sidebar mostra poucos ou nenhum documento
- ✅ Resposta mais genérica (sem contexto específico)

**Ajustar de volta:**
1. Mudar para 0.5 (padrão)
2. Refazer pergunta

**Esperado:**
- ✅ Agora encontra documentos

---

### Teste 4.3: Caso de Uso "Geral"

**Procedimento:**
1. Selecionar "Atendimento Geral"
2. Fazer pergunta: "Como resetar senha e devolver produto?"

**Esperado:**
- ✅ Busca em AMBAS as categorias
- ✅ Pode mostrar documentos de suporte_tecnico E relacionamento
- ✅ Resposta cobre ambos os tópicos

---

## 5. Testes de Recarregamento

### Teste 5.1: Adicionar Novo Documento

**Procedimento:**
1. Criar arquivo: `base_conhecimento/relacionamento/teste.txt`
2. Conteúdo:
```
DOCUMENTO DE TESTE

Este é um documento especial com uma palavra única: XYZABC123
```
3. Na aplicação, clicar "🔄 Recarregar"
4. Aguardar processamento
5. Perguntar: "O que você sabe sobre XYZABC123?"

**Esperado:**
- ✅ Processamento bem-sucedido
- ✅ Métrica de documentos aumenta
- ✅ Resposta menciona o documento de teste
- ✅ Contexto mostra `teste.txt`

**Limpar:**
- Deletar `teste.txt`
- Recarregar novamente

---

### Teste 5.2: Modificar Documento Existente

**Procedimento:**
1. Abrir `base_conhecimento/suporte_tecnico/guia_resolucao_problemas.txt`
2. Adicionar no final:
```
=== TESTE ===
Protocolo especial: TESTE-PROTOCOLO-789
```
3. Salvar
4. Recarregar no app
5. Perguntar: "Qual o protocolo especial de teste?"

**Esperado:**
- ✅ Resposta menciona: TESTE-PROTOCOLO-789
- ✅ Contexto mostra documento modificado

**Reverter:**
- Remover linha adicionada
- Recarregar

---

## 6. Testes de Desempenho

### Teste 6.1: Tempo de Resposta

**Procedimento:**
1. Fazer pergunta simples
2. Cronometrar tempo total

**Benchmarks:**
- Primeira pergunta (after startup): 2-5 segundos ✅
- Perguntas subsequentes: 1-3 segundos ✅
- Muito lento (>10s): ⚠️ Investigar

**Se muito lento:**
- Verificar internet (OpenAI)
- Verificar CPU (embeddings)
- Diminuir top_k

---

### Teste 6.2: Qualidade das Respostas

**Procedimento:**
Fazer 10 perguntas relacionadas aos documentos

**Métricas:**
- **Excelente:** 8+ respostas usam contexto correto (score >60%)
- **Bom:** 6-7 respostas usam contexto
- **Ruim:** <5 respostas usam contexto

**Se ruim:**
- Diminuir threshold (0.3-0.4)
- Aumentar top_k (4-5)
- Revisar qualidade dos documentos

---

## 7. Testes de Robustez

### Teste 7.1: Pergunta Sem Resposta na Base

**Pergunta:** "Como fazer bolo de chocolate?"

**Esperado:**
- ✅ Sidebar mostra "sem contexto" ou documentos irrelevantes (score <30%)
- ✅ Resposta genérica (IA responde sem base)
- ✅ Sistema não quebra

---

### Teste 7.2: Pergunta em Outro Idioma

**Pergunta:** "What is the return policy?" (em inglês)

**Esperado:**
- ✅ Modelo multilíngue deve encontrar documentos em PT
- ✅ Resposta pode ser em inglês OU português
- ✅ Score pode ser um pouco mais baixo (<60%)

---

### Teste 7.3: Pergunta Muito Longa

**Pergunta:** (Escrever 500+ palavras sobre um problema complexo)

**Esperado:**
- ✅ Sistema processa sem erro
- ✅ Encontra documentos relevantes
- ✅ Resposta focada (ignora partes irrelevantes)

---

### Teste 7.4: Desativar RAG

**Procedimento:**
1. Desligar toggle "Ativar RAG"
2. Fazer pergunta: "Qual o prazo de devolução?"

**Esperado:**
- ✅ Resposta genérica (sem dados específicos da empresa)
- ✅ Sidebar não mostra "Contexto usado"
- ✅ Sistema continua funcionando

**Reativar:**
1. Ligar toggle
2. Refazer pergunta

**Esperado:**
- ✅ Agora resposta específica com dados da empresa

---

## 8. Testes de Integração

### Teste 8.1: RAG + Análise de Sentimento

**Procedimento:**
1. Ativar análise de sentimento
2. Ativar RAG
3. Fazer pergunta frustrante: "Estou muito irritado, meu produto chegou quebrado!"

**Esperado:**
- ✅ Sentimento detecta: negativo
- ✅ RAG busca políticas de devolução/troca
- ✅ Resposta empática + solução baseada em documentos

---

### Teste 8.2: Múltiplas Mensagens (Contexto)

**Procedimento:**
1. Mensagem 1: "Quero devolver um produto"
2. Mensagem 2: "Qual o prazo?"
3. Mensagem 3: "E se perdeu a nota fiscal?"

**Esperado:**
- ✅ Todas as respostas usam contexto RAG apropriado
- ✅ Sistema mantém coerência na conversa
- ✅ Últimas 2 mensagens são usadas para busca

---

## 9. Testes Visuais (Interface)

### Checklist Visual:

- [ ] **Título:** Mostra "📚 RAG Ativo"
- [ ] **Sidebar:** Seção "Base de Conhecimento (RAG)" visível
- [ ] **Métrica:** Número de documentos correto
- [ ] **Toggle:** "Ativar RAG" funciona
- [ ] **Seletor:** Dropdown de casos de uso
- [ ] **Expander:** "Configurações RAG" abre/fecha
- [ ] **Expander:** "Contexto usado" mostra documentos após resposta
- [ ] **Botão:** "Recarregar" funciona
- [ ] **Popover:** "Stats" mostra JSON com estatísticas

---

## 10. Teste Final: Fluxo Completo

### Cenário 1: Suporte Técnico

1. Abrir app
2. Selecionar "Suporte Técnico TI"
3. Perguntar: "Minha internet está muito lenta, o que fazer?"
4. Verificar resposta detalhada com passos específicos
5. Ver contexto usado na sidebar
6. Avaliar satisfação (thumbs up)

✅ **Sucesso se:**
- Resposta completa e precisa
- Menciona informações dos documentos
- Score >60%

---

### Cenário 2: Atendimento ao Cliente

1. Selecionar "Relacionamento com Cliente"
2. Perguntar: "Comprei uma TV que chegou quebrada, o que posso fazer?"
3. Verificar resposta com opções de troca/devolução
4. Ver prazos específicos mencionados
5. Verificar contexto na sidebar

✅ **Sucesso se:**
- Resposta menciona: 7 dias arrependimento, defeito, troca
- Explica processo passo a passo
- Score >65%

---

### Cenário 3: Consulta Geral

1. Selecionar "Atendimento Geral"
2. Perguntar: "Preciso resetar minha senha e também devolver um produto"
3. Verificar resposta cobre ambos os tópicos
4. Ver contextos de ambas as categorias

✅ **Sucesso se:**
- Resposta aborda senha E devolução
- Usa documentos das 2 categorias
- Resposta coerente e organizada

---

## Registro de Testes

Use esta tabela para registrar seus testes:

| # | Teste | Data | Resultado | Score | Observações |
|---|-------|------|-----------|-------|-------------|
| 1.1 | Internet lenta | __/__ | ✅ / ❌ | __% | |
| 1.2 | Requisitos senha | __/__ | ✅ / ❌ | __% | |
| 1.3 | Detectar malware | __/__ | ✅ / ❌ | __% | |
| 1.4 | VPN corporativa | __/__ | ✅ / ❌ | __% | |
| 2.1 | Prazo devolução | __/__ | ✅ / ❌ | __% | |
| 2.2 | Cliente furioso | __/__ | ✅ / ❌ | __% | |
| 2.3 | Canais atendimento | __/__ | ✅ / ❌ | __% | |
| 2.4 | Tempo reembolso | __/__ | ✅ / ❌ | __% | |

**Meta de Sucesso:** 80% dos testes com ✅ e score médio >60%

---

## Troubleshooting de Testes

### Problema: Scores muito baixos (<40%)

**Soluções:**
1. Diminuir threshold (0.3)
2. Aumentar top_k (5)
3. Verificar se pergunta está relacionada aos documentos
4. Melhorar qualidade dos documentos

---

### Problema: Não encontra nenhum documento

**Soluções:**
1. Verificar se RAG está ativado (toggle)
2. Verificar se caso de uso correto está selecionado
3. Threshold pode estar muito alto (diminuir para 0.3)
4. Recarregar base de conhecimento

---

### Problema: Respostas genéricas (não usa contexto)

**Possíveis causas:**
1. Documentos encontrados, mas IA não está usando
   - Verificar se contexto aparece na sidebar
   - Score pode estar baixo
   - Aumentar número de documentos (top_k)

2. IA ignora contexto no prompt
   - Problema raro
   - Verificar `rag_config.py` → INTEGRATION_CONFIG

---

### Problema: Muito lento

**Diagnóstico:**
1. Primeira vez: Normal (1-2 minutos download modelo)
2. Sempre lento:
   - CPU sobrecarregado?
   - Internet lenta? (OpenAI API)
   - Muitos documentos? (diminuir top_k)

---

## Relatório de Testes

Após completar todos os testes, preencha:

**Data dos testes:** ___/___/2025
**Versão testada:** 1.0
**Testado por:** _______________

**Resultados:**
- Total de testes: ___
- Testes passados: ___
- Testes falhados: ___
- Score médio: ___%

**Problemas encontrados:**
1. _______________
2. _______________
3. _______________

**Sugestões de melhoria:**
1. _______________
2. _______________
3. _______________

**Conclusão:**
[ ] Sistema aprovado para produção
[ ] Requer ajustes (especificar acima)
[ ] Requer novos testes após correções

---

**Próximos passos após testes bem-sucedidos:**
1. ✅ Adicionar documentos reais da empresa
2. ✅ Treinar equipe no uso do sistema
3. ✅ Monitorar métricas de satisfação
4. ✅ Coletar feedback dos usuários
5. ✅ Iterar e melhorar continuamente

---

**Fim do Guia de Testes**

Para suporte técnico, consulte [RAG_README.md](RAG_README.md)
