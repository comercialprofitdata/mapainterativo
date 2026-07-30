# 📱 Aplicativo Mobile Offline de Visita a Clientes (Geolocalização & GPS)

Aplicativo web progressivo (PWA) desenvolvido para visitas a filiais e clientes, funcionando **100% offline** (mesmo sem sinal de celular ou internet). Ele identifica a sua posição GPS em tempo real e lista todos os clientes mais próximos ao seu redor, ordenados por distância, com suporte a filtro por filial, busca por texto, radar de proximidade e integração com Google Maps / Waze.

---

## 🚀 Como Usar no Celular (Passo a Passo)

### 1. Como abrir o aplicativo no seu Celular (Android / iPhone)
- **Opção A (Servidor Local / Wi-Fi):** Execute `python -m http.server 8080` no seu computador na pasta `Visitas`. Abra o navegador do celular conectado à mesma rede e acesse `http://IP_DO_SEU_PC:8080`.
- **Opção B (Instalação PWA na Tela Inicial):** No navegador do celular (Chrome / Safari / Edge), acesse o aplicativo e toque no menu do navegador -> **"Adicionar à Tela de Início"** ou **"Instalar Aplicativo"**. O app ficará salvo como um aplicativo nativo na tela do seu celular!
- **Opção C (Arquivo Direto):** Você pode enviar a pasta com os arquivos para o celular e abrir o arquivo `index.html` diretamente no navegador do seu smartphone.

---

## 🛠️ Recursos Principais

1. **📍 Geolocalização GPS Automática:**
   - Detecta sua latitude e longitude exatas com precisão em metros.
   - **"📍 Minha Localização"**: Centraliza o mapa instantaneamente onde você está.
   - **"🛰️ Seguir GPS"**: Atualiza os clientes próximos em tempo real enquanto você se desloca no veículo.

2. **📏 Filtro Inteligente de Raio de Proximidade:**
   - Selecione entre **500 metros, 1 km, 3 km, 5 km, 10 km, 25 km ou Todos**.
   - O aplicativo recalcula instantaneamente os clientes ao seu redor e os ordena da menor para a maior distância.

3. **📋 Visualizações Adaptadas para Celular:**
   - **🗺️ Mapa Interativo:** Agrupamento inteligente de marcadores (MarkerCluster) com detalhes do cliente ao tocar no pino.
   - **📋 Lista por Proximidade:** Cards limpos com nome, CNPJ, filial, status (ATIVO/INATIVO), endereço, última compra e botões de atalho:
     - 🗺️ **Maps:** Abre navegação até o cliente no Google Maps.
     - 🧭 **Waze:** Abre rota direta no aplicativo Waze.
     - 📞 **Ligar:** Disca para o telefone do cliente.
     - 💬 **WhatsApp:** Inicia conversa no WhatsApp sem precisar salvar o número.
   - **🎯 Modo Radar:** Tela estilo bússola/radar mostrando a direção e distância aproximada dos clientes em volta.

4. **🌐 Conexão com Google e Novos Pontos:**
   - Na aba **"🌐 Google"**, pesquise qualquer empresa ou endereço que não esteja na planilha.
   - Cadastre pontos manuais utilizando as coordenadas do seu GPS atual ou pesquisando no Google/OSM. Todos os pontos são salvos permanentemente no seu aparelho (IndexedDB).

5. **📂 Atualização de Planilha Direto no Celular:**
   - Quando receber uma planilha `.xlsx` nova pelo WhatsApp ou e-mail, abra a aba **"⚙️ Dados"** e toque em **"📂 Selecionar Arquivo Excel"**. O celular lê e processa a planilha inteira offline na hora!

---

## 📊 Arquitetura de Dados e Desempenho

- **Dataset Pré-processado (`generate_data.py`):**
  - Converte a planilha `clientes_rf_2026-07-30.xlsx` em `clientes_data.js` (12 MB).
  - Trata e normaliza automaticamente coordenadas geográficas para no formato decimal graus (-24.734..., -53.707...).
  - Suporta **48.182 clientes** mantendo o aplicativo leve (60 FPS no celular) usando cálculo ultra-rápido de Bounding Box Haversine.

- **Atualizando no Computador:**
  - Sempre que substituir o arquivo `.xlsx` na pasta do computador, basta rodar no terminal:
    ```bash
    python generate_data.py
    ```

---

## 📄 Estrutura de Arquivos

- [`index.html`](file:///c:/Users/vitorio.neto/Documents/Projetos%20IA/Visitas/index.html): Aplicação principal responsiva com suporte PWA.
- [`generate_data.py`](file:///c:/Users/vitorio.neto/Documents/Projetos%20IA/Visitas/generate_data.py): Script de conversão e limpeza vetorizado em Python.
- [`clientes_data.js`](file:///c:/Users/vitorio.neto/Documents/Projetos%20IA/Visitas/clientes_data.js): Banco de dados pre-carregado em JavaScript sem bloqueio de CORS.
- [`manifest.json`](file:///c:/Users/vitorio.neto/Documents/Projetos%20IA/Visitas/manifest.json): Configuração PWA para instalação no Android/iOS.
- [`sw.js`](file:///c:/Users/vitorio.neto/Documents/Projetos%20IA/Visitas/sw.js): Service Worker para cache 100% offline dos recursos.
