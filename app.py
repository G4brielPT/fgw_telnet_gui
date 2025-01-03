import sys
import subprocess
import os
import customtkinter as ctk
import threading
from PIL import Image
import requests
from io import BytesIO
import telnetlib
import socket
import time
from prettytable import PrettyTable
import queue

def verificar_python():
    if not sys.executable or not os.path.exists(sys.executable):
        print("Python não está instalado. Por favor, visite https://www.python.org/downloads/ para instalar o Python.")
        sys.exit(1)

def verificar_pacote_instalado(pacote):
    try:
        __import__(pacote)
        return True
    except ImportError:
        return False

def instalar_pacote(pacote):
    if not verificar_pacote_instalado(pacote):
        print(f"A instalar {pacote}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pacote])
    else:
        print(f"{pacote} já está instalado.")

def verificar_e_instalar_dependencias():
    pacotes_necessarios = ['customtkinter', 'pillow', 'requests', 'prettytable']
    
    for pacote in pacotes_necessarios:
        instalar_pacote(pacote)

class AplicacaoRouter(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("FiberMyWay - Interface Telnet do Router")
        self.geometry("800x600")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.quadro_principal = ctk.CTkFrame(self)
        self.quadro_principal.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.quadro_principal.grid_columnconfigure(0, weight=1)
        self.quadro_principal.grid_rowconfigure(0, weight=1)

        self.etiqueta_estado = None
        self.fila_resultados = queue.Queue()
        self.configurar_interface_login()

    def configurar_interface_login(self):
        for widget in self.quadro_principal.winfo_children():
            widget.destroy()

        url_logotipo = "http://192.168.1.254/external/styles/img/logo.png"
        try:
            resposta = requests.get(url_logotipo, timeout=5)
            imagem = Image.open(BytesIO(resposta.content))
            largura, altura = imagem.size
            nova_largura = 300
            nova_altura = int(altura * (nova_largura / largura))
            imagem_redimensionada = imagem.resize((nova_largura, nova_altura), Image.LANCZOS)
            foto = ctk.CTkImage(light_image=imagem_redimensionada, dark_image=imagem_redimensionada, size=(nova_largura, nova_altura))
            etiqueta_logotipo = ctk.CTkLabel(self.quadro_principal, image=foto, text="")
            etiqueta_logotipo.grid(row=0, column=0, pady=(20, 10))
        except Exception as e:
            print(f"Não foi possível carregar o logótipo: {str(e)}")

        entrada_utilizador = ctk.CTkEntry(self.quadro_principal, placeholder_text="Nome de utilizador")
        entrada_utilizador.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        entrada_palavra_passe = ctk.CTkEntry(self.quadro_principal, placeholder_text="Palavra-passe", show="*")
        entrada_palavra_passe.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        botao_entrar = ctk.CTkButton(self.quadro_principal, text="Entrar", command=lambda: self.entrar(entrada_utilizador.get(), entrada_palavra_passe.get()))
        botao_entrar.grid(row=3, column=0, padx=20, pady=20, sticky="ew")

        self.etiqueta_estado = ctk.CTkLabel(self.quadro_principal, text="")
        self.etiqueta_estado.grid(row=4, column=0, padx=20, pady=10)

    def entrar(self, utilizador, palavra_passe):
        self.atualizar_estado("A iniciar sessão...")
        threading.Thread(target=self.executar_telnet, args=(utilizador, palavra_passe)).start()

    def executar_telnet(self, utilizador, palavra_passe):
        try:
            anfitriao = "192.168.1.254"
            porta = 23
            timeout = 10

            tn = telnetlib.Telnet(anfitriao, porta, timeout)

            tn.read_until(b"Login: ", timeout)
            tn.write(utilizador.encode('ascii') + b"\n")

            tn.read_until(b"Password: ", timeout)
            tn.write(palavra_passe.encode('ascii') + b"\n")

            login_result = tn.read_until(b"/cli>", timeout)

            if b"/cli>" in login_result:
                tn.write(b"lan/dhcp/show\n")
                time.sleep(2)
                tn.write(b"quit\n")

                resultado = tn.read_all().decode('ascii')
                self.fila_resultados.put(resultado)
                self.after(0, self.processar_resultado)
            else:
                self.atualizar_estado("Falha no login. Verifique o nome de utilizador e a palavra-passe.")

        except socket.timeout:
            self.atualizar_estado("Erro: Tempo limite excedido ao tentar conectar.")
        except Exception as e:
            self.atualizar_estado(f"Erro: {str(e)}")
        finally:
            try:
                tn.close()
            except:
                pass

    def atualizar_estado(self, mensagem):
        self.after(0, lambda: self.etiqueta_estado.configure(text=mensagem))

    def processar_resultado(self):
        try:
            resultado = self.fila_resultados.get_nowait()
            self.mostrar_resultado(resultado)
        except queue.Empty:
            pass

    def mostrar_resultado(self, resultado):
        try:
            for widget in self.quadro_principal.winfo_children():
                widget.destroy()

            caixa_texto_resultado = ctk.CTkTextbox(self.quadro_principal, width=760, height=500)
            caixa_texto_resultado.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
            
            linhas = resultado.split('\n')
            texto_formatado = "Informações DHCP do Router:\n\n"

            # Filtrar linhas indesejadas
            linhas_filtradas = [linha for linha in linhas if not any(x in linha for x in ["GR241AG Gateway Router", "CLI Application", "Bye bye", " lan/dhcp/show", "quit", "/cli> quit"])]

            # Remover linhas em branco no início e no fim
            while linhas_filtradas and not linhas_filtradas[0].strip():
                linhas_filtradas.pop(0)
            while linhas_filtradas and not linhas_filtradas[-1].strip():
                linhas_filtradas.pop()

            texto_formatado += '\n'.join(linhas_filtradas)
            
            caixa_texto_resultado.insert("1.0", texto_formatado)

            botao_voltar = ctk.CTkButton(self.quadro_principal, text="Voltar", command=self.configurar_interface_login)
            botao_voltar.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
            
            self.etiqueta_estado = ctk.CTkLabel(self.quadro_principal, text="Informações obtidas com sucesso!")
            self.etiqueta_estado.grid(row=2, column=0, padx=20, pady=10)

        except Exception as e:
            print(f"Erro ao mostrar resultado: {str(e)}")
            self.atualizar_estado("Ocorreu um erro ao exibir as informações. Por favor, tente novamente.")

if __name__ == "__main__":
    print("Bem-vindo ao FiberMyWay!")
    
    verificar_python()
    verificar_e_instalar_dependencias()

    app = AplicacaoRouter()
    app.mainloop()
