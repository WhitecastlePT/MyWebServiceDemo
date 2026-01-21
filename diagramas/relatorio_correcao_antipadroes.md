# Relatório de Correção de Anti-Padrões

**Projeto:** Dia & Noite: O Mundo dos Animais  
**Autor:** Henrique Crachat (2501450)  
**Data:** 2026-01-08  
**Tipo:** Refatoração — Correção de Anti-Padrões  
**Compatibilidade:** 100% mantida com a API e com os padrões **Factory Method**, **Decorator** e **Observer**.

---

## Visão geral do que foi feito

Foram identificados **7 anti-padrões**. Destes, **4 foram corrigidos e implementados**, e **3 ficaram com design técnico completo para implementação futura**.

### Corrigidos (implementação completa)
1. Singleton Abuse / Global State (crítico)  
2. Circular Imports (moderado)  
3. Magic Numbers (crítico)  
4. Print Debugging (moderado)

### Com design técnico pronto (não implementado)
5. God Class — `CognitiveAnalytics` (moderado)  
6. Tight Coupling Between Observers (moderado)  
7. In-Memory Data Storage (crítico)

---

## 1) Singleton Abuse / Global State

### Antes (o que existia)
- `CognitiveAnalytics` e vários observers eram criados como **globais**.
- Endpoints dependiam de variáveis globais e de `global ...` dentro de `register_cognitive_routes()`.
- Anexar observers era feito por uma função separada (`attach_observers_to_challenge()`).

**Problemas principais**
- Testes unitários não isolados (estado partilhado).
- Risco em concorrência / multi-instância (thread-unsafe, sem multi-tenancy).
- Dependências implícitas e acoplamento.

### Depois (o que foi alterado)
**Solução:** Dependency Injection via **`ObserversContainer`**.

**Criado**
- `cognitive_module/observers_container.py` (novo): encapsula `CognitiveAnalytics` e todos os observers; centraliza dependências; inclui método para anexar observers ao challenge.

**Modificado**
- `cognitive_module/cognitive_endpoints.py`:
  - `register_cognitive_routes(app, observers_container=None)` passa a aceitar container opcional.
  - Se não for fornecido, cria um container automaticamente.
  - Removeu globais e atualizou referências para usar `observers.<observer>`.

**Resultado**
- Dependências explícitas.
- Testabilidade e isolamento por instância melhorados.
- API externa preservada: `register_cognitive_routes(app)` continua a funcionar.

---

## 2) Circular Imports

### Antes (o que existia)
- Imports eram feitos **dentro dos `__init__()`** dos challenges para “fugir” a imports circulares (ex.: `from data.animals_data import ...` dentro do construtor).

**Problemas principais**
- Overhead em runtime (import repetido).
- IDE/linters perdem análise estática.
- Arquitetura de dependências pior.

### Depois (o que foi alterado)
**Solução:** mover imports para o topo e usar acesso por módulo.

**Modificados**
- `models/audio_challenge.py`
- `models/visual_challenge.py`
- `models/habitat_challenge.py`
- `models/classification_challenge.py`

**Mudanças**
- `from data import animals_data` no topo.
- Remoção dos imports dentro de `__init__()`.
- Uso de `animals_data.get_animal_data(...)`, `animals_data.HABITATS`, etc.

**Resultado**
- Imports executados uma vez (load do módulo).
- Melhor refactoring, tipagem e manutenção.
- Interface/Factory Method mantidos.

---

## 3) Magic Numbers

### Antes (o que existia)
- Thresholds e valores de XP/pontos/níveis hardcoded em:
  - `cognitive_module/cognitive_analytics.py`
  - `observers/level_progression_observer.py`

**Problemas principais**
- Balanceamento difícil (alterar números = alterar lógica).
- Sem “fonte única de verdade”.
- Pouca documentação do significado.

### Depois (o que foi alterado)
**Solução:** Configuração centralizada.

**Criados**
- `config/__init__.py` (novo)
- `config/game_settings.py` (novo): centraliza regras de:
  - níveis (thresholds)
  - pontos (bónus por tempo)
  - XP (multiplicadores, bónus, níveis)

