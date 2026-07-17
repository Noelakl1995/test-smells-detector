import ast  # noqa: CPY001
import csv
import os



# ==========================================================
# CONFIGURAÇÕES
# ==========================================================

# Números comuns ignorados
IGNORE_NUMBERS = {
    0,
    1,
    -1,
    2,
    -2,
    0.0,
    1.0,
    -1.0,
    2.0,
    -2.0,
    True,
    False,
}

# Funções de assert conhecidas
ASSERT_FUNCTIONS = {
    "assert_array_equal",
    "assert_allclose",
    "assert_almost_equal",
    "assert_array_almost_equal",
    "assert_equal",
    "assert_raises",
    "raises",
    "approx",
    "assert_warns",
    "assert_no_warnings",
}

# Chamadas irrelevantes para Eager Test
IGNORE_CALLS = {
    "array",
    "reshape",
    "astype",
    "sum",
    "len",
    "append",
    "all",
    "any",
    "isfinite",
    "copy",
    "deepcopy",
    "seed",
    "rand",
    "randn",
    "zeros",
    "ones",
    "empty",
    "tolist",
    "item",
    "assert_array_equal",
    "assert_allclose",
    "assert_almost_equal",
    "assert_array_almost_equal",
    "assert_equal",
}

# Ações relevantes para detectar Eager Test
RELEVANT_ACTIONS = {
    "fit",
    "predict",
    "predict_proba",
    "score",
    "transform",
    "fit_transform",
    "inverse_transform",
    "export_graphviz",
    "export_text",
    "plot_tree",
    "apply",
    "decision_path",
    "end_run",
    "log_model",
    "load_model",
    "register_model",
    "start_runs",
    "log_metric",
    "log_param",
}

# Possíveis Mystery Guests
MYSTERY_GUEST_FUNCTIONS = {
    "open",
    "read_csv",
    "read_excel",
    "loadtxt",
    "connect",
    "fetchrequest.get",
    "request.post",
    "load_iris",
    "load_diabetes",
    "read_json",
    "load_dataset",
}


# ações relevantes para flaky test
FLAKY_FUNCTIONS = {
    "sleep",
    "randint",
    "random",
    "choice",
    "shuffle",
}


# Funções relacionadas a mocks
MOCK_FUNCTIONS = {
    "Mock",
    "MagicMock",
    "patch",
}

results = []


fixtures = {}

# ==========================================================
# FUNÇÃO AUXILIAR
# ==========================================================


def is_fixture(node):
    """
    Verifica se uma função possui o decorador
    @pytest.fixture ou @fixture
    """

    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Attribute):
            if decorator.attr == "fixture":
                return True

        elif isinstance(decorator, ast.Name):
            if decorator.id == "fixture":
                return True

    return False


def count_fixture_resources(fixture_node):
    """
    Conta quantos elementos são retornados pela fixture.
    """

    for child in ast.walk(fixture_node):
        if isinstance(child, ast.Return):
            if isinstance(child.value, ast.Tuple):
                return len(child.value.elts)

            return 1

    return 0


def get_function_name(call_node):

    if isinstance(call_node.func, ast.Name):
        return call_node.func.id

    if isinstance(call_node.func, ast.Attribute):
        return call_node.func.attr

    return None


# ==========================================================
# ANÁLISE
# ==========================================================

from pathlib import Path


def analyze_test_function(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    file_name: str,
    fixtures: dict,
) -> list:
    """Extrai métricas e smells de uma função de teste."""

    eager_actions = set()

    mystery_guest_detected = False
    general_fixture_detected = False
    flaky_test_detected = False

    test_size = (
        node.end_lineno - node.lineno + 1
    )

    assert_count = 0
    call_count = 0
    variable_count = 0
    fixture_count = len(node.args.args)
    undocumented_asserts = 0
    external_resource_count = 0
    constructor_count = 0
    mock_count = 0

    asserted_variables = set()

    for child in ast.walk(node):
        if isinstance(
            child,
            (
                ast.If,
                ast.For,
                ast.AsyncFor,
                ast.While,
                ast.Try,
                ast.With,
                ast.AsyncWith,
                ast.IfExp,
            ),
        ):
            constructor_count += 1

        if isinstance(
            child,
            (
                ast.Assign,
                ast.AnnAssign,
                ast.AugAssign,
            ),
        ):
            variable_count += 1

        if isinstance(child, ast.Assert):
            assert_count += 1

            if child.msg is None:
                undocumented_asserts += 1

            for subchild in ast.walk(child):
                if isinstance(subchild, ast.Name):
                    asserted_variables.add(
                        subchild.id
                    )

        if isinstance(
            child,
            (
                ast.With,
                ast.AsyncWith,
            ),
        ):
            for item in child.items:
                context = item.context_expr

                if isinstance(context, ast.Call):
                    function_name = get_function_name(
                        context
                    )

                    if function_name == "raises":
                        assert_count += 1
                        undocumented_asserts += 1

        if not isinstance(child, ast.Call):
            continue

        call_count += 1
        function_name = get_function_name(child)

        if not function_name:
            continue

        if function_name in ASSERT_FUNCTIONS:
            assert_count += 1
            undocumented_asserts += 1

        if function_name in RELEVANT_ACTIONS:
            eager_actions.add(function_name)

        if function_name in MYSTERY_GUEST_FUNCTIONS:
            mystery_guest_detected = True
            external_resource_count += 1

        if function_name in FLAKY_FUNCTIONS:
            flaky_test_detected = True

        if function_name in MOCK_FUNCTIONS:
            mock_count += 1

    general_fixture_detected = (
        detect_general_fixture(
            node=node,
            fixtures=fixtures,
        )
    )

    detected_smells = []

    if assert_count == 0:
        detected_smells.append("Unknown Test")

    if undocumented_asserts >= 3:
        detected_smells.append(
            "Assertion Roulette"
        )

    if len(eager_actions) >= 3:
        detected_smells.append("Eager Test")

    if mystery_guest_detected:
        detected_smells.append("Mystery Guest")

    if general_fixture_detected:
        detected_smells.append(
            "General Fixture"
        )

    if flaky_test_detected:
        detected_smells.append("Flaky Test")

    asserted_variables_count = len(
        asserted_variables
    )

    cyclomatic_complexity = (
        constructor_count + 1
    )

    return [
        node.name,
        file_name,
        test_size,
        assert_count,
        undocumented_asserts,
        call_count,
        variable_count,
        fixture_count,
        external_resource_count,
        constructor_count,
        mock_count,
        asserted_variables_count,
        cyclomatic_complexity,
        int(
            "Assertion Roulette"
            in detected_smells
        ),
        int("Eager Test" in detected_smells),
        int(
            "Mystery Guest"
            in detected_smells
        ),
        int(
            "General Fixture"
            in detected_smells
        ),
        int("Flaky Test" in detected_smells),
        int("Unknown Test" in detected_smells),
    ]

