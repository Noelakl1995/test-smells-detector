# test-smells-detector
Ferramenta baseada em AST para detecção de test smells em projetos Python de Machine Learning.
# Detector de Test Smells para Projetos de Machine Learning em Python

Este repositório contém a implementação da ferramenta desenvolvida no Trabalho de Conclusão de Curso (TCC) da Universidade Federal de Campina Grande (UFCG).

A ferramenta realiza a identificação automática de **test smells** em projetos Python por meio de análise estática baseada na **Árvore Sintática Abstrata (Abstract Syntax Tree – AST)**.

Os seguintes *test smells* são detectados:

- Assertion Roulette
- Eager Test
- Mystery Guest
- General Fixture
- Flaky Test

Além da detecção dos *test smells*, a ferramenta extrai métricas estruturais dos testes, utilizadas nas análises apresentadas no trabalho.

---

# Estrutura do projeto

```
test-smells-detector/
│
├── detector/          # Código principal do detector
├── scripts/           # Scripts de execução
├── notebooks/         # Análises e geração dos gráficos
├── results/           # Arquivos CSV produzidos
├── figures/           # Figuras utilizadas no TCC
├── requirements.txt
└── README.md
```

---

# Requisitos

- Python 3.10 ou superior

Instale as dependências:

```bash
pip install -r requirements.txt
```

---

# Como executar

Execute o detector informando a pasta que contém os testes do projeto.

```bash
python scripts/run_detector.py CAMINHO_DO_PROJETO --name NOME_DO_PROJETO
```

### Exemplo (MLflow)

```bash
python scripts/run_detector.py "C:\Users\elino\Downloads\mlflow\mlflow\tests" --name MLflow
```

### Exemplo (Scikit-learn)

```bash
python scripts/run_detector.py "C:\Users\elino\Downloads\scikit-learn\sklearn" --name Scikit-learn
```

---

# Saída

A ferramenta gera um arquivo CSV contendo, para cada função de teste:

- projeto analisado;
- nome da função de teste;
- arquivo de origem;
- métricas estruturais extraídas;
- *test smells* identificados.

Exemplo de colunas produzidas:

```
dataset
test_name
file
test_size
assert_count
call_count
variable_count
fixture_count
cyclomatic_complexity
assertion_roulette
eager_test
mystery_guest
general_fixture
flaky_test
```

---

# Reprodução dos experimentos

Os scripts utilizados para reproduzir os experimentos apresentados no TCC encontram-se nas pastas:

- `scripts/`
- `notebooks/`

Eles permitem gerar:

- estatísticas descritivas;
- tabelas apresentadas no trabalho;
- heatmaps;
- gráficos utilizados na análise dos resultados.

---

# Limitações

A ferramenta utiliza **análise estática baseada em AST**.

Consequentemente, alguns *test smells* (principalmente **Flaky Test**) são identificados por meio de heurísticas e os resultados devem ser interpretados como **indicativos**, podendo exigir inspeção manual.

---

# Trabalho associado

Este repositório acompanha o Trabalho de Conclusão de Curso:

**Identificação de Test Smells em Projetos de Machine Learning utilizando Análise Estática baseada em AST**

Universidade Federal de Campina Grande (UFCG)

---

# Autor

**Dagbegnon Noel Aklou**

Curso de Ciência da Computação

Universidade Federal de Campina Grande (UFCG)

---

# Licença

Este projeto está disponível sob a licença MIT.


