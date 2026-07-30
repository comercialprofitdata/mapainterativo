import pandas as pd
import json
import os
import sys

def main():
    excel_path = os.path.join(os.path.dirname(__file__), 'clientes_rf_2026-07-30.xlsx')
    if not os.path.exists(excel_path):
        print(f"Arquivo não encontrado: {excel_path}")
        sys.exit(1)
        
    print(f"Lendo {excel_path} (37 colunas)...")
    df = pd.read_excel(excel_path)
    print(f"Total de registros lidos: {len(df)}")
    
    # Tratamento de Coordenadas
    def fix_lat_lon(series):
        s = pd.to_numeric(series.astype(str).str.strip().str.replace(',', '.'), errors='coerce')
        mask = s.notna() & (s != 0)
        vals = s[mask].copy()
        while (vals.abs() > 180).any():
            over = vals.abs() > 180
            vals[over] = vals[over] / 10.0
        s[mask] = vals.round(6)
        return s

    df['lat_clean'] = fix_lat_lon(df['lat'])
    df['lon_clean'] = fix_lat_lon(df['lon'])

    is_br_lat = (df['lat_clean'] >= -35.0) & (df['lat_clean'] <= 6.0)
    is_br_lon = (df['lon_clean'] >= -75.0) & (df['lon_clean'] <= -30.0)
    valid_geo = is_br_lat & is_br_lon
    
    df.loc[~valid_geo, 'lat_clean'] = None
    df.loc[~valid_geo, 'lon_clean'] = None

    tel1 = df['telefone'].astype(str).str.strip().replace({'nan': '', 'None': '', 'NaN': ''})
    tel2 = df['rf_telefone'].astype(str).str.strip().replace({'nan': '', 'None': '', 'NaN': ''})
    df['tel_clean'] = tel1.where(tel1 != '', tel2)

    df['dt_clean'] = pd.to_datetime(df['data_ult'], errors='coerce').dt.strftime('%Y-%m-%d').fillna('')

    cnae_str = df['cnae_principal'].fillna('').astype(str).str.lower()
    target_keywords = ['supermercado', 'minimercado', 'mercearia', 'padaria', 'confeitaria', 'bebida', 'restaurante', 'lanchonete', 'alimento', 'conveniencia', 'armazem']
    is_target_cnae = cnae_str.apply(lambda val: any(kw in val for kw in target_keywords))

    records = []
    
    def get_str(col):
        return df[col].fillna('').astype(str).str.strip().values if col in df.columns else ['']*len(df)

    nomes = get_str('nome')
    razoes = get_str('razao')
    cnpjs = get_str('cnpj')
    filiais = get_str('filial')
    statuses = get_str('status')
    enderecos = get_str('endereco')
    ceps = get_str('cep')
    cidades = get_str('cidade')
    ufs = get_str('uf')
    telefones = df['tel_clean'].values
    emails = get_str('email')
    rf_emails = get_str('rf_email')
    dts = df['dt_clean'].values
    vlrs = pd.to_numeric(df['vlr_ult'], errors='coerce').fillna(0.0).round(2).values
    vlr_maxs = pd.to_numeric(df['vlr_max'], errors='coerce').fillna(0.0).round(2).values
    limites = pd.to_numeric(df['limite'], errors='coerce').fillna(0.0).round(2).values
    prazos = get_str('prazo')
    atividades = get_str('atividade')
    dt_aberturas = get_str('dt_abertura')
    obss = get_str('obs')
    tipos = get_str('tipo')
    situacoes_cnpj = get_str('situacao_cnpj')
    cnaes_princ = get_str('cnae_principal')
    cnaes_sec = get_str('cnaes_secundarios')
    cap_sociais = pd.to_numeric(df['capital_social'], errors='coerce').fillna(0.0).round(2).values
    naturezas = get_str('natureza_jur')
    socios = get_str('socios')
    pop_muns = pd.to_numeric(df['pop_mun'], errors='coerce').fillna(0).values
    pib_pcs = pd.to_numeric(df['pib_pc'], errors='coerce').fillna(0.0).round(2).values
    lats = df['lat_clean'].values
    lons = df['lon_clean'].values
    cods = df['cod'].values

    for i in range(len(df)):
        lt = float(lats[i]) if pd.notna(lats[i]) else None
        lg = float(lons[i]) if pd.notna(lons[i]) else None
        c_code = int(cods[i]) if pd.notna(cods[i]) and str(cods[i]).isdigit() else i + 1

        rec = {
            "id": c_code,
            "c": nomes[i],
            "r": razoes[i],
            "j": cnpjs[i],
            "f": filiais[i],
            "s": statuses[i],
            "e": enderecos[i],
            "cep": ceps[i],
            "m": cidades[i],
            "u": ufs[i] or "PR",
            "t": telefones[i],
            "email": emails[i] or rf_emails[i],
            "du": dts[i],
            "vu": float(vlrs[i]),
            "vmax": float(vlr_maxs[i]),
            "lim": float(limites[i]),
            "prazo": prazos[i],
            "ativ": atividades[i],
            "dtab": dt_aberturas[i],
            "obs": obss[i],
            "tipo": tipos[i],
            "sit_rf": situacoes_cnpj[i] or "ATIVA",
            "cnae": cnaes_princ[i],
            "cnae_sec": cnaes_sec[i],
            "cap_soc": float(cap_sociais[i]),
            "nat_jur": naturezas[i],
            "socios": socios[i],
            "pop": int(pop_muns[i]),
            "pib": float(pib_pcs[i]),
            "target": bool(is_target_cnae[i]),
            "lt": lt,
            "lg": lg
        }
        records.append(rec)

    # Remova os arquivos antigos > 25MB para não estourar o limite do Cloudflare
    for old_file in ['clientes_data.json', 'clientes_data.js']:
        old_path = os.path.join(os.path.dirname(__file__), old_file)
        if os.path.exists(old_path):
            os.remove(old_path)
            print(f"Removido arquivo antigo: {old_file}")

    # Dividir em 3 partes (< 14MB cada) para respeitar o limite de 25MB do Cloudflare Pages
    total = len(records)
    chunk_size = (total // 3) + 1
    chunks = [records[i:i + chunk_size] for i in range(0, total, chunk_size)]

    for idx, chunk in enumerate(chunks, 1):
        js_chunk_path = os.path.join(os.path.dirname(__file__), f'clientes_part{idx}.js')
        with open(js_chunk_path, 'w', encoding='utf-8') as f:
            f.write(f"window.CLIENTES_PRELOAD = (window.CLIENTES_PRELOAD || []).concat(")
            json.dump(chunk, f, ensure_ascii=False, separators=(',', ':'))
            f.write(");\n")
        size_mb = os.path.getsize(js_chunk_path) / (1024 * 1024)
        print(f"Criado {js_chunk_path} ({size_mb:.2f} MB - OK Cloudflare < 25MB)")

if __name__ == '__main__':
    main()
