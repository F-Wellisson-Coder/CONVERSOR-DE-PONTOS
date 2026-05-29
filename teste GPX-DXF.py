import gpxpy, gpxpy.gpx, ezdxf
from pyproj import Transformer
import tkinter as tk
from tkinter import filedialog, messagebox
import os

# Descobrir UTM correta com base em coordenadas:
def coordenada_base(lat, lon):
    zona = int((lon + 180) / 6) + 1
    if lat >= 0:
        return 32600 + zona
    else:
        return 32700 + zona

# Converter GPX em DXF normal
def transformar_gpx_em_dxf(gpx_origem, dxf_destino):
    try:
        with open(gpx_origem, "r") as arquivo_gpx:
            gpx = gpxpy.parse(arquivo_gpx)

        if not (gpx.waypoints or gpx.routes or gpx.tracks):
            messagebox.showerror("Erro", "GPX está vazio.")
            return

        # Primeiro ponto para zona UTM
        if gpx.waypoints:
            lat, lon = gpx.waypoints[0].latitude, gpx.waypoints[0].longitude
        elif gpx.routes and gpx.routes[0].points:
            lat, lon = gpx.routes[0].points[0].latitude, gpx.routes[0].points[0].longitude
        else:
            lat, lon = gpx.tracks[0].segments[0].points[0].latitude, gpx.tracks[0].segments[0].points[0].longitude

        codigo_utm = coordenada_base(lat, lon)
        transformar = Transformer.from_crs("EPSG:4326", f"EPSG:{codigo_utm}", always_xy=True)

        doc = ezdxf.new("R2007")
        msp = doc.modelspace()

        def transformar_ponto(p):
            return transformar.transform(p.longitude, p.latitude)

        for ponto in gpx.waypoints:
            tamanho = 3
            x, y = transformar_ponto(ponto)
            msp.add_line((x - tamanho, y - tamanho), (x + tamanho, y + tamanho), dxfattribs={'color': 3})
            msp.add_line((x - tamanho, y + tamanho), (x + tamanho, y - tamanho), dxfattribs={'color': 3})
            if ponto.name:
                msp.add_text(ponto.name, dxfattribs={'height': 10}).set_placement((x, y, 0))

        doc.saveas(dxf_destino)
        messagebox.showinfo("Sucesso", f"Arquivo DXF criado em:\n{dxf_destino}")

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro durante a conversão:\n{e}")

# Converter GPX em DXF usando ponto de referência
def transformar_gpx_em_dxf_coordenado(gpx_origem, dxf_destino, x_ref, y_ref, ref):
    try:
        with open(gpx_origem, "r") as arquivo_gpx:
            gpx = gpxpy.parse(arquivo_gpx)

        if not gpx.waypoints:
            messagebox.showerror("Erro", "GPX sem pontos válidos.")
            return

        lat0, lon0 = gpx.waypoints[0].latitude, gpx.waypoints[0].longitude
        codigo_utm = coordenada_base(lat0, lon0)
        transformar = Transformer.from_crs("EPSG:4326", f"EPSG:{codigo_utm}", always_xy=True)

        def convert(n):
            return float(str(n)[:10])  # limita a 10 dígitos

        doc = ezdxf.new("R2007")
        msp = doc.modelspace()

        def diferenca(ref, x_ref, y_ref):
            nome_ponto = {}
            for ponto in gpx.waypoints:
                x, y = transformar.transform(ponto.longitude, ponto.latitude)
                nome_ponto[ponto.name] = x, y
            x = nome_ponto[ref][0]
            y = nome_ponto[ref][1]
            dx = x_ref - x
            dy = y_ref - y
            return dx, dy
        

        def transformar_ponto(p):
            x, y = transformar.transform(p.longitude, p.latitude)
            dx, dy = diferenca(ref, x_ref, y_ref)
            return convert(x) + dx, convert(y)+ dy 


        for ponto in gpx.waypoints:
            tamanho = 3
            x, y = transformar_ponto(ponto)
            msp.add_line((x - tamanho, y - tamanho), (x + tamanho, y + tamanho), dxfattribs={'color': 3})
            msp.add_line((x - tamanho, y + tamanho), (x + tamanho, y - tamanho), dxfattribs={'color': 3})
            if ponto.name:
                msp.add_text(ponto.name, dxfattribs={'height': 10}).set_placement((x, y, 0))

        doc.saveas(dxf_destino)
        messagebox.showinfo("Sucesso", f"Arquivo DXF criado em:\n{dxf_destino}")

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro durante a conversão:\n{e}")

