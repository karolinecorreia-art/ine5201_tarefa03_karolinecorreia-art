# jogo_forca.py
# INE5201 - Tarefa 03: Jogo da Forca com interface gráfica
import json
import os
import random
import unicodedata

import FreeSimpleGUI as sg   # se usar PySimpleGUI 4.60.5: import PySimpleGUI as sg

# Caminhos baseados na pasta do próprio script (funciona de qualquer lugar)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_PALAVRAS = os.path.join(BASE_DIR, "palavras.txt")
ARQUIVO_STATS = os.path.join(BASE_DIR, "estatisticas.json")
MAX_ERROS = 6
LETRAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Cores da interface (fundo azul petróleo)
COR_FUNDO = "#8B6EC7"
COR_BOTAO = "#A1AB2C"
COR_TEXTO = "#FFFEEC"
COR_ACERTO = "#90B04D"
COR_ERRO = "#D85252"
COR_DICA = "#67C5C0"
COR_MSG_ERRO = "#FF8A80"
COR_MSG_AVISO = "#FFB74D"
COR_MSG_DICA = "#80D8FF"


# ---------- ARQUIVOS E STRINGS ----------
def remover_acentos(texto):
    """Troca 'ação' por 'acao' para combinar com o teclado A-Z."""
    normalizado = unicodedata.normalize("NFD", texto)
    return "".join(c for c in normalizado if unicodedata.category(c) != "Mn")


def carregar_palavras(arquivo=ARQUIVO_PALAVRAS):
    """Lê o .txt e devolve palavras em maiúsculas, sem acentos, sem
    duplicatas, sem linhas vazias e só com letras de A a Z."""
    try:
        with open(arquivo, "r", encoding="utf-8-sig") as f:
            linhas = f.readlines()
    except OSError:
        sg.popup_error(f"Não foi possível abrir o arquivo:\n{arquivo}")
        return []

    palavras = []
    for linha in linhas:
        palavra = remover_acentos(linha.strip()).upper()
        if palavra and all(c in LETRAS for c in palavra) and palavra not in palavras:
            palavras.append(palavra)
    return palavras


def escolher_palavra(lista, anterior=None):
    """Sorteia uma palavra, evitando repetir a da partida anterior."""
    opcoes = [p for p in lista if p != anterior] or lista
    return random.choice(opcoes)


def carregar_estatisticas(arquivo=ARQUIVO_STATS):
    """Lê as estatísticas; se o arquivo não existir ou estiver inválido, zera."""
    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            dados = json.load(f)
        vitorias = dados["vitorias"]
        derrotas = dados["derrotas"]
        if type(vitorias) is int and type(derrotas) is int \
                and vitorias >= 0 and derrotas >= 0:
            return vitorias, derrotas
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return 0, 0


def salvar_estatisticas(vitorias, derrotas, arquivo=ARQUIVO_STATS):
    """Grava em arquivo temporário e depois troca, para não corromper.
    Devolve True se salvou e False se deu erro."""
    temporario = arquivo + ".tmp"
    try:
        with open(temporario, "w", encoding="utf-8") as f:
            json.dump({"vitorias": vitorias, "derrotas": derrotas}, f)
        os.replace(temporario, arquivo)
        return True
    except OSError:
        return False


def texto_estatisticas(vitorias, derrotas):
    total = vitorias + derrotas
    taxa = 100 * vitorias / total if total else 0
    return (f"Partidas: {total} | Vitórias: {vitorias} | "
            f"Derrotas: {derrotas} | Aproveitamento: {taxa:.0f}%")


# ---------- LÓGICA ----------
def atualizar_display(palavra, letras_tentadas):
    """Ex.: PYTHON com {P, T} -> 'P _ T _ _ _'"""
    return " ".join(l if l in letras_tentadas else "_" for l in palavra)


def verificar_vitoria(palavra, letras_tentadas):
    return all(l in letras_tentadas for l in palavra)


def letras_ocultas(palavra, letras_tentadas):
    """Letras da palavra ainda não descobertas, em ordem alfabética."""
    return sorted(l for l in set(palavra) if l not in letras_tentadas)


def letras_erradas(palavra, letras_tentadas):
    return sorted(l for l in letras_tentadas if l not in palavra)


