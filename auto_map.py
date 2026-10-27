import csv
import urllib.request
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
CSV_FILE = BASE / "labs_queue.csv"

def main():
    print("=== Auto-Mapeador de Laboratórios PortSwigger ===")
    print("Cole as URLs das instâncias abaixo (uma por linha).")
    print("Pressione Enter em uma linha vazia para finalizar e processar:\n")
    
    urls_recebidas = []
    while True:
        try:
            linha = input().strip()
            if not linha:
                break
            urls_recebidas.append(linha)
        except EOFError:
            break

    if not urls_recebidas:
        print("Nenhuma URL informada. Encerrando.")
        return

    if not CSV_FILE.exists():
        print(f"Erro: O arquivo {CSV_FILE} não foi encontrado. Execute o gerador de CSV primeiro.")
        return

    # Carrega o CSV atual
    with CSV_FILE.open("r", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    atualizados = 0

    print("\nProcessando URLs...")
    for url in urls_recebidas:
        try:
            # Faz uma requisição rápida na URL da instância para ler o título da página
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=8) as response:
                html = response.read().decode('utf-8', errors='ignore')
            
            # Extrai o título da página da PortSwigger
            match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE)
            if match:
                titulo_pagina = match.group(1)
                # Limpa o título para extrair o nome do laboratório
                lab_nome = titulo_pagina.split("-")[0].replace("Lab:", "").strip()
                
                # Procura no CSV qual linha bate com esse nome de laboratório
                encontrou = False
                for row in rows:
                    if lab_nome.lower() in row["laboratorio"].lower():
                        row["url"] = url
                        row["status"] = "pendente"
                        print(f"  [+] Vinculado: '{row['laboratorio']}' -> {url}")
                        atualizados += 1
                        encontrou = True
                        break
                if not encontrou:
                    print(f"  [-] Laboratório não encontrado na fila para o título: {lab_nome}")
            else:
                print(f"  [!] Não foi possível encontrar a tag <title> na URL: {url}")
        except Exception as e:
            print(f"  [!] Erro ao acessar a URL {url}: {e}")

    # Salva de volta no CSV mantendo o formato correto
    fieldnames = list(rows[0].keys()) if rows else ["script", "laboratorio", "url", "status"]
    with CSV_FILE.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nProcesso concluído! {atualizados} laboratório(s) mapeado(s) e marcado(s) como 'pendente'.")
    print("Agora você já pode rodar: python .\\run_all.py")

if __name__ == "__main__":
    main()