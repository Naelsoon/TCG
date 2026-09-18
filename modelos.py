import uuid
import random
from typing import Literal
from pydantic import BaseModel, Field

class Carta(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    tipo: Literal["criatura"] = "criatura"
    nome: str
    custo_ether: int = Field(default=1, ge=0)
    ataque: int = Field(ge=0)
    defesa: int = Field(ge=0)
    defesa_atual: int = Field(default=0)
    condicao: bool = False  # True = Exausta
    estilo: bool = True     # True = Tonta 

    def model_post_init(self, __context):
        if self.defesa_atual == 0:
            self.defesa_atual = self.defesa

    def atacar(self) -> tuple[bool, str]:
        if self.estilo:
            return False, f"{self.nome} tem tontura de invocação e não pode atacar nesse turno!"
        if self.condicao:
            return False, f"{self.nome} já atacou nesse turno e está exausta!"

        self.condicao = True
        return True, f"{self.nome} atacou causando {self.ataque} de dano!"

    def novo_turno(self) -> None:
        self.estilo = False
        self.condicao = False


class Pocao(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    tipo: Literal["pocao"] = "pocao"
    nome: str
    cura: int
    quantidade: int = Field(default=1, ge=0)
    custo_ether: int = Field(default=1, ge=0)

    def usar(self, hp_atual: int, max_hp: int) -> tuple[int, bool, str]:
        if self.quantidade <= 0:
            return hp_atual, False, f"Você não tem mais {self.nome}s!"

        self.quantidade -= 1
        novo_hp = min(hp_atual + self.cura, max_hp)
        return novo_hp, True, f"Usou {self.nome}! HP recuperado."


class Deck(BaseModel):
    cartas: list[Carta | Pocao] = Field(default_factory=list)

    def embaralhar(self) -> None:
        random.shuffle(self.cartas)

    def comprar(self) -> Carta | Pocao | None:
        if not self.cartas:
            return None
        return self.cartas.pop(0)


class Jogador(BaseModel):
    sid: str = "" 
    nickname: str
    hp: int = Field(default=30, ge=0, le=30)
    max_hp: int = 30
    ether_atual: int = Field(default=1, ge=0, le=10)
    max_ether: int = 1
    deck: Deck = Field(default_factory=Deck)
    mao: list[Carta | Pocao] = Field(default_factory=list)
    cemiterio: list[Carta | Pocao] = Field(default_factory=list)

    def comprar_carta(self) -> Carta | Pocao | None:
        carta = self.deck.comprar()
        if carta:
            self.mao.append(carta)
        return carta

    def renovar_ether(self, rodada: int) -> None:
        self.max_ether = min(10, rodada)
        self.ether_atual = self.max_ether