# ---------- DESENHO ----------
def desenhar_boneco(grafico, erros):
    """Desenha a forca e uma parte do corpo por erro (6 no total)."""
    grafico.erase()
    grafico.draw_line((20, 20), (120, 20), width=4)     # base
    grafico.draw_line((70, 20), (70, 230), width=4)     # poste
    grafico.draw_line((70, 230), (140, 230), width=4)   # topo
    grafico.draw_line((140, 230), (140, 205), width=3)  # corda
    if erros >= 1:
        grafico.draw_circle((140, 190), 15, line_color="black", line_width=3)  # cabeça
    if erros >= 2:
        grafico.draw_line((140, 175), (140, 115), width=3)   # tronco
    if erros >= 3:
        grafico.draw_line((140, 165), (110, 140), width=3)   # braço esquerdo
    if erros >= 4:
        grafico.draw_line((140, 165), (170, 140), width=3)   # braço direito
    if erros >= 5:
        grafico.draw_line((140, 115), (115, 75), width=3)    # perna esquerda
    if erros >= 6:
        grafico.draw_line((140, 115), (165, 75), width=3)    # perna direita


# ---------- INTERFACE ----------
def aplicar_tema():
    """Define o fundo azul petróleo e as cores padrão dos elementos."""
    sg.theme_background_color(COR_FUNDO)
    sg.theme_element_background_color(COR_FUNDO)
    sg.theme_text_element_background_color(COR_FUNDO)
    sg.theme_text_color(COR_TEXTO)
    sg.theme_button_color((COR_TEXTO, COR_BOTAO))


def montar_layout(vitorias, derrotas):
    teclado = []
    for i in range(0, 26, 9):
        teclado.append([sg.Button(l, key=f"-L{l}-", size=(3, 1), pad=(2, 2),
                                  disabled=True)
                        for l in LETRAS[i:i + 9]])

    return [
        [sg.Text("JOGO DA FORCA", font=("Helvetica", 20), justification="center",
                 expand_x=True)],
        [sg.Graph((200, 250), (0, 0), (200, 250), background_color="white",
                  key="-GRAFICO-")],
        [sg.Text("Clique em 'Novo Jogo'", font=("Courier", 28), key="-PALAVRA-")],
        [sg.Text("Tentativas restantes: 6", font=("Helvetica", 12), key="-TENT-")],
        [sg.Text("Letras erradas: -", font=("Helvetica", 11), size=(40, 1),
                 key="-ERRADAS-")],
        [sg.Text("", font=("Helvetica", 14, "bold"), size=(40, 1), key="-MSG-")],
        *teclado,
        [sg.Button("Novo Jogo"), sg.Button("Desistir", disabled=True),
         sg.Button("Dicas (1)", key="Dicas", disabled=True), sg.Button("Sair")],
        [sg.Text(texto_estatisticas(vitorias, derrotas), key="-STATS-")],
    ]


def confirmar(mensagem):
    return sg.popup_yes_no(mensagem, title="Confirmar", keep_on_top=True) == "Yes"


def mostrar_vitoria(palavra):
    """Tela à parte que aparece quando o jogador vence."""
    sg.popup("Parabéns, você venceu!", f"A palavra era: {palavra}",
             title="Vitória!", font=("Helvetica", 14), keep_on_top=True)


def habilitar_teclado(window, ativo):
    for l in LETRAS:
        window[f"-L{l}-"].update(disabled=not ativo)


def resetar_teclado(window):
    for l in LETRAS:
        window[f"-L{l}-"].update(disabled=False,
                                 button_color=sg.theme_button_color())


def atualizar_tela(window, e):
    erradas = letras_erradas(e["palavra"], e["tentadas"])
    window["-PALAVRA-"].update(atualizar_display(e["palavra"], e["tentadas"]))
    window["-TENT-"].update(f"Tentativas restantes: {MAX_ERROS - e['erros']}")
    window["-ERRADAS-"].update("Letras erradas: " + (", ".join(erradas) or "-"))
    window["-STATS-"].update(texto_estatisticas(e["vitorias"], e["derrotas"]))
    desenhar_boneco(window["-GRAFICO-"], e["erros"])


def novo_jogo(window, e, palavras):
    e.update(palavra=escolher_palavra(palavras, e["palavra"]), tentadas=set(),
             erros=0, ativo=True, dica_usada=False)
    window["-MSG-"].update("")
    resetar_teclado(window)
    window["Desistir"].update(disabled=False)
    window["Dicas"].update("Dicas (1)", disabled=False)
    atualizar_tela(window, e)


