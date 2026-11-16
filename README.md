# Organizador Automático de Arquivos

Script em Python que organiza uma pasta bagunçada, como a pasta Downloads, separando os arquivos em subpastas por tipo.

## Requisitos

- Python 3.8 ou superior (nenhuma instalação extra)

## Uso

```bash
python organizador.py                      # organiza a pasta Downloads
python organizador.py "C:/Caminho/Pasta"   # organiza outra pasta
python organizador.py --simular            # só mostra o que seria feito
python organizador.py --por-data           # Imagens/2026-11, PDFs/2026-10...
python organizador.py --desfazer           # desfaz a última organização
```

## Recursos

- Categorias: PDFs, Imagens, Planilhas, Documentos, Videos, Audios, Compactados, Programas e Outros
- Modo de simulação, sem mover nada
- Nomes duplicados viram `arquivo (1).pdf`, sem sobrescrever
- Histórico das movimentações e comando para desfazer
- Opção de subpastas por data (Ano-Mês)

## Personalização

Edite o dicionário `CATEGORIAS` em `organizador.py` para adicionar ou mudar extensões.