**Modificados**
- `cognitive_module/cognitive_analytics.py`: passou a usar `LevelSettings.calculate_level(...)`.
- `observers/level_progression_observer.py`: passou a usar `XPSettings` (constantes e cálculos).

**Resultado**
- Valores consolidados num só local.
- Mais configurável e testável.
- Mantém os mesmos resultados lógicos (mudou “onde”, não “o quê”).

---

## 4) Print Debugging

### Antes (o que existia)
- Uso de `print()` em vários pontos (com foco evidenciado em `observers/analytics_observer.py`).
- Output não controlável por ambiente e sem níveis (DEBUG/INFO/ERROR).

### Depois (o que foi alterado)
**Solução:** logging centralizado.

**Criados**
- `utils/__init__.py` (novo)
- `utils/logger.py` (novo): `setup_logging(...)` e `get_logger(name)` com configuração padrão.

**Modificados**
- `observers/analytics_observer.py`: substituiu `print()` por `logger.debug/info(...)`.
- `cognitive_module/observers_container.py`: ajuste para evitar import circular (imports movidos para dentro do `__init__()` do container).

**Resultado**
- Logs com timestamps, níveis e nome do módulo.
- Possibilidade de controlar verbosidade e redirecionar para ficheiro.
- Mantém output no console, agora estruturado.

**Nota**
- Existem outros ficheiros ainda com prints, listados como “por corrigir” (achievement/invenira/level_progression + demos).

---

## Impacto nos padrões de design

- **Factory Method:** intacto (apenas reorganização de imports).
- **Decorator:** intacto (nenhuma alteração de interface).
- **Observer:** intacto e melhorado:
  - observers agora são injetados via container (mais testável).
  - logging profissional substitui prints.

---

## Resumo de ficheiros (o que mudou)

### Criados (5)
- `cognitive_module/observers_container.py` — container para DI de observers  
- `config/__init__.py` — exports/config  
- `config/game_settings.py` — settings centralizadas (níveis, XP, pontos)  
- `utils/__init__.py` — exports utils  
- `utils/logger.py` — logging centralizado  

### Modificados (9)
- `cognitive_module/cognitive_endpoints.py` — remove globais, DI, refs atualizadas  
- `cognitive_module/cognitive_analytics.py` — usa settings (remove magic numbers)  
- `observers/level_progression_observer.py` — usa settings (remove magic numbers)  
- `observers/analytics_observer.py` — troca prints por logger  
- `cognitive_module/observers_container.py` — ajuste de imports para evitar circular  
- `models/audio_challenge.py` — imports reorganizados  
- `models/visual_challenge.py` — imports reorganizados  
- `models/habitat_challenge.py` — imports reorganizados  
- `models/classification_challenge.py` — imports reorganizados  

---

## Anti-padrões com design técnico pronto (não implementados)

### 1) God Class — `CognitiveAnalytics`
**Antes:** classe concentrava persistência + cálculos + recomendações + export.  
**Proposto:** separar em componentes coesos (ex.: repository + calculators + service) mantendo a mesma API externa.

### 2) In-Memory Data Storage
**Antes:** dados em dicionários em memória, perdidos ao reiniciar e sem escala horizontal.  
**Proposto:** Repository Pattern com SQLAlchemy + tabelas para progresso e histórico; migração gradual (SQLite → Postgres).

### 3) Tight Coupling Between Observers
**Antes:** `LevelProgressionObserver` chamava `InveniraObserver` diretamente.  
**Proposto:** Event Bus / Mediator para publicar “level_up” e outros eventos; observers passam a subscrever eventos, eliminando dependências diretas.

---

## Conclusão

- **4 anti-padrões corrigidos** com implementação efetiva.
- **3 anti-padrões restantes** documentados com arquitetura e plano de implementação.
- **Compatibilidade total** preservada e padrões de design mantidos.
- Projeto ficou mais **testável**, **configurável**, **manutenível** e com **logging profissional**.
