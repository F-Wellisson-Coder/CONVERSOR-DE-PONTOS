import gpxpy, ezdxf
from pyproj import Transformer
import customtkinter as ctk
from customtkinter import filedialog
from CTkMessagebox import CTkMessagebox
import os

# ================= FUNÇÕES DE CONVERSÃO ================= #

# Descobrir a zona de coordenada correta para usar na biblioteca do pyproj:
def coordenada_base(lat, lon):
    zona = int((lon + 180) / 6) + 1
    if lat >= 0:
        return 32600 + zona
    else:
        return 32700 + zona

# Converter GPX em DXF sem ponto de referência:
def transformar_gpx_dxf(gpx_origem, dxf_destino):
    try:
        with open(gpx_origem, "r") as arquivo_gpx:
            gpx = gpxpy.parse(arquivo_gpx)

        if not (gpx.waypoints or gpx.routes or gpx.tracks):
            CTkMessagebox(message="Erro: Arquivo GPX está vazio.", icon="cancel")
            return
        
        # Pegar o primeiro ponto (waypoint, rota ou faixa)
        if gpx.waypoints:
            lat, lon = gpx.waypoints[0].latitude, gpx.waypoints[0].longitude
        elif gpx.routes and gpx.routes[0].points:
            lat, lon = gpx.routes[0].points[0].latitude, gpx.routes[0].points[0].longitude
        else:
            lat, lon = gpx.tracks[0].segments[0].points[0].latitude, gpx.tracks[0].segments[0].points[0].longitude

        # Código EPSG da zona UTM
        codigo_UTM = coordenada_base(lat, lon)
        transformar = Transformer.from_crs("EPSG:4326", f"EPSG:{codigo_UTM}", always_xy=True)

        # Criar arquivo DXF
        doc = ezdxf.new("R2007")
        msp = doc.modelspace()

        # Função auxiliar para transformar coordenadas
        def transformar_ponto(p):
            return transformar.transform(p.longitude, p.latitude)
        
        # Criar símbolos "X" e nomes
        for ponto in gpx.waypoints:
            tamanho = 3
            x, y = transformar_ponto(ponto)
            msp.add_line((x - tamanho, y - tamanho), (x + tamanho, y + tamanho), dxfattribs={"color": 3})
            msp.add_line((x - tamanho, y + tamanho), (x + tamanho, y - tamanho), dxfattribs={"color": 3})
            if ponto.name:
                msp.add_text(ponto.name, dxfattribs={"height": 10}).set_placement((x, y, 0))

        # Salvar arquivo
        doc.saveas(dxf_destino)
        CTkMessagebox(message=f"Sucesso! Arquivo DXF criado em:\n{dxf_destino}", icon="check")

    except Exception as e:
        CTkMessagebox(message=f"Erro durante a conversão:\n{e}", icon="cancel")

# Converter GPX em DXF usando ponto de referência
def transformar_gpx_dxf_coordenado(gpx_origem, dxf_destino, ref, x_ref, y_ref):
    try:
        with open(gpx_origem, "r") as arquivo_gpx:
            gpx = gpxpy.parse(arquivo_gpx)

        if not gpx.waypoints:
            CTkMessagebox(message="Erro: GPX sem pontos válidos.", icon="cancel")
            return
        
        # Pegar o primeiro ponto do arquivo GPX
        lat0, lon0 = gpx.waypoints[0].latitude, gpx.waypoints[0].longitude

        # Código EPSG da zona UTM
        codigo_UTM = coordenada_base(lat0, lon0)
        transformar = Transformer.from_crs("EPSG:4326", f"EPSG:{codigo_UTM}", always_xy=True)

        # Limita coordenadas a 10 dígitos
        def converter(n):
            return float(str(n)[:10])
        
        # Criar arquivo DXF
        doc = ezdxf.new("R2007")
        msp = doc.modelspace()

        # Calcula diferença entre ponto de referência e coordenadas desejadas
        nome_ponto = {p.name: transformar.transform(p.longitude, p.latitude) for p in gpx.waypoints}
        if ref not in nome_ponto:
            CTkMessagebox(message=f"Erro: Ponto '{ref}' não encontrado no GPX.", icon="cancel")
            return
        
        x0, y0 = nome_ponto[ref]
        dx = x_ref - x0
        dy = y_ref - y0

        # Converter e desenhar pontos ajustados
        for ponto in gpx.waypoints:
            tamanho = 3
            x, y = transformar.transform(ponto.longitude, ponto.latitude)
            x = converter(x) + dx
            y = converter(y) + dy
            msp.add_line((x - tamanho, y - tamanho), (x + tamanho, y + tamanho), dxfattribs={'color': 3})
            msp.add_line((x - tamanho, y + tamanho), (x + tamanho, y - tamanho), dxfattribs={'color': 3})
            if ponto.name:
                msp.add_text(ponto.name, dxfattribs={'height': 10}).set_placement((x, y, 0))
            
        # Salvar arquivo
        doc.saveas(dxf_destino)
        CTkMessagebox(message=f"Sucesso! Arquivo DXF criado em:\n{dxf_destino}", icon="check")

    except Exception as e:
        CTkMessagebox(message=f"Erro durante a conversão:\n{e}", icon="cancel")

