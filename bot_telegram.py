import time
import telebot
from analise_premium import AnalisePremium

# TOKEN E ID DO SEU CANAL
TOKEN = "7088974821:AAFx0xVtzEnbHleQU7J66wEfVmPtghnRHs0"
CHAT_ID = "-1002270247449"

bot = telebot.TeleBot(TOKEN)

class BotEliteV3:
    def __init__(self):
        self.ia = AnalisePremium()
        self.ultimo_conferido = None
        self.wins, self.losses, self.sg, self.g1 = 0, 0, 0, 0
        self.em_alerta = False
        self.gale_ativo = False
        self.previsao_atual = None

    def enviar(self, msg):
        try: return bot.send_message(CHAT_ID, msg, parse_mode="Markdown", disable_web_page_preview=True)
        except: pass

    def monitorar(self):
        print("💎 DeepBacbo Elite V3 Online - Conferência Total Ativada")
        self.enviar("🚀 *DEEPBACBO ELITE V3 ATIVADO*\n_Monitoramento jogo-a-jogo ativado._")

        while True:
            try:
                self.ia.atualizar_banco()
                hist = self.ia.historico_completo
                
                if not hist:
                    time.sleep(2); continue

                if self.ultimo_conferido is None:
                    self.ultimo_conferido = hist[0]
                    time.sleep(2); continue

                # Identifica se houve novos jogos desde a última vez
                novos_jogos = []
                for jogo in hist:
                    if jogo == self.ultimo_conferido:
                        break
                    novos_jogos.append(jogo)

                # Processa cada novo jogo que aconteceu (do mais antigo para o mais novo)
                for jogo in reversed(novos_jogos):
                    cor_resultado = jogo[0]
                    if self.em_alerta:
                        self.validar(cor_resultado)
                    self.ultimo_conferido = jogo

                # Só busca novo sinal se não estiver esperando resultado de Gale
                if not self.em_alerta:
                    dados = self.ia.prever()
                    if dados:
                        self.alertar(dados)

                time.sleep(2) # Verifica a cada 2 segundos
            except Exception as e:
                print(f"Erro: {e}")
                time.sleep(5)

    def alertar(self, d):
        self.em_alerta = True
        self.previsao_atual = d
        cor_nome = "🔵 PLAYER (AZUL)" if d['previsao_genai'] == 'P' else "🔴 BANKER (VERMELHO)"
        
        msg = (
            f"⚡️ *{d['label']}* ⚡️\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🎯 ENTRADA: *{cor_nome}*\n"
            f"📊 ASSERTIVIDADE: `{d['probabilidade']}%`\n"
            f"🔄 PROTEÇÃO: *GALE 1*\n"
            f"⚖️ COBRIR EMPATE: `SIM`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔥 *FORÇA SG:* {d['grafico']}\n"
            f"📍 [CLIQUE AQUI PARA APOSTAR](https://go.aff.esportiva.bet/sm9dwy54)"
        )
        self.enviar(msg)

    def validar(self, res):
        alvo = self.previsao_atual['previsao_genai']
        
        # 1. Caso de Green na cor certa
        if res == alvo:
            if self.gale_ativo:
                self.g1 += 1
                self.finalizar("✅ **GREEN NO GALE 1!** 🔄", res)
            else:
                self.sg += 1
                self.finalizar("✅ **GREEN DE PRIMEIRA!** 🔥", res)
        
        # 2. Caso de Empate (Tie) - Considerado Green de Cobertura
        elif res == 'T':
            self.finalizar("⚖️ **GREEN NO EMPATE!** (COBERTURA)", res)
            self.wins += 1 # Opcional: remover se não quiser contar empate no placar
        
        # 3. Caso de Erro na primeira entrada -> Entra em Gale
        elif not self.gale_ativo:
            self.gale_ativo = True
            self.enviar("🔄 *ENTRANDO NO GALE 1...*")
        
        # 4. Caso de Erro no Gale -> Red
        else:
            self.losses += 1
            self.finalizar("❌ **RED (STOP G1)**", res)

    def finalizar(self, txt, res_cor):
        if "GREEN" in txt: self.wins += 1
        
        emoji = "🔵" if res_cor == 'P' else "🔴" if res_cor == 'B' else "🟡"
        taxa = (self.wins / (self.wins + self.losses)) * 100 if (self.wins + self.losses) > 0 else 0
        
        msg = (
            f"{txt}\n"
            f"Resultado: {emoji}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📈 *PLACAR DA SESSÃO:*\n"
            f"✅ WINS: `{self.wins}` (SG: {self.sg} | G1: {self.g1})\n"
            f"❌ REDS: `{self.losses}` | 📊 TAXA: `{taxa:.1f}%`\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        self.enviar(msg)
        self.em_alerta = False
        self.gale_ativo = False

if __name__ == "__main__":
    BotEliteV3().monitorar()