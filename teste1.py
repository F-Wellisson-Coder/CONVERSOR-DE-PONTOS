import gpxpy, gpxpy.gpx, ezdxf, time
from pyproj import Transformer
import tkinter as tk
from tkinter import filedialog


#Descobrir UTM correta com base em coordenadas:
def coordenada_base(lat, lon):
    zona = int((lon + 180) / 6) + 1
    if lat >= 0:
        return 32600 + zona
    else:
        return 32700 + zona

#função principal - COORDENADAS DO ARQUIVO GPX:
def transformar_gpx_em_dxf(gpx_origem, dxf_destino):
    try: #procurar o arquivo GPX:
        with open(gpx_origem, "r") as arquivo_gpx:
            gpx = gpxpy.parse(arquivo_gpx)
        #caso o arquivo esteja vazio:
        if not (gpx.waypoints or gpx.routes or gpx.tracks):
            print("GPX está vazio")
            time.sleep(2)
        #procura o ponto para definir a zona:
        if gpx.waypoints:
            lat, lon = gpx.waypoints[0].latitude, gpx.waypoints[0].longitude
        elif gpx.routes and gpx.routes[0].points:
            lat, lon = gpx.routes[0].points[0].latitude, gpx.routes[0].points[0].longitude
        else:
            lat, lon = gpx.tracks[0].segments[0].points[0].latitude, gpx.tracks[0].segments[0].points[0].longitude

        codigo_utm = coordenada_base(lat, lon)
        transformar = Transformer.from_crs("EPSG:4326", f"EPSG:{codigo_utm}", always_xy=True)
        print(f"Codigo da zona ultilizada EPSG:{codigo_utm} - COORDENADAS DO ARQUIVO GPX")
        time.sleep(2)
        #Cria o desenho em DXF
        doc = ezdxf.new("R2007")
        msp = doc.modelspace()
        #transformar pontos 
        def transformar_ponto(p):
            return transformar.transform(p.longitude, p.latitude)
        #GPX em pontos
        for ponto in gpx.waypoints:
            tamanho = 3
            x, y = transformar_ponto(ponto)
            msp.add_line((x - tamanho, y - tamanho), (x + tamanho, y + tamanho), dxfattribs={'color': 3})
            msp.add_line((x - tamanho, y + tamanho), (x + tamanho, y - tamanho), dxfattribs={'color': 3})
            if ponto.name:
                msp.add_text(ponto.name, dxfattribs={'height': 10}).set_placement((x, y, 0))
        doc.saveas(dxf_destino)
        print(f"Arquivo DXF criado em: {dxf_destino}")
        time.sleep(2)

    except Exception as e:
        print(f"Ocorreu um erro durante a conversão: {e}")
        time.sleep(2)


def transformar_gpx_em_dxf_coordenado(gpx_origem, dxf_destino, x_ref, y_ref):
    try: #procurar o arquvi GPX:
        with open(gpx_origem, "r") as arquivo_gpx:
            gpx = gpxpy.parse(arquivo_gpx)
        #caso o arquivo esteja vazio:
        if not (gpx.waypoints or gpx.routes or gpx.tracks):
            print("GPX está vazio")
        # 2. Detectar zona UTM automática a partir do primeiro ponto do GPX
        if gpx.waypoints:
            lat0, lon0 = gpx.waypoints[0].latitude, gpx.waypoints[0].longitude
        else:
            raise ValueError("GPX sem pontos válidos.")
            time.sleep(2)
        

        #procura o ponto para definir a zona:
        codigo_utm = coordenada_base(lat0, lon0)
        transformar = Transformer.from_crs("EPSG:4326", f"EPSG:{codigo_utm}", always_xy=True)
        print(f"Codigo da zona ultilizada EPSG:{codigo_utm} - COORDENADAS DO USUARIO ({x_ref}, {y_ref})")
        time.sleep(2)
        #tratar coordendas para 10 digitos
        def convert(n):
            n = str(n)
            n = n[0:10]
            return float(n)
        
        #desenha o arquivo DXF
        doc = ezdxf.new("R2007")
        msp = doc.modelspace()
        #pega a distancia do ponto referencia para mover 
        x, y = transformar.transform(gpx.waypoints[0].longitude, gpx.waypoints[0].latitude)
        x = convert(x)
        y = convert(y)
        dx = x_ref - x
        dy = y_ref - y

        #transformar pontos 
        def transformar_ponto(p, dx, dy):
            x, y = transformar.transform(p.longitude, p.latitude)
            x = convert(x)
            y = convert(y)
            x = x + dx
            y = y + dy
            print(x,y)
            return (x, y)
            
        #GPX em pontos
        for ponto in gpx.waypoints:
            tamanho = 3
            x, y = transformar_ponto(ponto, dx, dy)
            msp.add_line((x - tamanho, y - tamanho), (x + tamanho, y + tamanho), dxfattribs={'color': 3})
            msp.add_line((x - tamanho, y + tamanho), (x + tamanho, y - tamanho), dxfattribs={'color': 3})
            if ponto.name:
                msp.add_text(ponto.name, dxfattribs={'height': 10}).set_placement((x, y, 0))
        doc.saveas(dxf_destino)
        print(f"Arquivo DXF criado em: {dxf_destino}")
        time.sleep(2)

    except Exception as e:
        print(f"Ocorreu um erro durante a conversão: {e}")
        time.sleep(2)


def escolher_local_arquivo():
    tela = tk.Tk()
    tela.withdraw()
    caminho_do_arquivo = filedialog.askopenfilename()
    if caminho_do_arquivo:
        print("local selecionado !")
    else: 
        print("nenhum local selecionado !")
    return caminho_do_arquivo


if __name__ == "__main__":
    gpx_origem = escolher_local_arquivo()
    dxf_destino = gpx_origem.replace(".gpx", ".dxf")
    print(dxf_destino)


    escolha = input("Deseja usar ponto de referência para coordenadas relativas? (s/n): ").lower()
    if escolha == 's':
        lat_ref = float(input("Latitude do ponto de referência: "))
        lon_ref = float(input("Longitude do ponto de referência: "))
        transformar_gpx_em_dxf_coordenado(gpx_origem, dxf_destino, lat_ref, lon_ref)
    else:
        transformar_gpx_em_dxf(gpx_origem, dxf_destino)
    