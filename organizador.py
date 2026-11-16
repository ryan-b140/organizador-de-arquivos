#!/usr/bin/env python3
"""
Organizador Automático de Arquivos
----------------------------------
Separa os arquivos de uma pasta bagunçada (ex.: Downloads) em subpastas
por tipo: PDFs, Imagens, Planilhas, Documentos etc.

Uso:
    python organizador.py                    # organiza a pasta Downloads
    python organizador.py "C:/Caminho/Pasta" # organiza uma pasta específica
    python organizador.py --simular          # mostra o que seria feito
    python organizador.py --por-data         # cria subpastas Ano-Mês (2026-11)
    python organizador.py --desfazer         # desfaz a última organização
"""

import argparse
import json
import os
import shutil
from datetime import datetime

# Categorias e extensões correspondentes.
CATEGORIAS = {
    "PDFs": [".pdf"],
    "Imagens": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".heic"],
    "Planilhas": [".xls", ".xlsx", ".xlsm", ".csv", ".ods"],
    "Documentos": [".doc", ".docx", ".txt", ".odt", ".rtf", ".ppt", ".pptx", ".md"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv"],
    "Audios": [".mp3", ".wav", ".flac", ".ogg", ".m4a"],
    "Compactados": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Programas": [".exe", ".msi", ".dmg", ".deb", ".apk"],
}

PASTA_PADRAO = "Outros"
ARQUIVO_HISTORICO = ".organizador_historico.json"  # oculto, fica na pasta organizada


# ---------------------------------------------------------------- utilidades
def descobrir_categoria(nome_arquivo):
    """Retorna a categoria de um arquivo com base na extensão."""
    extensao = os.path.splitext(nome_arquivo)[1].lower()
    for categoria, extensoes in CATEGORIAS.items():
        if extensao in extensoes:
            return categoria
    return PASTA_PADRAO


def caminho_sem_conflito(destino):
    """Se já existir um arquivo com o mesmo nome, adiciona (1), (2)..."""
    if not os.path.exists(destino):
        return destino
    base, extensao = os.path.splitext(destino)
    contador = 1
    while os.path.exists(f"{base} ({contador}){extensao}"):
        contador += 1
    return f"{base} ({contador}){extensao}"


def carregar_historico(pasta):
    caminho = os.path.join(pasta, ARQUIVO_HISTORICO)
    if not os.path.isfile(caminho):
        return []
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def salvar_historico(pasta, historico):
    caminho = os.path.join(pasta, ARQUIVO_HISTORICO)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(historico, f, ensure_ascii=False, indent=2)


def remover_pastas_vazias(inicio, raiz):
    """Remove a pasta 'inicio' e suas pais (até 'raiz') se estiverem vazias."""
    atual = inicio
    while os.path.abspath(atual) != os.path.abspath(raiz):
        try:
            os.rmdir(atual)  # só funciona se estiver vazia
        except OSError:
            break
        atual = os.path.dirname(atual)


# ------------------------------------------------------------------ organizar
def organizar(pasta, simular=False, por_data=False):
    """Percorre a pasta e move cada arquivo para sua subpasta."""
    pasta = os.path.abspath(pasta)
    if not os.path.isdir(pasta):
        print(f"Erro: a pasta '{pasta}' não existe.")
        return

    movimentos = []
    resumo = {}

    for nome in os.listdir(pasta):
        origem = os.path.join(pasta, nome)

        # Ignora subpastas e arquivos ocultos (inclui o histórico)
        if not os.path.isfile(origem) or nome.startswith("."):
            continue

        categoria = descobrir_categoria(nome)
        subpasta = categoria
        if por_data:
            data = datetime.fromtimestamp(os.path.getmtime(origem))
            subpasta = os.path.join(categoria, data.strftime("%Y-%m"))

        pasta_destino = os.path.join(pasta, subpasta)
        destino = caminho_sem_conflito(os.path.join(pasta_destino, nome))

        if simular:
            print(f"[SIMULAÇÃO] {nome}  ->  {subpasta}/")
        else:
            os.makedirs(pasta_destino, exist_ok=True)
            try:
                shutil.move(origem, destino)
            except OSError as erro:
                print(f"Não foi possível mover '{nome}': {erro}")
                continue
            print(f"Movido: {nome}  ->  {subpasta}/")
            movimentos.append({"origem": origem, "destino": destino})

        resumo[categoria] = resumo.get(categoria, 0) + 1

    # Guarda no histórico para permitir desfazer
    if movimentos:
        historico = carregar_historico(pasta)
        historico.append(
            {"data": datetime.now().isoformat(timespec="seconds"), "movimentos": movimentos}
        )
        salvar_historico(pasta, historico)

    total = sum(resumo.values())
    print("\n" + "=" * 40)
    print(f"Total de arquivos {'que seriam movidos' if simular else 'movidos'}: {total}")
    for categoria, quantidade in sorted(resumo.items()):
        print(f"  {categoria}: {quantidade}")


# -------------------------------------------------------------------- desfazer
def desfazer(pasta, simular=False):
    """Desfaz a última organização feita nesta pasta."""
    pasta = os.path.abspath(pasta)
    historico = carregar_historico(pasta)

    if not historico:
        print("Nenhuma organização anterior encontrada para desfazer.")
        return

    ultima = historico.pop()
    print(f"Desfazendo a organização de {ultima['data']}...\n")
    devolvidos = 0

    for mov in reversed(ultima["movimentos"]):
        origem, destino = mov["origem"], mov["destino"]

        if not os.path.exists(destino):
            print(f"Ignorado (não encontrado): {destino}")
            continue

        volta = caminho_sem_conflito(origem)

        if simular:
            print(f"[SIMULAÇÃO] {os.path.basename(destino)}  ->  {os.path.dirname(volta)}")
        else:
            try:
                shutil.move(destino, volta)
            except OSError as erro:
                print(f"Não foi possível devolver '{destino}': {erro}")
                continue
            print(f"Devolvido: {os.path.basename(volta)}")
            remover_pastas_vazias(os.path.dirname(destino), pasta)

        devolvidos += 1

    if not simular:
        salvar_historico(pasta, historico)

    print(f"\nArquivos {'que seriam devolvidos' if simular else 'devolvidos'}: {devolvidos}")


# ------------------------------------------------------------------------ CLI
def main():
    pasta_downloads = os.path.join(os.path.expanduser("~"), "Downloads")

    parser = argparse.ArgumentParser(description="Organiza arquivos por tipo.")
    parser.add_argument("pasta", nargs="?", default=pasta_downloads,
                        help="Pasta a organizar (padrão: Downloads)")
    parser.add_argument("--simular", action="store_true",
                        help="Mostra o que seria feito, sem mover nada")
    parser.add_argument("--por-data", action="store_true",
                        help="Cria subpastas por Ano-Mês dentro de cada categoria")
    parser.add_argument("--desfazer", action="store_true",
                        help="Desfaz a última organização da pasta")
    args = parser.parse_args()

    print(f"Pasta: {args.pasta}\n")
    if args.desfazer:
        desfazer(args.pasta, simular=args.simular)
    else:
        organizar(args.pasta, simular=args.simular, por_data=args.por_data)


if __name__ == "__main__":
    main()
