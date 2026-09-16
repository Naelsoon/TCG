from modelos import Jogador, Carta

class Duelo: 
    def __init__(self, jogador1: Jogador, jogador2: Jogador):
        self.p1 = jogador1
        self.p2 = jogador2
        self.turno = 1
        self.jogador_ativo = self.p1

    def realizar_ataque_direto(self, carta: Carta, alvo: Jogador) -> None:
     if  carta.estilo:
        print(f"{carta.nome} está tonta e não pode atacar nesse turno")
        return
     if carta.condicao:
        print(f"{carta.nome} já atacou!")
        return

     alvo.hp = max(0, alvo.hp - carta.ataque)
     carta.condicao = True

     print(f"{carta.nome} atacou {alvo.nickname} diretamente!")
     print(f"HP de {alvo.nickname}: {alvo.hp}/{alvo.max_hp}")

    def passar_turno(self) -> None:
       self.jogador_ativo = self.p2 if self.jogador_ativo == self.p1 else self.p1