# Instalação e execução

## O que é necessário
| Item | Versão | Observação |
|---|---|---|
| Python | 3.10 ou superior | https://www.python.org/downloads/ |
| Flask | 3.0 ou superior | instalado pelo `pip` (arquivo `requirements.txt`) |
| Navegador | qualquer atual | Chrome, Edge, Firefox |
| Internet | só na instalação | para baixar Python e Flask |

O banco é o SQLite, que já vem com o Python: **não há nada a instalar para o banco**.

## Jeito fácil (Windows)
Dê dois cliques em **`iniciar.bat`**.
- Se o Python não estiver instalado, ele **pergunta se você quer instalar** (S/N) e usa o `winget` do Windows.
- Se faltar o Flask, o sistema **pergunta se pode instalar** (S/N).
- Depois abre o navegador sozinho. Para encerrar, feche a janela preta.

## Pelo terminal

### Windows (CMD ou PowerShell)
```bat
winget install -e --id Python.Python.3.12
py --version
cd caminho\para\05_Codigo_Fonte
py -m pip install -r requirements.txt
py run.py
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update && sudo apt install -y python3 python3-pip python3-venv
cd caminho/para/05_Codigo_Fonte
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

### macOS
```bash
brew install python
cd caminho/para/05_Codigo_Fonte
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Abra http://127.0.0.1:5000 . **Primeiro acesso:** matrícula `1`, senha `01012000` (troque no menu "Senha").

## Testes
```bash
python -m unittest discover -v

# cobertura de testes (meta: 80%)
pip install coverage
python -m coverage run -m unittest discover
python -m coverage report -m
```

## Problemas comuns
| Sintoma | Solução |
|---|---|
| `python não é reconhecido` | Use `py` no lugar de `python`, ou reinstale marcando **Add Python to PATH**. No Windows, desative o atalho da Microsoft Store em *Configurações > Aplicativos > Aliases de execução*. |
| `externally-managed-environment` (Linux) | Use o ambiente virtual (`python3 -m venv .venv`), como mostrado acima. |
| Porta 5000 em uso | Feche o outro programa ou altere `port=5000` no final do `run.py`. |
| Quero zerar os dados | Feche o sistema e apague a pasta `instance/`. O banco e o admin inicial são recriados na próxima execução. |
