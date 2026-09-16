from typing import Literal
from Pydantic import BaseModel, Field

class Carta(BaseModel):
    nome: str
    custo_ether: int = Field(default = 1, ge = 0)
    ataque: int      = Field(ge = 0)
    defesa: int      = Field(ge = 0)
    condicao: bool   = False #exered
    estilo:   bool   = True #dizzy

    def atacar(self) -> None:
        if self.estilo:
            print(f"{self.nome} tem tontura de invocação e não pode atacar nesse turno")
            return
        if self.condicao:
            print(f"{self.nome} já atacou nesse turno e está exausta!")
            return

        self.estilo = True
        print(f"{self.nome} atacou causando {self.ataque} de dano!")

    def novo_turno(self) -> None:
        self.estilo   = False
        self.condicao = False
        print(f"{self.nome} está pronta para o combate!")


class Pocao(BaseModel):
    nome: str
    cura: int
    quantidade: int = Field(default = 3, ge = 0)

    def usar(self, hp_atual: int, max_hp: int) -> int:
        if self.quantidade <= 0:
            print(f"Você não tem mais {self.nome}s no inventário!")
            return hp_atual

        self.quantidade -= 1
        novo_hp = min(hp_atual + self.cura, max_hp)
        print(f"Usou {self.nome}! HP recuperado. Restam {self.quantidade} unidades.")
        return novo_hp


class Armamento(BaseModel):
    nome: str
    dado_bonus:   int = Field(ge = 0)
    durabilidade: int = Field(default = 100, ge = 0)
    radidade: Literal["Comum", "Rara", "Lendária"] = "Comum"


class Pet(BaseModel):
    nome: str
    nivel: int = Field(default = 1, ge = 1)
    esta_ativo: bool = False
    habilidades: list[str] = Field(default_factory=list)


class Jogador(BaseModel):
    nickname: str
    hp: int = Field(default = 30, ge = 0, le = 30)
    max_hp: int = 30
    ether_atual: int = Field(default = 1, ge = 0, le= 10)
    max_ether: int = 10

