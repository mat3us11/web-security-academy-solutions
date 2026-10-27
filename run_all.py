
import argparse
import csv
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

BASE = Path(__file__).resolve().parent
CSV_FILE = BASE / "labs_queue.csv"
LOG_DIR = BASE / "04-reports"
LOG_FILE = LOG_DIR / "executor.log"

FIELDS = ["script", "laboratorio", "url", "status"]

# Apenas mensagens explícitas de sucesso emitidas pelo script.
SUCCESS_PATTERNS = [
    r"\blab solved\b",
    r"\bsuccessfully solved\b",
    r"\blaboratory solved\b",
]

FAILURE_PATTERNS = [
    r"\bnot solved\b",
    r"\bfailed to solve\b",
    r"traceback \(most recent call last\)",
]


def log(message):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {message}"
    print(line)

    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(line + "\n")


def valid_lab_url(value):
    try:
        parsed = urlparse(value.strip())
        host = (parsed.hostname or "").lower()

        return (
            parsed.scheme == "https"
            and host.endswith(".web-security-academy.net")
            and host != "web-security-academy.net"
            and parsed.username is None
            and parsed.password is None
            and parsed.port in (None, 443)
        )
    except ValueError:
        return False


def resolve_script(value):
    candidate = (BASE / value).resolve()

    if not candidate.is_relative_to(BASE):
        raise ValueError("O script precisa estar dentro do repositório.")

    if not candidate.is_file() or candidate.suffix.lower() != ".py":
        raise ValueError(f"Script Python não encontrado: {value}")

    if candidate == Path(__file__).resolve():
        raise ValueError("O executor não pode executar a si mesmo.")

    return candidate


def load_queue():
    if not CSV_FILE.exists():
        with CSV_FILE.open(
            "w", newline="", encoding="utf-8-sig"
        ) as file:
            writer = csv.DictWriter(file, fieldnames=FIELDS)
            writer.writeheader()

        log(f"CSV criado: {CSV_FILE}")
        return []

    with CSV_FILE.open(
        "r", newline="", encoding="utf-8-sig"
    ) as file:
        reader = csv.DictReader(file)
        actual = set(reader.fieldnames or [])

        if not set(FIELDS).issubset(actual):
            raise ValueError(
                "Cabeçalho inválido no labs_queue.csv. "
                "Esperado: " + ", ".join(FIELDS)
            )

        return list(reader)


def save_queue(rows):
    with CSV_FILE.open(
        "w", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=FIELDS,
            extrasaction="ignore",
        )
        writer.writeheader()

        for row in rows:
            writer.writerow({
                key: row.get(key, "")
                for key in FIELDS
            })


def classify_output(output, returncode):
    for pattern in FAILURE_PATTERNS:
        if re.search(pattern, output, re.IGNORECASE):
            return "verificar"

    if returncode != 0:
        return "erro"

    for pattern in SUCCESS_PATTERNS:
        if re.search(pattern, output, re.IGNORECASE):
            # É apenas um indício; confirmar na Academy.
            return "verificar"

    return "verificar"


def run_one(row, timeout, retries, dry_run=False):
    script_name = row.get("script", "").strip()
    lab_name = row.get("laboratorio", "").strip()
    url = row.get("url", "").strip()

    log(f"Laboratório: {lab_name or script_name}")

    if not valid_lab_url(url):
        log(f"URL inválida ou não autorizada: {url or '(vazia)'}")
        return "erro"

    try:
        script = resolve_script(script_name)
    except (ValueError, OSError) as exc:
        log(f"Erro ao validar script: {exc}")
        return "erro"

    command = [sys.executable, str(script), url]
    log(f"Script: {script.relative_to(BASE)}")

    if dry_run:
        log("SIMULAÇÃO: nenhum script foi executado.")
        return "pendente"

    for attempt in range(retries + 1):
        log(f"Tentativa {attempt + 1} de {retries + 1}")

        try:
            result = subprocess.run(
                command,
                cwd=BASE,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                shell=False,
                check=False,
            )

            output = (result.stdout or "") + "\n" + (
                result.stderr or ""
            )

            for line in output.splitlines():
                log(line)

            log(f"Código de saída: {result.returncode}")

            status = classify_output(output, result.returncode)

            if status == "verificar":
                log(
                    "Confirme manualmente se a Academy marcou "
                    "o laboratório como resolvido."
                )
                return status

        except subprocess.TimeoutExpired:
            log(f"Tempo limite excedido: {timeout} segundos.")
            status = "erro"

        except OSError as exc:
            log(f"Não foi possível iniciar o script: {exc}")
            return "erro"

        if attempt < retries:
            log("Nova tentativa...")
            time.sleep(2)

    return status


def main():
    parser = argparse.ArgumentParser(
        description="Executor de scripts de laboratórios PortSwigger."
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=180,
        help="Tempo máximo por script, em segundos.",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=0,
        help="Tentativas extras em caso de erro (máximo 2).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Valida a fila sem executar scripts.",
    )
    args = parser.parse_args()

    if args.timeout < 1:
        parser.error("--timeout precisa ser maior que zero.")

    if not 0 <= args.retries <= 2:
        parser.error("--retries precisa estar entre 0 e 2.")

    try:
        rows = load_queue()
    except (OSError, ValueError, csv.Error) as exc:
        log(f"Não foi possível ler a fila: {exc}")
        sys.exit(1)

    if not rows:
        log("Nenhum laboratório cadastrado.")
        return

    processed = 0

    for row in rows:
        status = row.get("status", "").strip().lower()

        # Só processa registros explicitamente liberados.
        if status not in ("pendente", "erro"):
            continue

        processed += 1
        row["status"] = run_one(
            row,
            timeout=args.timeout,
            retries=args.retries,
            dry_run=args.dry_run,
        )

        try:
            save_queue(rows)
        except (OSError, csv.Error) as exc:
            log(f"Erro ao salvar CSV: {exc}")
            sys.exit(1)

    log(f"Processamento encerrado. Itens examinados: {processed}")
    log(f"Histórico: {LOG_FILE}")
    log("Verifique na Academy todos os itens com status 'verificar'.")


if __name__ == "__main__":
    main()
