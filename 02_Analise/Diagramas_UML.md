# 4. Diagramas UML

## Diagrama de Classes (modelo de domínio)
As estratégias de cálculo são implementadas como funções registradas em `CALCULADORES` (módulo `regras.py`);
no diagrama aparecem como classes para representar o padrão **Strategy** (RNF004).

```mermaid
classDiagram
    class Colaborador {
        +int matricula
        +String nome
        +Date dataNascimento
        +Date dataInicioContrato
        +Date dataFimContrato
        +int nivelAcesso
        +String status
        +String tipo
        +int salarioBaseCentavos
        +desabilitar()
        +reativar()
    }
    class Periodo {
        +int ano
        +int mes
        +String status
        +fechar()
    }
    class Folha {
        +int meta
        +int vendasCentavos
        +int quantidadeProduzida
        +int adicionaisCentavos
        +int totalCentavos
        +calcular()
    }
    class CalculoRemuneracao {
        <<interface>>
        +calcular(dados) Resultado
    }
    class CalculoPadrao
    class CalculoComissionado
    class CalculoProducao
    Colaborador "1" --> "*" Folha : possui
    Periodo "1" --> "*" Folha : contem
    Folha ..> CalculoRemuneracao : usa
    CalculoRemuneracao <|.. CalculoPadrao
    CalculoRemuneracao <|.. CalculoComissionado
    CalculoRemuneracao <|.. CalculoProducao
```

## Diagrama de Sequência – Cadastro de colaborador
```mermaid
sequenceDiagram
    actor RH as Administrador RH
    participant UI as Interface Web
    participant S as Sistema Flask
    participant B as Banco SQLite
    RH->>UI: Preenche e confirma o cadastro
    UI->>S: POST colaboradores novo
    S->>S: Valida autorizacao nivel 1 e dados
    S->>B: INSERT colaborador com senha em hash
    B-->>S: Matricula gerada
    S-->>UI: Redireciona com mensagem de sucesso
    UI-->>RH: Lista com o novo colaborador
```

## Diagrama de Sequência – Geração, lançamento e fechamento da folha
```mermaid
sequenceDiagram
    actor RH as Administrador RH
    participant S as Sistema Flask
    participant R as Regras de calculo
    participant B as Banco SQLite
    RH->>S: Gerar folha do mes
    S->>B: Busca colaboradores com contrato no mes
    loop Para cada colaborador
        S->>B: Busca folha do mes anterior
        S->>R: Define a meta do mes
        S->>R: Calcula remuneracao
        S->>B: INSERT folha
    end
    S-->>RH: Folha aberta com total
    RH->>S: Lanca vendas e producao
    S->>R: Recalcula cada folha
    S->>B: UPDATE folha
    RH->>S: Fechar mes
    S->>B: UPDATE periodo para FECHADO
    S-->>RH: Folha congelada
```

## Diagrama de Sequência – Acesso negado ao nível 3
```mermaid
sequenceDiagram
    actor C as Colaborador nivel 3
    participant S as Sistema Flask
    participant B as Banco SQLite
    C->>S: GET folha com id de outra pessoa
    S->>B: Busca a folha pelo id
    B-->>S: Folha de outro colaborador
    S->>S: Matricula da sessao difere da folha
    S-->>C: 403 Acesso negado sem dados
```

## Modelo de Dados (ER)
```mermaid
erDiagram
    COLABORADOR ||--o{ FOLHA : possui
    PERIODO ||--o{ FOLHA : contem
    COLABORADOR {
        int matricula PK
        string nome
        string data_nascimento
        string data_inicio_contrato
        string data_fim_contrato
        int nivel_acesso
        string status
        string senha_hash
        string tipo
        int salario_base_centavos
        int percentual_comissao_bp
        int valor_unidade_centavos
    }
    PERIODO {
        int id PK
        int ano
        int mes
        string status
    }
    FOLHA {
        int id PK
        int periodo_id FK
        int matricula FK
        int meta
        int vendas_centavos
        int quantidade_produzida
        int adicionais_centavos
        int total_centavos
    }
```

## Diagrama de Estados – Período da folha
```mermaid
stateDiagram-v2
    [*] --> ABERTO : gerar folha
    ABERTO --> ABERTO : lancar vendas e producao
    ABERTO --> FECHADO : fechar mes
    FECHADO --> [*]
```
