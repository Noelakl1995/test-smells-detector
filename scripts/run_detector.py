import argparse
import sys
from pathlib import Path


# Permite executar o script diretamente:
# python scripts/run_detector.py ...
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from detector.analyzer import analyze_project


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Detecta test smells em arquivos "
            "de teste de projetos Python."
        )
    )

    parser.add_argument(
        "project_path",
        help=(
            "Caminho da pasta que contém "
            "os arquivos de teste."
        ),
    )

    parser.add_argument(
        "--name",
        required=True,
        help=(
            "Nome do projeto ou dataset, "
            "por exemplo: MLflow."
        ),
    )

    parser.add_argument(
        "--output",
        help=(
            "Caminho do CSV de saída. "
            "Quando omitido, o arquivo será "
            "salvo na pasta results."
        ),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    project_name = args.name.strip()

    if args.output:
        output_file = args.output
    else:
        safe_name = (
            project_name
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
        )

        output_file = (
            PROJECT_ROOT
            / "results"
            / f"{safe_name}_test_smells.csv"
        )

    try:
        analyze_project(
            test_folder=args.project_path,
            project_name=project_name,
            output_file=str(output_file),
        )
    except (
        FileNotFoundError,
        NotADirectoryError,
        PermissionError,
    ) as error:
        print(f"Erro: {error}")
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()