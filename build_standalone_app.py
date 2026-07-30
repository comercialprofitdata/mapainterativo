import json
import os

def main():
    visitas_dir = os.path.dirname(__file__)
    index_path = os.path.join(visitas_dir, 'index.html')
    data_path = os.path.join(visitas_dir, 'clientes_data.json')
    output_path = os.path.join(visitas_dir, 'app_visitas_standalone.html')
    
    if not os.path.exists(index_path) or not os.path.exists(data_path):
        print("Arquivo index.html ou clientes_data.json não encontrado.")
        return
        
    print("Lendo clientes_data.json...")
    with open(data_path, 'r', encoding='utf-8') as f:
        raw_json = f.read()
        
    print("Lendo index.html...")
    with open(index_path, 'r', encoding='utf-8') as f:
        html = f.read()
        
    # Substitui <script src="clientes_data.js"></script> pelo JSON embutido diretamente
    embed_script = f"<script>\nwindow.CLIENTES_PRELOAD = {raw_json};\n</script>"
    
    if '<script src="clientes_data.js"></script>' in html:
        standalone_html = html.replace('<script src="clientes_data.js"></script>', embed_script)
    else:
        standalone_html = html.replace('</head>', f'{embed_script}\n</head>')
        
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(standalone_html)
        
    print(f"Sucesso! Gerado {output_path} ({os.path.getsize(output_path)/(1024*1024):.2f} MB)")

if __name__ == '__main__':
    main()
