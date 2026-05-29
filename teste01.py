import gpxpy
import gpxpy.gpx
import ezdxf
import time
from pyproj import Transformer

# Função para descobrir EPSG UTM automaticamente
def get_utm_epsg(lat, lon):
    zona = int((lon + 180) / 6) + 1
    if lat >= 0:
        return 32600 + zona  # Hemisfério Norte
    else:
        return 32700 + zona  # Hemisfério Sul

# Função principal: coordenadas absolutas
def gpx_to_dxf(gpx_file_path, dxf_file_path):
    try: #abrir o arquivo gpx
        with open(gpx_file_path, 'r') as gpx_file:
            gpx = gpxpy.parse(gpx_file)
        
        if not (gpx.waypoints or gpx.routes or gpx.tracks):
            print("GPX vazio.")
            return

        # Pega primeira coordenada para definir zona
        if gpx.waypoints:
            lat, lon = gpx.waypoints[0].latitude, gpx.waypoints[0].longitude
        elif gpx.routes and gpx.routes[0].points:
            lat, lon = gpx.routes[0].points[0].latitude, gpx.routes[0].points[0].longitude
        else:
            lat, lon = gpx.tracks[0].segments[0].points[0].latitude, gpx.tracks[0].segments[0].points[0].longitude

        epsg_code = get_utm_epsg(lat, lon)
        transformer = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg_code}", always_xy=True)
        print(f"Usando projeção EPSG:{epsg_code} (coordenadas absolutas)")
        #cria o desenho em DXF
        doc = ezdxf.new('R2007')
        msp = doc.modelspace()

        def transform_point(p):
            return transformer.transform(p.longitude, p.latitude)

        # --- Waypoints ---
        for point in gpx.waypoints:
            x, y = transform_point(point)
            msp.add_circle((x, y, 0), radius=5, dxfattribs={'color': 1})
            if point.name:
                msp.add_text(point.name, dxfattribs={'height': 10}).set_placement((x, y, 0))

        # --- Rotas ---
        for route in gpx.routes:
            coords = [transform_point(p) for p in route.points]
            for c in coords:
                msp.add_circle(c + (0,), radius=5, dxfattribs={'color': 2})
            if len(coords) > 1:
                msp.add_lwpolyline(coords, dxfattribs={'color': 2})

        # --- Trilhas ---
        for track in gpx.tracks:
            for segment in track.segments:
                coords = [transform_point(p) for p in segment.points]
                for c in coords:
                    msp.add_circle(c + (0,), radius=3, dxfattribs={'color': 3})
                if len(coords) > 1:
                    msp.add_lwpolyline(coords, dxfattribs={'color': 3})

        doc.saveas(dxf_file_path)
        print(f"Arquivo DXF criado em: {dxf_file_path}")

    except Exception as e:
        print(f"Ocorreu um erro durante a conversão: {e}")

# Função opcional: coordenadas relativas ao ponto do usuário
def gpx_to_dxf_relative(gpx_file_path, dxf_file_path, lat_ref, lon_ref):
    try:
        with open(gpx_file_path, 'r') as gpx_file:
            gpx = gpxpy.parse(gpx_file)

        epsg_code = get_utm_epsg(lat_ref, lon_ref)
        transformer = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg_code}", always_xy=True)
        print(f"Usando projeção EPSG:{epsg_code} com referência em ({lat_ref}, {lon_ref})")

        x_ref, y_ref = transformer.transform(lon_ref, lat_ref)

        doc = ezdxf.new('R2007')
        msp = doc.modelspace()

        def transform_point(p):
            x, y = transformer.transform(p.longitude, p.latitude)
            return (x - x_ref, y - y_ref)

        # --- Waypoints ---
        for point in gpx.waypoints:
            x, y = transform_point(point)
            msp.add_circle((x, y, 0), radius=5, dxfattribs={'color': 1})
            if point.name:
                msp.add_text(point.name, dxfattribs={'height': 10}).set_placement((x, y, 0))

        # --- Rotas ---
        for route in gpx.routes:
            coords = [transform_point(p) for p in route.points]
            for c in coords:
                msp.add_circle(c + (0,), radius=5, dxfattribs={'color': 2})
            if len(coords) > 1:
                msp.add_lwpolyline(coords, dxfattribs={'color': 2})

        # --- Trilhas ---
        for track in gpx.tracks:
            for segment in track.segments:
                coords = [transform_point(p) for p in segment.points]
                for c in coords:
                    msp.add_circle(c + (0,), radius=3, dxfattribs={'color': 3})
                if len(coords) > 1:
                    msp.add_lwpolyline(coords, dxfattribs={'color': 3})

        doc.saveas(dxf_file_path)
        print(f"Arquivo DXF criado em: {dxf_file_path}")

    except Exception as e:
        print(f"Ocorreu um erro durante a conversão: {e}")

# ============================
# Script interativo
# ============================
if __name__ == "__main__":
    gpx_file = input("Caminho do arquivo GPX: ")
    dxf_file = input("Caminho de saída do DXF: ")

    escolha = input("Deseja usar ponto de referência para coordenadas relativas? (s/n): ").lower()
    if escolha == 's':
        lat_ref = float(input("Latitude do ponto de referência: "))
        lon_ref = float(input("Longitude do ponto de referência: "))
        gpx_to_dxf_relative(gpx_file, dxf_file, lat_ref, lon_ref)
    else:
        gpx_to_dxf(gpx_file, dxf_file)