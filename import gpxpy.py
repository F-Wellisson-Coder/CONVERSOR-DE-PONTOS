import gpxpy
import gpxpy.gpx
import ezdxf
import time
from pyproj import Transformer


def get_epsg_from_coords(lat, lon):
    zona = int((lon + 180) / 6) + 1  # cálculo da zona UTM
    if lat >= 0:
        raise ValueError("Este código está configurado apenas para hemisfério sul.")
    
    epsg_map = {
        18: 31981,
        19: 31982,
        22: 31982,
        23: 31983,
        24: 31984,
        25: 31985,
    }
    return epsg_map.get(zona, None)


def gpx_to_dxf(gpx_file_path, dxf_file_path):
    
    try:
        with open(gpx_file_path, 'r') as gpx_file:
            gpx = gpxpy.parse(gpx_file)

        if not (gpx.waypoints or gpx.routes or gpx.tracks):
            print("GPX vazio.")
            return

        # Pegar a primeira coordenada como referência para definir a zona
        if gpx.waypoints:
            lat, lon = gpx.waypoints[0].latitude, gpx.waypoints[0].longitude
        elif gpx.routes and gpx.routes[0].points:
            lat, lon = gpx.routes[0].points[0].latitude, gpx.routes[0].points[0].longitude
        else:
            lat, lon = gpx.tracks[0].segments[0].points[0].latitude, gpx.tracks[0].segments[0].points[0].longitude

        epsg_code = get_epsg_from_coords(lat, lon)
        if epsg_code is None:
            raise ValueError("Longitude fora do alcance das zonas UTM brasileiras.")

        transformer = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg_code}", always_xy=True)
        print(f"Usando projeção EPSG:{epsg_code}")

        # Criar desenho DXF
        doc = ezdxf.new('R2007')
        msp = doc.modelspace()

        # --- pontos ---
        for point in gpx.waypoints:
            x, y = transformer.transform(point.longitude, point.latitude)
            #alterado aqui-----------------------------------------------
            msp.add_circle((x, y, 0), radius=1, dxfattribs={'color': 1})
            if point.name:
                #dxfattribs={'height': 10
                msp.add_text(point.name, dxfattribs={'height': 5}).set_placement((x, y, 0))

        # --- Rotas ---
        for route in gpx.routes:
            coords = []
            for point in route.points:
                x, y = transformer.transform(point.longitude, point.latitude)
                coords.append((x, y))
                msp.add_circle((x, y, 0), radius=5, dxfattribs={'color': 2})
            if len(coords) > 1:
                msp.add_lwpolyline(coords, dxfattribs={'color': 2})

        # --- Trilhas ---
        for track in gpx.tracks:
            for segment in track.segments:
                coords = []
                for point in segment.points:
                    x, y = transformer.transform(point.longitude, point.latitude)
                    coords.append((x, y))
                    msp.add_circle((x, y, 0), radius=3, dxfattribs={'color': 3})
                if len(coords) > 1:
                    msp.add_lwpolyline(coords, dxfattribs={'color': 3})

        # Salvar DXF
        doc.saveas(dxf_file_path)
        print(f"Arquivo DXF criado em: {dxf_file_path}")
        time.sleep(2)

    except Exception as e:
        print(f"Ocorreu um erro durante a conversão: {e}")
        time.sleep(2)


# Exemplo de uso
gpx_file = "C:\\Users\\Wellison\\Desktop\\teste\\gpx\\arquivo.gpx"   # Caminho do arquivo GPX
dxf_file = "C:\\Users\\Wellison\\Desktop\\teste\\dxf\\saida.dxf"    # Caminho do DXF de saída
gpx_to_dxf(gpx_file, dxf_file)