def detect_general_fixture(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    fixtures: dict,
) -> bool:
    """Verifica o uso parcial de recursos de fixtures."""

    for arg in node.args.args:
        fixture_name = arg.arg

        if fixture_name not in fixtures:
            continue

        fixture_node = fixtures[fixture_name]

        total_resources = count_fixture_resources(
            fixture_node
        )

        if total_resources < 2:
            continue

        used_resources = 0

        for child in ast.walk(node):
            if not isinstance(child, ast.Assign):
                continue

            if not isinstance(
                child.value,
                ast.Name,
            ):
                continue

            if child.value.id != fixture_name:
                continue

            if len(child.targets) != 1:
                continue

            target = child.targets[0]

            if not isinstance(target, ast.Tuple):
                continue

            for element in target.elts:
                if (
                    isinstance(element, ast.Name)
                    and element.id != "_"
                ):
                    used_resources += 1

        if (
            used_resources > 0
            and used_resources < total_resources
        ):
            return True

    return False



def analyze_project(
    test_folder: str,
    project_name: str,
    output_file: str,
) -> int:
    """
    Analisa os testes Python de um projeto e gera um arquivo CSV.

    Retorna a quantidade de funções de teste analisadas.
    """

    test_path = Path(test_folder)

    if not test_path.exists():
        raise FileNotFoundError(
            f"A pasta informada não existe: {test_folder}"
        )

    if not test_path.is_dir():
        raise NotADirectoryError(
            f"O caminho informado não é uma pasta: {test_folder}"
        )

    results = []

    for root, _, files in os.walk(test_path):
        for file in files:
            if not (
                file.startswith("test")
                and file.endswith(".py")
            ):
                continue

            full_path = Path(root) / file

            try:
                source = full_path.read_text(
                    encoding="utf-8"
                )
                tree = ast.parse(
                    source,
                    filename=str(full_path),
                )
            except UnicodeDecodeError as error:
                print(
                    f"[AVISO] Não foi possível ler "
                    f"{full_path}: {error}"
                )
                continue
            except SyntaxError as error:
                print(
                    f"[AVISO] Erro de sintaxe em "
                    f"{full_path}: {error}"
                )
                continue
            except OSError as error:
                print(
                    f"[AVISO] Erro ao abrir "
                    f"{full_path}: {error}"
                )
                continue

            # As fixtures devem ser identificadas por arquivo.
            fixtures = {}

            for node in ast.walk(tree):
                if (
                    isinstance(
                        node,
                        (
                            ast.FunctionDef,
                            ast.AsyncFunctionDef,
                        ),
                    )
                    and is_fixture(node)
                ):
                    fixtures[node.name] = node

            print(f"Analisando: {full_path}")

            for node in ast.walk(tree):
                if not isinstance(
                    node,
                    (
                        ast.FunctionDef,
                        ast.AsyncFunctionDef,
                    ),
                ):
                    continue

                if not node.name.startswith("test"):
                    continue

                result = analyze_test_function(
                    node=node,
                    file_name=file,
                    fixtures=fixtures,
                )

                results.append(result)

    output_path = Path(output_file)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    header = [
        "dataset",
        "test_name",
        "file",
        "test_size",
        "assert_count",
        "undocumented_asserts",
        "call_count",
        "variable_count",
        "fixture_count",
        "external_resource_count",
        "constructor_count",
        "mock_count",
        "asserted_variables_count",
        "cyclomatic_complexity",
        "assertion_roulette",
        "eager_test",
        "mystery_guest",
        "general_fixture",
        "flaky_test",
        "unknown_test",
    ]

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)

        for result in results:
            writer.writerow(
                [project_name] + result
            )

    print(
        f"\nAnálise concluída: "
        f"{len(results)} funções de teste."
    )
    print(f"CSV gerado em: {output_path}")

    return len(results)
