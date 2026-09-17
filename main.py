from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from modelos import Jogador, Carta, Pocao, Deck
from regras import Duelo

app = FastAPI(title="TCG Card Game API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

partida_ativa: Duelo | None = None

class IniciarPartidaRequest(BaseModel):
    nickname_p1: str
    nickname_p2: str

class AcaoCartaRequest(BaseModel):
    indice_na_mao: int

def criar_deck_padrao() -> Deck:
    return Deck(cartas=[
        Carta(nome="Gato Gatuno", custo_ether=1, ataque=3, defesa=1),
        Carta(nome="Guerreiro de Aço", custo_ether=2, ataque=5, defesa=3),
        Carta(nome="Mago Supremo", custo_ether=3, ataque=7, defesa=2),
        Carta(nome="Lobo Selvagem", custo_ether=1, ataque=4, defesa=1),
        Carta(nome="Escudeiro Real", custo_ether=2, ataque=3, defesa=5),
        Carta(nome="Dragão Menor", custo_ether=3, ataque=8, defesa=4)
    ])

def serializar_item(item):
    """Converte cartas e poções em dicionários detalhados para o Front-end."""
    if isinstance(item, Carta):
        return {
            "tipo": "carta",
            "nome": item.nome,
            "custo_ether": item.custo_ether,
            "ataque": item.ataque,
            "defesa": item.defesa,
            "estilo": item.estilo,      # True = Tonta
            "condicao": item.condicao   # True = Exausta
        }
    elif isinstance(item, Pocao):
        return {
            "tipo": "pocao",
            "nome": item.nome,
            "custo_ether": item.custo_ether,
            "cura": item.cura,
            "quantidade": item.quantidade
        }
    return {}

@app.post("/partida/iniciar", status_code=201)
def iniciar_partida(payload: IniciarPartidaRequest):
    global partida_ativa

    p1 = Jogador(nickname=payload.nickname_p1, deck=criar_deck_padrao())
    p2 = Jogador(nickname=payload.nickname_p2, deck=criar_deck_padrao())

    p1.deck.embaralhar()
    p2.deck.embaralhar()

    p1.mao.append(Pocao(nome="Poção de Cura", cura=10, custo_ether=1))
    p2.mao.append(Pocao(nome="Poção de Cura", cura=10, custo_ether=1))

    p1.comprar_carta()
    p1.comprar_carta()
    p2.comprar_carta()
    p2.comprar_carta()

    partida_ativa = Duelo(jogador1=p1, jogador2=p2)

    return {"mensagem": "Partida iniciada!"}

@app.get("/partida/estado")
def obter_estado():
    if not partida_ativa:
        raise HTTPException(status_code=400, detail="Nenhuma partida ativa.")

    p1 = partida_ativa.p1
    p2 = partida_ativa.p2

    return {
        "turno": partida_ativa.turno,
        "jogador_ativo": partida_ativa.jogador_ativo.nickname,
        "jogadores": {
            p1.nickname: {
                "hp": p1.hp,
                "max_hp": p1.max_hp,
                "ether": p1.ether_atual,
                "max_ether": p1.max_ether,
                "mao": [serializar_item(i) for i in p1.mao],
                "campo": [serializar_item(c) for c in partida_ativa.campo[p1.nickname]]
            },
            p2.nickname: {
                "hp": p2.hp,
                "max_hp": p2.max_hp,
                "ether": p2.ether_atual,
                "max_ether": p2.max_ether,
                "mao": [serializar_item(i) for i in p2.mao],
                "campo": [serializar_item(c) for c in partida_ativa.campo[p2.nickname]]
            }
        }
    }

@app.post("/partida/invocar")
def invocar_carta(payload: AcaoCartaRequest):
    if not partida_ativa:
        raise HTTPException(status_code=400, detail="Nenhuma partida ativa.")

    jogador = partida_ativa.jogador_ativo
    sucesso = partida_ativa.invocar_carta(jogador=jogador, indice_na_mao=payload.indice_na_mao)

    if not sucesso:
        raise HTTPException(status_code=400, detail="Não foi possível jogar esta carta.")

    return {"mensagem": "Jogada realizada!"}

@app.post("/partida/passar-turno")
def passar_turno():
    if not partida_ativa:
        raise HTTPException(status_code=400, detail="Nenhuma partida ativa.")

    partida_ativa.passar_turno()
    partida_ativa.jogador_ativo.comprar_carta()

    return {"mensagem": "Turno passado!"}