# ================= INTERFACE CUSTOM TKINTER ================= #

janela = ctk.CTk()
janela.title("Conversor GPX/DXF")
janela.geometry("500x380")

# Variáveis globais
gpx_origem = None
dxf_destino = None

# Escolher arquivo GPX e local de destino DXF
def escolher_arquivo():
    global gpx_origem, dxf_destino
    gpx_origem = filedialog.askopenfilename(filetypes=[("Arquivos GPX", "*.gpx")])
    if gpx_origem:
        lbl_arquivo.configure(text=f"Selecionado: {gpx_origem}")

        nome_base = os.path.splitext(os.path.basename(gpx_origem))[0] + ".dxf"
        pasta = os.path.dirname(gpx_origem)

        dxf_destino = filedialog.asksaveasfilename(
            defaultextension=".dxf",
            initialfile=nome_base,
            initialdir=pasta,
            filetypes=[("DXF files", "*.dxf")]
        )

        if dxf_destino:
            lbl_destino.configure(text=f"Salvar em: {dxf_destino}")
        else:
            lbl_destino.configure(text="Nenhum destino selecionado")
    else:
        lbl_arquivo.configure(text="Nenhum arquivo selecionado")

# Converter diretamente
def converter():
    if not gpx_origem:
        CTkMessagebox(message="Erro: Selecione um arquivo GPX primeiro!", icon="cancel")
        return
    if not dxf_destino:
        CTkMessagebox(message="Erro: Escolha o local de destino do DXF!", icon="cancel")
        return
    transformar_gpx_dxf(gpx_origem, dxf_destino)

# Converter com coordenada de referência
def converter_coordenado():
    if not gpx_origem:
        CTkMessagebox(message="Erro: Selecione um arquivo GPX primeiro!", icon="cancel")
        return
    if not dxf_destino:
        CTkMessagebox(message="Erro: Escolha o local de destino do DXF!", icon="cancel")
        return
    try:
        x_ref = float(entry_x.get())
        y_ref = float(entry_y.get())
        ref = str(entry_ref.get())
        transformar_gpx_dxf_coordenado(gpx_origem, dxf_destino, ref, x_ref, y_ref)
    except ValueError:
        CTkMessagebox(message="Erro: Digite valores numéricos válidos para X e Y.", icon="cancel")

# ================= COMPONENTES GRÁFICOS ================= #

btn_arquivo = ctk.CTkButton(janela, text="Selecionar arquivo GPX e destino", command=escolher_arquivo)
btn_arquivo.pack(pady=5)

lbl_arquivo = ctk.CTkLabel(janela, text="Nenhum arquivo selecionado")
lbl_arquivo.pack()

lbl_destino = ctk.CTkLabel(janela, text="Nenhum destino selecionado")
lbl_destino.pack()

Multiabas = ctk.CTkTabview(master=janela)
Multiabas.pack(padx=20, pady=20)

Multiabas.add("CONVERTER")
Multiabas.add("  MOVER  ")

# Aba CONVERTER
btn_converter = ctk.CTkButton(master=Multiabas.tab("CONVERTER"), text="Converter para DXF", command=converter)
btn_converter.place(relx=0.5, rely=0.5, anchor='center')

# Aba MOVER
aba_mover = Multiabas.tab("  MOVER  ")

ctk.CTkLabel(master=aba_mover, text="Ponto:").grid(row=0, column=0, columnspan=2, padx=20, pady=5)
entry_ref = ctk.CTkEntry(master=aba_mover, width=50)
entry_ref.grid(row=0, column=2, columnspan=2, padx=5, pady=5)

ctk.CTkLabel(master=aba_mover, text="X:").grid(row=1, column=1, padx=5, pady=5)
entry_x = ctk.CTkEntry(master=aba_mover, width=125,)
entry_x.grid(row=1, column=2, padx=5, pady=5)

ctk.CTkLabel(master=aba_mover, text="Y:").grid(row=2, column=1, padx=5, pady=5)
entry_y = ctk.CTkEntry(master=aba_mover, width=125)
entry_y.grid(row=2, column=2, padx=5, pady=5)

btn_mover = ctk.CTkButton(master=aba_mover, text="Converter para DXF", command=converter_coordenado)
btn_mover.grid(row=5, column=2, padx=5, pady=5)

lbl_criador = ctk.CTkLabel(janela, text="Criado por: F.wellisson")
lbl_criador.pack()


# Iniciar aplicação
janela.mainloop()