def encerrar(window, e, venceu, desistiu=False):
    e["ativo"] = False
    if venceu:
        e["vitorias"] += 1
        window["-MSG-"].update("")      # a vitória aparece em tela separada
    else:
        e["derrotas"] += 1
        texto = "Você desistiu!" if desistiu else "Você perdeu!"
        window["-MSG-"].update(f"{texto} A palavra era: {e['palavra']}",
                               text_color=COR_MSG_ERRO)
    if not salvar_estatisticas(e["vitorias"], e["derrotas"]):
        sg.popup("Não foi possível salvar as estatísticas em arquivo.",
                 title="Aviso", keep_on_top=True)
    window["-PALAVRA-"].update(" ".join(e["palavra"]))
    window["-STATS-"].update(texto_estatisticas(e["vitorias"], e["derrotas"]))
    habilitar_teclado(window, False)
    window["Desistir"].update(disabled=True)
    window["Dicas"].update(disabled=True)
    if venceu:
        window.refresh()                # mostra a palavra completa antes do popup
        mostrar_vitoria(e["palavra"])


def jogar_letra(window, e, letra):
    if letra in e["tentadas"]:
        window["-MSG-"].update(f"Você já tentou '{letra}'!",
                               text_color=COR_MSG_AVISO)
        return
    e["tentadas"].add(letra)
    acertou = letra in e["palavra"]
    window[f"-L{letra}-"].update(
        disabled=True,
        button_color=(COR_TEXTO, COR_ACERTO if acertou else COR_ERRO))
    if acertou:
        window["-MSG-"].update("")
    else:
        e["erros"] += 1
    atualizar_tela(window, e)
    if verificar_vitoria(e["palavra"], e["tentadas"]):
        encerrar(window, e, venceu=True)
    elif e["erros"] >= MAX_ERROS:
        encerrar(window, e, venceu=False)


def dar_dica(window, e):
    """1 dica por partida: revela uma letra ainda oculta (sem custo de erro)."""
    if e["dica_usada"] or not e["ativo"]:
        return
    ocultas = letras_ocultas(e["palavra"], e["tentadas"])
    if not ocultas:
        return
    e["dica_usada"] = True
    window["Dicas"].update("Dicas (0)", disabled=True)
    letra = random.choice(ocultas)
    jogar_letra(window, e, letra)
    if e["ativo"]:
        window[f"-L{letra}-"].update(button_color=(COR_TEXTO, COR_DICA))
        window["-MSG-"].update(f"Dica: a letra {letra} foi revelada!",
                               text_color=COR_MSG_DICA)


# ---------- MAIN ----------
def main():
    aplicar_tema()
    palavras = carregar_palavras(ARQUIVO_PALAVRAS)
    if not palavras:
        return
    vitorias, derrotas = carregar_estatisticas()
    estado = {"palavra": "", "tentadas": set(), "erros": 0, "ativo": False,
              "dica_usada": False, "vitorias": vitorias, "derrotas": derrotas}

    window = sg.Window("Jogo da Forca - INE5201", montar_layout(vitorias, derrotas),
                       finalize=True, element_justification="center",
                       return_keyboard_events=True)
    desenhar_boneco(window["-GRAFICO-"], 0)

    # loop de eventos da GUI
    while True:
        event, _ = window.read()
        if event in (sg.WIN_CLOSED, "Sair"):
            break
        if event == "Novo Jogo":
            if estado["ativo"]:
                if not confirmar("Há uma partida em andamento.\n"
                                 "Começar outra? (a atual conta como derrota)"):
                    continue
                encerrar(window, estado, venceu=False, desistiu=True)
            novo_jogo(window, estado, palavras)
        elif event == "Desistir" and estado["ativo"]:
            if confirmar("Tem certeza que deseja desistir?"):
                encerrar(window, estado, venceu=False, desistiu=True)
        elif event == "Dicas" and estado["ativo"]:
            dar_dica(window, estado)
        elif event.startswith("-L") and estado["ativo"]:
            jogar_letra(window, estado, event[2])        # "-LA-" -> "A"
        elif len(event) == 1 and event.upper() in LETRAS and estado["ativo"]:
            jogar_letra(window, estado, event.upper())   # teclado físico
    window.close()


if __name__ == "__main__":
    main()