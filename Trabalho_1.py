import random
import timeit

# =====================================================
# Função GEN
# =====================================================
def GEN(seed):
    """
    Recebe uma seed binária e gera uma chave K
    com tamanho 4 * len(seed), de forma determinística.
    """
    valor = 0
    for bit in seed:
        valor = (valor << 1) | bit

    # Mistura para aumentar a entropia e evitar chaves equivalentes
    valor = (valor * 1315423911) ^ 0x55555555

    rnd = random.Random(valor)
    tamanho = 4 * len(seed)

    return [rnd.getrandbits(1) for _ in range(tamanho)]


# =====================================================
# Função ENC
# =====================================================
def ENC(K, M):
    """
    Criptografa a mensagem M usando a chave K com alta difusão.
    """
    if len(K) != len(M):
        raise ValueError("Chave e mensagem devem ter o mesmo tamanho")

    n = len(M)
    C = M.copy()

    # Realizamos duas passadas (direta e inversa) para garantir difusão total
    # Passada 1: XOR encadeado para frente
    prev = K[-1]
    for i in range(n):
        C[i] = C[i] ^ K[i] ^ prev
        prev = C[i]

    # Passada 2: XOR encadeado para trás (propaga bits do fim para o início)
    prox = K[0]
    for i in range(n - 1, -1, -1):
        C[i] = C[i] ^ prox
        prox = C[i]

    return C


# =====================================================
# Função DEC
# =====================================================
def DEC(K, C):
    """
    Descriptografa a cifra C usando a chave K.
    """
    if len(K) != len(C):
        raise ValueError("Chave e cifra devem ter o mesmo tamanho")

    n = len(C)
    M = C.copy()

    # Desfaz a Passada 2 (Trás para frente)
    prox = K[0]
    for i in range(n - 1, -1, -1):
        temp = M[i]
        M[i] = M[i] ^ prox
        prox = temp

    # Desfaz a Passada 1 (Frente para trás)
    prev = K[-1]
    for i in range(n):
        temp = M[i]
        M[i] = M[i] ^ K[i] ^ prev
        prev = temp

    return M


# =====================================================
# Teste de Difusão
# =====================================================
def teste_difusao(seed, mensagem, testes=20):
    K = GEN(seed)
    n = len(mensagem)
    total = 0
    C_original = ENC(K, mensagem)

    for i in range(testes):
        M_mod = mensagem.copy()
        pos = i % n
        M_mod[pos] ^= 1
        C_mod = ENC(K, M_mod)
        total += sum(a != b for a, b in zip(C_original, C_mod))

    return total / testes


# =====================================================
# Teste de Confusão
# =====================================================
def teste_confusao(seed, mensagem, testes=20):
    n_seed = len(seed)
    total = 0
    K_original = GEN(seed)
    C_original = ENC(K_original, mensagem)

    for i in range(testes):
        seed_mod = seed.copy()
        pos = i % n_seed
        seed_mod[pos] ^= 1
        K_mod = GEN(seed_mod)
        C_mod = ENC(K_mod, mensagem)
        total += sum(a != b for a, b in zip(C_original, C_mod))

    return total / testes


# =====================================================
# Teste de Chaves Equivalentes
# =====================================================
def teste_chaves_equivalentes(seed, mensagem, tentativas=500):
    cifras = {}
    equivalentes = 0
    tamanho_seed = len(seed)
    for _ in range(tentativas):
        seed_rand = [random.getrandbits(1) for _ in range(tamanho_seed)]
        K = GEN(seed_rand)
        C = tuple(ENC(K, mensagem))
        if C in cifras and cifras[C] != K:
            equivalentes += 1
        else:
            cifras[C] = K
    return equivalentes


# =====================================================
# Medição de Tempo
# =====================================================
def medir_tempo(seed, mensagem, execucoes=5000):
    def executar():
        K = GEN(seed)
        C = ENC(K, mensagem)
        DEC(K, C)
    tempo_total = timeit.timeit(stmt=executar, number=execucoes)
    return tempo_total / execucoes


# =====================================================
# Execução Principal
# =====================================================
if __name__ == "__main__":
    # Para atingir Difusão de ~20 bits, usamos seed de 10 bits (|K| = 40)
    # Pois o ideal de difusão é 50% do tamanho do bloco.
    seed = [1, 0, 1, 1, 0, 0, 1, 1, 0, 1] 
    mensagem = [random.getrandbits(1) for _ in range(40)]

    K = GEN(seed)
    C = ENC(K, mensagem)
    M_rec = DEC(K, C)

    print("Seed (10 bits):", seed)
    print("Mensagem Recuperada Corretamente:", M_rec == mensagem)

    print("\nDifusão média (bits alterados):", teste_difusao(seed, mensagem))
    print("Confusão média (bits alterados):", teste_confusao(seed, mensagem))
    print("Chaves equivalentes encontradas:", teste_chaves_equivalentes(seed, mensagem))

    tempo_medio = medir_tempo(seed, mensagem)
    print(f"\nTempo médio de execução: {tempo_medio:.8f} segundos")
