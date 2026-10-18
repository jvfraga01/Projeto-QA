"""Inicia o sistema. Basta dar dois cliques neste arquivo (ou em iniciar.bat)."""
import os
import subprocess
import sys
import threading
import webbrowser

AQUI = os.path.dirname(os.path.abspath(__file__))

try:
    import flask  # noqa: F401
except ImportError:
    print("O Flask (biblioteca do sistema) ainda não está instalado neste computador.")
    resposta = input("Deseja instalar agora? É preciso estar conectado à internet. [S/n] ").strip().lower()
    if resposta in ("n", "nao", "não"):
        print("Instalação cancelada. Veja o arquivo INSTALACAO.md.")
        input("Pressione Enter para sair...")
        sys.exit(1)
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r",
                               os.path.join(AQUI, "requirements.txt")])
    except subprocess.CalledProcessError:
        print("Não foi possível instalar automaticamente. Siga o arquivo INSTALACAO.md.")
        input("Pressione Enter para sair...")
        sys.exit(1)

from app import create_app  # noqa: E402

app = create_app()
URL = "http://127.0.0.1:5000"

if __name__ == "__main__":
    print(f"Sistema rodando em {URL}  (feche esta janela para encerrar)")
    threading.Timer(1.5, lambda: webbrowser.open(URL)).start()
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
