"""
BWS Finance - Landing Page Server
Servidor HTTP simples para servir a página inicial na porta 80
"""
import http.server
import socketserver
import os
import sys

# Configurações
PORT = 80
DIRECTORY = os.path.join(os.path.dirname(__file__), 'landing')

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Adiciona headers de segurança
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('X-XSS-Protection', '1; mode=block')
        super().end_headers()

def start_server():
    """Inicia o servidor HTTP na porta 80"""
    try:
        with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
            print("=" * 60)
            print(f"🌐 BWS Finance - Landing Page Server")
            print("=" * 60)
            print(f"✅ Servidor iniciado na porta {PORT}")
            print(f"📂 Diretório: {DIRECTORY}")
            print(f"🔗 Acesso Local: http://localhost:{PORT}")
            print(f"🔗 Acesso Rede: http://192.168.80.122:{PORT}")
            print("=" * 60)
            print("Pressione Ctrl+C para parar o servidor\n")
            httpd.serve_forever()
    except PermissionError:
        print("\n❌ ERRO: Porta 80 requer privilégios administrativos!")
        print("\n📌 Soluções:")
        print("   1. Execute como Administrador (clique direito > 'Executar como administrador')")
        print("   2. Ou altere a porta para 8080 (não requer admin)\n")
        sys.exit(1)
    except OSError as e:
        if "10048" in str(e) or "Only one usage" in str(e):
            print("\n❌ ERRO: Porta 80 já está em uso!")
            print("\n📌 Solução: Libere a porta 80 ou use outra porta (ex: 8080)\n")
            sys.exit(1)
        else:
            raise
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor encerrado pelo usuário")
        sys.exit(0)

if __name__ == "__main__":
    start_server()
