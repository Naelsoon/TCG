from modelos import Jogador, Carta, Pocao

class Duelo: 
    def __init__(self, sala_id: str, jogador1: Jogador, jogador2: Jogador):
        self.sala_id = sala_id
        self.p1 = jogador1
        self.p2 = jogador2
        self.turno = 1
        self.jogador_ativo = self.p1
        self.vencedor: str | None = None
        self.campo: dict[str, list[Carta]] = {
            self.p1.nickname: [],
            self.p2.nickname: []
        }

    def invocar_carta(self, jogador: Jogador, carta_id: str) -> tuple[bool, str]:
        carta = next((c for c in jogador.mao if getattr(c, 'id', None) == carta_id), None)

        if not carta or not isinstance(carta, Carta):
            return False, "Carta inválida para invocação!"

        if jogador.ether_atual < carta.custo_ether:
            return False, f"Ether insuficiente! Custo: {carta.custo_ether} | Atual: {jogador.ether_atual}"

        jogador.ether_atual -= carta.custo_ether
        jogador.mao.remove(carta)
        self.campo[jogador.nickname].append(carta)

        return True, f"{jogador.nickname} invocou [{carta.nome}]!"

    def usar_item_da_mao(self, jogador: Jogador, carta_id: str) -> tuple[bool, str]:
        item = next((c for c in jogador.mao if getattr(c, 'id', None) == carta_id), None)

        if not item or not isinstance(item, Pocao):
            return False, "Poção não encontrada!"

        if jogador.ether_atual < item.custo_ether:
            return False, f"Ether insuficiente! Custo: {item.custo_ether}"

        jogador.ether_atual -= item.custo_ether
        jogador.hp = item.usar(hp_atual=jogador.hp, max_hp=jogador.max_hp)

        jogador.mao.remove(item)
        jogador.cemiterio.append(item)

        return True, f"{jogador.nickname} usou {item.nome} e recuperou vida!"

    def realizar_ataque_direto(self, jogador_atacante: Jogador, atacante_id: str, jogador_defensor: Jogador) -> tuple[bool, str]:
        if self.campo[jogador_defensor.nickname]:
            return False, "Você não pode atacar o jogador diretamente enquanto houver criaturas no campo inimigo!"

        atacante = next((c for c in self.campo[jogador_atacante.nickname] if c.id == atacante_id), None)
        if not atacante:
            return False, "Criatura atacante não encontrada no campo!"

        if atacante.tonta:
            return False, f"{atacante.nome} sofre de mareio de invocação e não pode atacar neste turno!"
        if atacante.exausta:
            return False, f"{atacante.nome} já atacou neste turno!"

        jogador_defensor.hp = max(0, jogador_defensor.hp - atacante.ataque)
        atacante.exausta = True

        self._checar_vencedor()
        return True, f"[{atacante.nome}] atacou {jogador_defensor.nickname} diretamente causando {atacante.ataque} de dano!"

    def realizar_ataque_criatura(self, jogador_atacante: Jogador, atacante_id: str, defensora_id: str, jogador_defensor: Jogador) -> tuple[bool, str]:
        atacante = next((c for c in self.campo[jogador_atacante.nickname] if c.id == atacante_id), None)
        defensora = next((c for c in self.campo[jogador_defensor.nickname] if c.id == defensora_id), None)

        if not atacante or not defensora:
            return False, "Criatura atacante ou defensora não encontrada!"

        if atacante.tonta:
            return False, f"{atacante.nome} sofre de mareio de invocação!"
        if atacante.exausta:
            return False, f"{atacante.nome} já atacou neste turno!"

        defensora.defesa_atual -= atacante.ataque
        atacante.exausta = True

        msg = f"[{atacante.nome}] atacou [{defensora.nome}]!"

        if defensora.defesa_atual <= 0:
            self.campo[jogador_defensor.nickname].remove(defensora)
            jogador_defensor.cemiterio.append(defensora)
            msg += f" [{defensora.nome}] foi destruída!"

        return True, msg

    def passar_turno(self) -> tuple[bool, str]:
        self.jogador_ativo = self.p2 if self.jogador_ativo == self.p1 else self.p1
        self.turno += 1
        self.jogador_ativo.renovar_ether(rodada=(self.turno + 1) // 2)
        self.jogador_ativo.comprar_carta()

        for carta in self.campo[self.jogador_ativo.nickname]:
            carta.renovar_turno()

        return True, f"Turno {self.turno}: Vez de {self.jogador_ativo.nickname}"

    def _checar_vencedor(self) -> None:
        if self.p1.hp <= 0:
            self.vencedor = self.p2.nickname
        elif self.p2.hp <= 0:
            self.vencedor = self.p1.nickname

    def obter_estado(self) -> dict:
        return {
            "sala_id": self.sala_id,
            "turno": self.turno,
            "jogador_ativo": self.jogador_ativo.nickname,
            "vencedor": self.vencedor,
            "campo": {
                nick: [c.model_dump() for c in cartas]
                for nick, cartas in self.campo.items()
            },
            "p1": self.p1.model_dump(),
            "p2": self.p2.model_dump()
        }