# --- INTERFACE TKINTER ---

janela = tk.Tk()
janela.title("Conversor GPX/DXF")
janela.geometry("500x380")

gpx_origem = None
dxf_destino = None

def escolher_arquivo():
    global gpx_origem, dxf_destino
    gpx_origem = filedialog.askopenfilename(filetypes=[("Arquivos GPX", "*.gpx")])
    if gpx_origem:
        lbl_arquivo.config(text=f"Selecionado: {gpx_origem}")

        # sugere o mesmo nome trocando extensão
        nome_base = os.path.splitext(os.path.basename(gpx_origem))[0] + ".dxf"
        pasta = os.path.dirname(gpx_origem)

        dxf_destino = filedialog.asksaveasfilename(
            defaultextension=".dxf",
            initialfile=nome_base,
            initialdir=pasta,
            filetypes=[("DXF files", "*.dxf")]
        )

        if dxf_destino:
            lbl_destino.config(text=f"Salvar em: {dxf_destino}")
        else:
            lbl_destino.config(text="Nenhum destino selecionado")
    else:
        lbl_arquivo.config(text="Nenhum arquivo selecionado")

def converter():
    if not gpx_origem:
        messagebox.showerror("Erro", "Selecione um arquivo GPX primeiro!")
        return
    if not dxf_destino:
        messagebox.showerror("Erro", "Escolha o local de destino do DXF!")
        return

    if var_ref.get() == 1:  # com ponto de referência
        try:
            x_ref = float(entry_x.get())
            y_ref = float(entry_y.get())
            ref = str(entry_ref.get())
            transformar_gpx_em_dxf_coordenado(gpx_origem, dxf_destino, x_ref, y_ref, ref)
        except ValueError:
            messagebox.showerror("Erro", "Digite valores numéricos válidos para X e Y.")
    else:  # normal
        transformar_gpx_em_dxf(gpx_origem, dxf_destino)

# Botões e labels
btn_arquivo = tk.Button(janela, text="Selecionar arquivo GPX e destino", command=escolher_arquivo)
btn_arquivo.pack(pady=5)

lbl_arquivo = tk.Label(janela, text="Nenhum arquivo selecionado")
lbl_arquivo.pack()

lbl_destino = tk.Label(janela, text="Nenhum destino selecionado")
lbl_destino.pack()

var_ref = tk.IntVar()

def alternar_frame():
    if var_ref.get() == 1:
        frame_ref.pack(pady=5)
    else:
        frame_ref.pack_forget()

chk_ref = tk.Checkbutton(janela, text="Usar ponto de referência", variable=var_ref, command=alternar_frame)
chk_ref.pack(pady=5)

frame_ref = tk.Frame(janela)
tk.Label(frame_ref, text="X:").grid(row=0, column=0, padx=5)
entry_x = tk.Entry(frame_ref, width=12)
entry_x.grid(row=0, column=1)

tk.Label(frame_ref, text="Y:").grid(row=0, column=2, padx=5)
entry_y = tk.Entry(frame_ref, width=12)
entry_y.grid(row=0, column=3)

tk.Label(frame_ref, text="Ponto:").grid(row=1, column=1, padx=5)
entry_ref = tk.Entry(frame_ref, width=12)
entry_ref.grid(row=1, column=2)

btn_converter = tk.Button(janela, text="Converter para DXF", command=converter)
btn_converter.pack(pady=20)

janela.mainloop()