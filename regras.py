from modelos import Jogador, Carta, Pocao

class Duelo: 
    def __init__(self, jogador1: Jogador, jogador2: Jogador):
        self.p1 = jogador1
        self.p2 = jogador2
        self.turno = 1
        self.jogador_ativo = self.p1
        self.campo: dict[str, list[Carta]] ={
           self.p1.nickname: [],
           self.p2.nickname: []
        }

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

    def invocar_carta(self, jogador:Jogador, indice_na_mao: int) -> bool:
      if indice_na_mao >= len(jogador.mao):
         print("Opção inválida, Carta não está na mão")
         return False

      carta = jogador.mao[indice_na_mao]

      if not isinstance(carta, Carta):
            print(f"{carta.nome} é uma poção/item e não pode ser invocada no campo!")
            return False

      if jogador.ether_atual < carta.custo_ether:
         print(f"Ether insuficiente! Custo: {carta.custo_ether} |Disponível: {jogador.ether_atual} ")
         return False

      jogador.ether_atual -= carta.custo_ether
      carta_baixada = jogador.mao.pop(indice_na_mao)
      self.campo[jogador.nickname].append(carta_baixada)

      print(f"{jogador.nickname} invocou [{carta_baixada.nome}] no campo! Ether restante: {jogador.ether_atual}")
      return True

    def passar_turno(self) -> None:
          self.jogador_ativo = self.p2 if self.jogador_ativo == self.p1 else self.p1
          self.turno +=1
          print(f"Turno {self.turno}: vez  de {self.jogador_ativo.nickname}")

          self.jogador_ativo.renovar_ether(rodada=(self.turno + 1) // 2)

          for carta in self.campo[self.jogador_ativo.nickname]:
            carta.novo_turno()

    def realizar_ataque_criatura(self, atacante: Carta, defensora: Carta, defensor: Jogador) -> None:
       if atacante.estilo:
          print(f"{atacante.nome} está tonta de invocação e não pode atacar!")
          return
       if atacante.condicao:
          print(f"{atacante.nome} já atacou nesse turno e está exausta!")
          return

       print(f"[{atacante.nome}] ATQ: {atacante.ataque} ataca [{defensora.nome}] DEF: {defensora.defesa}")

       if atacante.ataque >= defensora.defesa:
          print(f"{defensora.nome} foi destruida e enviada ao cemiterio de {defensor.nickname}")
          self.campo[defensor.nickname].remove(defensora)
          defensor.cemiterio.append(defensora)
       else:
         print(f"{defensora.nome} resistiu ao ataque!")

       atacante.condicao = True

    def usar_item_da_mao(self, jogador: Jogador, indice_na_mao: int) -> bool:
       if indice_na_mao >= len(jogador.mao):
          print("Item não encontrado na mão!")
          return False

       item = jogador.mao[indice_na_mao]

       if not isinstance(item, Pocao):
          print(f"{item.nome} é uma criatura e não um poção/magia")
          return False

       if jogador.ether_atual < item.custo_ether:
          print(f"Ether insuficiente para usar {item.nome}! | Custo: {item.custo_ether}")
          return False

       jogador.ether_atual -= item.custo_ether
       jogador.hp = item.usar(hp_atual=jogador.hp, max_hp=jogador.max_hp)

       item_usado = jogador.mao.pop(indice_na_mao)
       jogador.cemiterio.append(item_usado)

       print(f"{jogador.nickname} agora tem {jogador.hp}/{jogador.max_hp} HP! | Ether restante: {jogador.ether_atual}")
       return True

    def checar_vencedor(self) -> Jogador | None:
       if self.p1.hp <= 0:
          print(f"\n {self.p2.nickname} VENCEU A PARTIDA")
          return self.p2

       elif self.p2.hp <=0:
         print(f"\n {self.p1.nickname} VENCEU A PARTIDA")
         return self.p1
       return None
       