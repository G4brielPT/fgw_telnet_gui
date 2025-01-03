# FiberMyWay - Interface Telnet para Router

**FiberMyWay** é uma interface gráfica desenvolvida em Python que se conecta a um **FiberGateway** via **Telnet** para buscar e exibir informações do router, com o objetivo de facilitar a visualização e interação com os dados da rede.

## Funcionalidades

- Conexão via **Telnet** para buscar informações do **FiberGateway**.
- Interface gráfica simples e intuitiva utilizando o **CustomTkinter**.
- Suporte para login com nome de usuário e senha.
- Exibição de resultados obtidos após a execução de comandos Telnet.

## Como Funciona

1. O programa inicia uma conexão **Telnet** com o **FiberGateway** (IP: `192.168.1.254` e porta `23`).
2. O usuário insere o nome de usuário e a senha para realizar o login no dispositivo.
3. O aplicativo envia comandos via Telnet para obter as informações solicitadas.
4. As informações são processadas e exibidas na interface gráfica.
5. Se houver falha no login ou na comunicação com o dispositivo, mensagens de erro são exibidas.

## Requisitos

- Python 3.x
- Bibliotecas necessárias:
  - `customtkinter` (para a interface gráfica)
  - `pillow` (para processamento de imagens)
  - `requests` (para baixar imagens)
  - `prettytable` (para exibir as tabelas)
  - `telnetlib` (para comunicação via Telnet)
  - `queue` (para gerenciar os resultados assíncronos)

## Instalação

1. Clone o repositório:
   git clone https://github.com/G4brielPT/fgw_telnet_gui.git

2. Navegue até o diretório do projeto:
   cd fgw_telnet_gui

3. Instale as dependências:
   pip install -r requirements.txt

## Como Usar

1. Execute o aplicativo:
   python main.py

2. A interface gráfica será exibida, e você será solicitado a inserir o nome de usuário e a senha do **FiberGateway**.

3. Após o login bem-sucedido, os dados obtidos a partir dos comandos Telnet serão exibidos na interface.

4. Caso ocorra algum erro, mensagens informativas aparecerão na tela.

## Estrutura do Código

- **verificar_python**: Verifica se o Python está instalado no sistema.
- **verificar_pacote_instalado**: Verifica se os pacotes necessários estão instalados.
- **instalar_pacote**: Instala os pacotes ausentes.
- **verificar_e_instalar_dependencias**: Verifica e instala as dependências do projeto.
- **AplicacaoRouter**: A classe principal que define a interface gráfica e os comportamentos da aplicação, incluindo a conexão Telnet e o processamento dos resultados.
