
import csv
import re
from pathlib import Path
from urllib.parse import urlparse

BASE = Path(__file__).resolve().parent
CSV_FILE = BASE / "labs_queue.csv"

FIELDS = ["script", "laboratorio", "url", "status"]

IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "04-reports",
}


def log(message):
    print(message)


def valid_lab_url(url):
    try:
        parsed = urlparse((url or "").strip())
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


def read_existing_queue():
    """Lê a fila atual para preservar URLs e estados existentes."""
    if not CSV_FILE.exists():
        return {}

    with CSV_FILE.open(
        "r", newline="", encoding="utf-8-sig"
    ) as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            return {}

        required = {"script", "url", "status"}
        if not required.issubset(set(reader.fieldnames)):
            raise ValueError(
                "O CSV atual não possui as colunas necessárias. "
                "Faça uma cópia de segurança antes de recriá-lo."
            )

        existing = {}

        for row in reader:
            script = (row.get("script") or "").strip().replace("\\", "/")
            if not script:
                continue

            existing[script] = {
                "script": script,
                "laboratorio": (row.get("laboratorio") or "").strip(),
                "url": (row.get("url") or "").strip(),
                "status": (row.get("status") or "").strip(),
            }

        return existing


def get_lab_title(guide, script):
    """Obtém o título do laboratório a partir do Markdown."""
    try:
        content = guide.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError):
        return script.stem

    # Procura o primeiro título Markdown.
    match = re.search(r"(?m)^#\s+(.+?)\s*#*\s*$", content)

    if match:
        return match.group(1).strip()

    # Usa o nome do arquivo se não houver título.
    return script.stem


def discover_scripts():
    """Localiza scripts que possuem um guia Markdown correspondente."""
    found = []

    for script in BASE.rglob("*.py"):
        relative = script.relative_to(BASE)

        if any(part.lower() in IGNORED_DIRS for part in relative.parts):
            continue

        if script == Path(__file__).resolve():
            continue

        if script.stem == "run_all":
            continue

        guide = script.with_suffix(".md")

        # Só inclui scripts documentados.
        if not guide.is_file():
            continue

        found.append({
            "script": relative.as_posix(),
            "laboratorio": get_lab_title(guide, script),
        })

    return sorted(found, key=lambda item: item["script"].lower())


def generate_queue():
    previous = read_existing_queue()
    discovered = discover_scripts()

    if not discovered:
        log("Nenhum par de arquivos .py e .md foi encontrado.")
        return

    rows = []
    preserved_urls = 0
    waiting_urls = 0
    new_entries = 0
    invalid_urls = 0

    for lab in discovered:
        key = lab["script"]
        old = previous.get(key)

        if old is None:
            url = ""
            status = "aguardando_url"
            new_entries += 1
        else:
            url = old["url"]
            status = old["status"] or "aguardando_url"

            if url:
                preserved_urls += 1

        if not url:
            status = "aguardando_url"
            waiting_urls += 1
        elif not valid_lab_url(url):
            status = "erro"
            invalid_urls += 1
        elif status == "aguardando_url":
            # Não libera a execução automaticamente.
            status = "aguardando_confirmacao"

        rows.append({
            "script": key,
            "laboratorio": lab["laboratorio"],
            "url": url,
            "status": status,
        })

    # Grava a fila completa em um arquivo temporário primeiro.
    temp_file = CSV_FILE.with_suffix(".tmp")

    with temp_file.open(
        "w", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    temp_file.replace(CSV_FILE)

    log("")
    log("Fila atualizada com sucesso!")
    log(f"Total de scripts documentados: {len(rows)}")
    log(f"Novos registros: {new_entries}")
    log(f"URLs preservadas: {preserved_urls}")
    log(f"Sem URL: {waiting_urls}")
    log(f"URLs inválidas: {invalid_urls}")
    log(f"Arquivo: {CSV_FILE}")
    log("")
    log("Os registros não são executados pelo gerador.")
    log("Confira o CSV antes de liberar qualquer laboratório.")


if __name__ == "__main__":
    try:
        generate_queue()
    except (OSError, csv.Error, ValueError) as exc:
        log(f"ERRO: {exc}")
        raise SystemExit(1)
