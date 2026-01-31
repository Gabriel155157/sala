import requests
import os

class AnalisePremium:
    def __init__(self):
        self.historico_completo = [] 
        self.URL_API = "https://locabot.online/api_bacbo.php"
        self.arquivo_log = "padroes_vencedores.txt"
        self.padroes_ouro = self._carregar_padroes_ouro()
        
        self.ASSERTIVIDADE_MINIMA = 80.0
        self.AMOSTRA_MINIMA = 3          
        self.TAMANHO_MAX_PADRAO = 4 # Padrões menores são mais rápidos e eficazes

    def _carregar_padroes_ouro(self):
        if not os.path.exists(self.arquivo_log):
            return set()
        with open(self.arquivo_log, "r") as f:
            return set(linha.strip() for linha in f if linha.strip())

    def _salvar_padrao_ouro(self, txt_gatilho):
        if txt_gatilho not in self.padroes_ouro:
            self.padroes_ouro.add(txt_gatilho)
            with open(self.arquivo_log, "a") as f:
                f.write(f"{txt_gatilho}\n")
            return True
        return False

    def gerar_barra(self, percentual):
        blocos = int(percentual / 10)
        return "🟦" * blocos + "⬜" * (10 - blocos)

    def atualizar_banco(self):
        try:
            response = requests.get(self.URL_API, timeout=5)
            if response.status_code != 200: return
            data = response.json()
            if not data: return
            
            # Inverte para que o índice 0 seja o MAIS RECENTE
            self.historico_completo = []
            for x in data[::-1]: 
                cor = 'P' if x['pedra'] == 'Player' else 'B' if x['pedra'] == 'Banker' else 'T'
                num = int(x['numero'])
                self.historico_completo.append((cor, num))
        except Exception: 
            pass

    def prever(self):
        if len(self.historico_completo) < 15: return None
        
        for tamanho in range(2, self.TAMANHO_MAX_PADRAO + 1):
            padrao_atual = self.historico_completo[:tamanho]
            txt_gatilho = "-".join([f"{c}{n}" for c, n in padrao_atual[::-1]])
            
            total_encontrado = 0
            stats_p = {'sg': 0, 'g1': 0}
            stats_b = {'sg': 0, 'g1': 0}
            empates = 0
            
            limite = len(self.historico_completo) - tamanho - 3
            for i in range(1, limite):
                if self.historico_completo[i : i + tamanho] == padrao_atual:
                    total_encontrado += 1
                    # Verifica SG
                    if self.historico_completo[i-1][0] == 'P': stats_p['sg'] += 1
                    elif self.historico_completo[i-1][0] == 'B': stats_b['sg'] += 1
                    elif self.historico_completo[i-1][0] == 'T': empates += 1
                    
                    # Verifica G1
                    if self.historico_completo[i-1][0] != 'P' and self.historico_completo[i-2][0] == 'P': stats_p['g1'] += 1
                    if self.historico_completo[i-1][0] != 'B' and self.historico_completo[i-2][0] == 'B': stats_b['g1'] += 1

            if total_encontrado >= self.AMOSTRA_MINIMA:
                prob_p = ((stats_p['sg'] + stats_p['g1']) / total_encontrado) * 100
                prob_b = ((stats_b['sg'] + stats_b['g1']) / total_encontrado) * 100
                
                previsao = 'P' if prob_p >= self.ASSERTIVIDADE_MINIMA else 'B' if prob_b >= self.ASSERTIVIDADE_MINIMA else None
                
                if previsao:
                    stats = stats_p if previsao == 'P' else stats_b
                    prob_final = prob_p if previsao == 'P' else prob_b
                    p_sg = (stats['sg'] / total_encontrado) * 100
                    
                    if p_sg < 40: continue # Evita padrões que dependem demais de Gale

                    label = "💎 PADRÃO OURO" if txt_gatilho in self.padroes_ouro else "🔥 SINAL CONFIRMADO"
                    if prob_final >= 100: self._salvar_padrao_ouro(txt_gatilho)
                    
                    return {
                        "previsao_genai": previsao,
                        "probabilidade": round(prob_final, 1),
                        "gatilho": txt_gatilho,
                        "p_sg": p_sg,
                        "label": label,
                        "grafico": self.gerar_barra(p_sg)
                    }
        return None