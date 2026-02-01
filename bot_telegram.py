import os
import time
import telebot
import requests
from analise_premium import AnalisePremium

# Puxa os dados das Configurações Secretas do GitHub
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

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
        print("💎 DeepBacbo Elite V3 Online")
        while True:
            try:
                self.ia.atualizar_banco()
                hist = self.ia.historico_completo
                if not hist:
                    time.sleep(2); continue

                if self.ultimo_conferido is None:
                    self.ultimo_conferido = hist[0]
                    time.sleep(2); continue

                novos_jogos = []
                for jogo in hist:
                    if jogo == self.ultimo_conferido: break
                    novos_jogos.append(jogo)

                for jogo in reversed(novos_jogos):
                    if self.em_alerta: self.validar(jogo[0])
                    self.ultimo_conferido = jogo

                if not self.em_alerta:
                    dados = self.ia.prever()
                    if dados: self.alertar(dados)

                time.sleep(2)
            except Exception as e:
                print(f"Erro: {e}")
                time.sleep(5)

    def alertar(self, d):
        self.em_alerta = True
        self.previsao_atual = d
        cor_nome = "🔵 AZUL" if d['previsao_genai'] == 'P' else "🔴 VERMELHO"
        msg = f"🎯 *ENTRADA:* {cor_nome}\n📊 *ASSERTIVIDADE:* {d['probabilidade']}%"
        self.enviar(msg)

    def validar(self, res):
        alvo = self.previsao_atual['previsao_genai']
        if res == alvo or res == 'T':
            status = "✅ GREEN!"
            self.wins += 1
            self.finalizar(status)
        elif not self.gale_ativo:
            self.gale_ativo = True
            self.enviar("🔄 *GALE 1*")
        else:
            self.losses += 1
            self.finalizar("❌ RED")

    def finalizar(self, txt):
        msg = f"{txt}\n📊 PLACAR: {self.wins}W - {self.losses}L"
        self.enviar(msg)
        self.em_alerta, self.gale_ativo = False, False

if __name__ == "__main__":
    BotEliteV3().monitorar()
