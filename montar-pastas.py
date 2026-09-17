#!/usr/bin/env python3
"""Monta as pastas de acesso do Lucro Artesanato.

POR QUE ISTO EXISTE (regra dura do Vini, 17/09/2026):

A liberacao e PELO LINK, e a chave vai no CAMINHO. Nada de backend, localStorage
ou query string. Motivo tecnico, aprendido em campo na oferta 004: no fluxo
Compartilhar > Adicionar a Tela de Inicio do iOS, a URL do icone sai do manifest
da pagina ABERTA e a query string e descartada. Se a chave estivesse na query, o
icone nasceria travado e nao haveria recuperacao (no iPhone o app instalado tem
storage separado do Safari).

Com a chave na PASTA, cada pasta tem o seu manifest com start_url dela mesma, e o
icone nasce liberado. E por isso os apps tambem sao copiados pra dentro da pasta:
a compradora instala de dentro do app que esta usando, que e o gesto natural.

Uso:  python montar-pastas.py
Depois: publicar a pasta inteira em lucroartesanato/app.
"""
import json, os, shutil

RAIZ = os.path.dirname(os.path.abspath(__file__))
BASE = 'https://lucroartesanato.github.io/app/'

# app na raiz (pasta/index.html) -> nome do arquivo dentro da pasta de acesso.
# Nenhum deles pode virar index.html: dentro da pasta esse nome e do MENU.
APPS = {
    'calculadora': 'calculadora.html',
    'catalogo':    'catalogo.html',
    'kits':        'kits.html',
    'respostas':   'respostas.html',   # entra junto do Preco Justo, sem card proprio
}
MENU = 'hub.html'

# chave -> o que ela libera. FONTE UNICA desta tabela.
# Espelha o hub.html: se mudar aqui, mude la.
NIVEIS = {
    'p':    ['preco'],                       # comprou so o front
    'pc':   ['preco', 'catalogo'],           # front + bump
    'pk':   ['preco', 'kits'],               # front + upsell (recusou o bump)
    'tudo': ['preco', 'catalogo', 'kits'],   # front + bump + upsell
}

def manifest(chave):
    """start_url e scope da PROPRIA pasta: e isso que faz o icone nascer liberado."""
    return {
        'name': 'Lucro Artesanato',
        'short_name': 'Preço Justo',
        'description': 'O preço certo de cada peça, com o seu tempo dentro da conta.',
        'start_url': BASE + chave + '/',
        'scope': BASE,
        'display': 'standalone',
        'orientation': 'portrait',
        'background_color': '#FAF6F0',
        'theme_color': '#9C5B3F',
        'icons': [
            {'src': BASE + 'favicon-96.png',  'sizes': '96x96',   'type': 'image/png'},
            {'src': BASE + 'icone-192.png',   'sizes': '192x192', 'type': 'image/png', 'purpose': 'any'},
            {'src': BASE + 'icone-512.png',   'sizes': '512x512', 'type': 'image/png', 'purpose': 'any'},
            {'src': BASE + 'icone-512.png',   'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'},
        ],
    }

def ajustar(html):
    """Dentro da pasta, os assets moram um nivel acima."""
    for a in ['favicon-96.png', 'favicon-180.png', 'icone-192.png', 'icone-512.png']:
        html = html.replace('"' + a + '"', '"../' + a + '"')
        html = html.replace("'" + a + "'", "'../" + a + "'")
    return html

def main():
    faltando = [a for a in APPS if not os.path.exists(os.path.join(RAIZ, a, 'index.html'))]
    if faltando:
        print('ERRO: app sem index.html na raiz: ' + ', '.join(faltando))
        return

    for chave in NIVEIS:
        pasta = os.path.join(RAIZ, chave)
        os.makedirs(pasta, exist_ok=True)

        # o menu vira o index.html da pasta
        with open(os.path.join(RAIZ, MENU), encoding='utf-8') as fh:
            html = ajustar(fh.read())
        with open(os.path.join(pasta, 'index.html'), 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(html)

        # os apps, pra a chave estar no caminho de QUALQUER pagina que ela abra
        for origem, destino in APPS.items():
            with open(os.path.join(RAIZ, origem, 'index.html'), encoding='utf-8') as fh:
                html = ajustar(fh.read())
            with open(os.path.join(pasta, destino), 'w', encoding='utf-8', newline='\n') as fh:
                fh.write(html)

        with open(os.path.join(pasta, 'manifest.webmanifest'), 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(manifest(chave), fh, ensure_ascii=False, indent=2)

        print('  ' + chave + '/  ->  index.html (menu) + ' + ' + '.join(APPS.values()) + ' + manifest')

    print('\nPastas montadas a partir de UMA fonte. Nunca edite dentro da pasta:')
    print('edite ' + MENU + ' ou ' + '/index.html, '.join(APPS) + '/index.html e rode de novo.')

if __name__ == '__main__':
    main()
