# danfse-nt008

Biblioteca Python para gerar o DANFSe a partir do XML nacional da NFS-e, seguindo a Nota Tecnica No 008 SE/CGNFS-e de 05/05/2026.

> Alerta
> Esta implementacao foi escrita seguindo a documentacao oficial da NT 008:
> https://www.gov.br/nfse/pt-br/biblioteca/documentacao-tecnica/rtc/nt-008-se-cgnfse-danfse-20260505.pdf
>
> O PDF e os campos foram validados por implementacao local e testes da biblioteca, mas esta versao ainda nao foi homologada em um validador oficial externo.

O objetivo do projeto e reproduzir o DANFSe com os caminhos XML, descricoes, medidas, fontes e regras de supressao definidos na NT 008. A biblioteca nao inventa valores: quando uma tag exigida para um campo nao existe no XML, o campo e preenchido com `-`, conforme a nota 12 da tabela 2.4.5.

## Licenca

Este projeto e publicado com uma licenca de uso propria, incluida em [LICENSE](LICENSE).

Uso comercial exige mencao visivel de que o produto, servico ou distribuicao utiliza `danfse-nt008`.

## Requisitos

- Python 3.10+
- `uv`
- WeasyPrint
- `qrcode[pil]`
- No Windows, runtime nativo do WeasyPrint via MSYS2
- Fontes Arial e Microsoft Sans Serif instaladas no sistema

## Instalacao

### 1. Instale o Python

Use Python 3.10 ou superior.

### 2. Instale o `uv`

```powershell
pip install uv
```

### 3. Instale o runtime do WeasyPrint no Windows

Instale o MSYS2 e depois rode:

```powershell
pacman -S --noconfirm mingw-w64-x86_64-pango
```

O pacote carrega por padrao o diretorio:

```text
C:\msys64\mingw64\bin
```

Se o MSYS2 estiver em outro caminho, defina `WEASYPRINT_DLL_DIRECTORIES` apontando para o `mingw64\\bin`.

### 4. Instale as dependencias da biblioteca

```powershell
cd "C:\caminho\para\danfse-nt008"
uv sync
```

## Uso rapido

Gerar PDF:

```powershell
uv run danfse-nt008 xml.xml --output danfse.pdf
```

Gerar HTML:

```powershell
uv run danfse-nt008 xml.xml --output danfse.html
```

Modo estrito de fontes:

```powershell
uv run danfse-nt008 xml.xml --output danfse.pdf --strict-fonts
```

## Exemplo em Python

```python
from pathlib import Path

from danfse_nt008 import parse_danfse, render_danfse_pdf, validate_danfse_data

data = parse_danfse("xml.xml")
issues = validate_danfse_data(data)

if issues:
    for issue in issues:
        print(issue.code, issue.message)
else:
    render_danfse_pdf(data, Path("danfse.pdf"))
```

## Exemplo de validacao

```python
from danfse_nt008 import parse_danfse, validate_danfse_data

data = parse_danfse("xml.xml")
issues = validate_danfse_data(data)

for issue in issues:
    print(f"{issue.code}: {issue.message}")
```

## Fonte

A NT 008 exige:

- Arial para titulos e labels
- Microsoft Sans Serif para conteudo dos demais campos

Se a fonte nao estiver instalada, a CLI avisa. Para checagem mais rigorosa, use `--strict-fonts`.

## Escopo implementado

- Cabecalho do DANFSe e identificacao da NFS-e
- Dados da NFS-e
- Prestador / Fornecedor
- Tomador / Adquirente
- Destinatario da Operacao
- Intermediario da Operacao
- Servico Prestado
- Tributacao Municipal (ISSQN)
- Tributacao Federal (Exceto CBS)
- Tributacao IBS / CBS
- Valor Total da NFS-e
- Informacoes Complementares
- Canhoto opcional

## Validacoes ja tratadas

- QR Code usando a URL publica da NFS-e com a chave de acesso
- Mensagem de homologacao quando `tpAmb == 2`
- Campos ausentes preenchidos com `-`
- Descricoes oficiais para codigos normativos mapeados
- Municipios resolvidos por tabela local gerada da API oficial do IBGE
- Supressao/reducao de Tomador, Destinatario, Intermediario e Tributacao Municipal quando aplicavel
- Linhas opcionais do ISSQN suprimidas quando todos os campos da linha nao existem no XML
- Linha PIS/COFINS da Tributacao Federal impressa somente para competencia ate o fim do ano-calendario de 2026, conforme nota 6
- Informacoes Complementares montadas na ordem definida pela NT
- Validador de medidas, tamanhos maximos de campos e regras condicionais implementadas

## Desenvolvimento

Rodar testes:

```powershell
uv run python -m unittest discover -s tests -v
```

Checar compilacao:

```powershell
uv run python -m compileall -q src tests
```

## Observacoes

- Nao use fallback entre grupos diferentes do XML para preencher informacoes.
- Dados de exemplo, caches e artefatos gerados devem ficar fora do controle de versao.
