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

    # Validação Brasil (-35 <= lat <= 6, -75 <= lon <= -30)
    is_br_lat = (df['lat_clean'] >= -35.0) & (df['lat_clean'] <= 6.0)
    is_br_lon = (df['lon_clean'] >= -75.0) & (df['lon_clean'] <= -30.0)
    valid_geo = is_br_lat & is_br_lon
    
    df.loc[~valid_geo, 'lat_clean'] = None
    df.loc[~valid_geo, 'lon_clean'] = None

    # Tratamento de Telefone e Data
    tel1 = df['telefone'].astype(str).str.strip().replace({'nan': '', 'None': '', 'NaN': ''})
    tel2 = df['rf_telefone'].astype(str).str.strip().replace({'nan': '', 'None': '', 'NaN': ''})
    df['tel_clean'] = tel1.where(tel1 != '', tel2)

    df['dt_clean'] = pd.to_datetime(df['data_ult'], errors='coerce').dt.strftime('%Y-%m-%d').fillna('')

    # Mapeamento de CNAEs Alvo (Alimentício, Varejo, Bebidas, Padaria, Restaurante, Conveniência)
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
            "c": nomes[i],                          # Nome Fantasia
            "r": razoes[i],                         # Razão Social
            "j": cnpjs[i],                          # CNPJ
            "f": filiais[i],                        # Filial
            "s": statuses[i],                       # Status (ATIVO/INATIVO)
            "e": enderecos[i],                      # Endereço
            "cep": ceps[i],                         # CEP
            "m": cidades[i],                        # Cidade
            "u": ufs[i] or "PR",                    # UF
            "t": telefones[i],                      # Telefone
            "email": emails[i] or rf_emails[i],     # Email
            "du": dts[i],                           # Data Última Compra
            "vu": float(vlrs[i]),                   # Valor Última Compra
            "vmax": float(vlr_maxs[i]),             # Valor Máximo
            "lim": float(limites[i]),               # Limite Crédito
            "prazo": prazos[i],                     # Prazo
            "ativ": atividades[i],                  # Atividade
            "dtab": dt_aberturas[i],                # Data Abertura
            "obs": obss[i],                         # Observações
            "tipo": tipos[i],                       # Tipo Perfil
            "sit_rf": situacoes_cnpj[i] or "ATIVA", # Situação CNPJ Receita Federal
            "cnae": cnaes_princ[i],                 # CNAE Principal
            "cnae_sec": cnaes_sec[i],               # CNAEs Secundários
            "cap_soc": float(cap_sociais[i]),       # Capital Social
            "nat_jur": naturezas[i],                # Natureza Jurídica
            "socios": socios[i],                    # QSA / Sócios
            "pop": int(pop_muns[i]),                # População Município
            "pib": float(pib_pcs[i]),               # PIB per Capita
            "target": bool(is_target_cnae[i]),      # CNAE Alvo
            "lt": lt,                               # Latitude
            "lg": lg                                # Longitude
        }
        records.append(rec)

    geo_count = sum(1 for r in records if r['lt'] is not None)
    target_count = sum(1 for r in records if r['target'])
    print(f"Total de registros: {len(records)}")
    print(f"Com GPS válido: {geo_count} ({geo_count/len(records)*100:.1f}%)")
    print(f"CNAE Alvo (Atendidos): {target_count} ({target_count/len(records)*100:.1f}%)")

    json_path = os.path.join(os.path.dirname(__file__), 'clientes_data.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, separators=(',', ':'))
    print(f"Criado {json_path} ({os.path.getsize(json_path)/(1024*1024):.2f} MB)")

    js_path = os.path.join(os.path.dirname(__file__), 'clientes_data.js')
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write("window.CLIENTES_PRELOAD = ")
        json.dump(records, f, ensure_ascii=False, separators=(',', ':'))
        f.write(";\n")
    print(f"Criado {js_path} ({os.path.getsize(js_path)/(1024*1024):.2f} MB)")

if __name__ == '__main__':
    main()
