import random
import timeit

# =====================================================
# Função GEN
# =====================================================
def GEN(seed):
    """
    Recebe uma seed binária e gera uma chave K
    com tamanho 4 * len(seed), de forma determinística
    e com maior mistura para reduzir chaves equivalentes.
    """
    valor = 0
    for bit in seed:
        valor = (valor << 1) | bit

    # mistura simples para aumentar entropia
    valor = valor * 1315423911

    rnd = random.Random(valor)
    tamanho = 4 * len(seed)

    return [rnd.getrandbits(1) for _ in range(tamanho)]


# =====================================================
# Função ENC
# =====================================================
def ENC(K, M):
    """
    Criptografa a mensagem M usando a chave K
    """
    if len(K) != len(M):
        raise ValueError("Chave e mensagem devem ter o mesmo tamanho")

    n = len(M)
    C = [0] * n
    prev = 0

    # XOR encadeado (difusão)
    for i in range(n):
        mi = M[i]
        C[i] = mi ^ K[i] ^ prev
        prev = mi

    # permutação circular manual (mais rápida)
    ultimo = C[-1]
    for i in range(n - 1, 0, -1):
        C[i] = C[i - 1]
    C[0] = ultimo

    return C


# =====================================================
# Função DEC
# =====================================================
def DEC(K, C):
    """
    Descriptografa a cifra C usando a chave K
    """
    if len(K) != len(C):
        raise ValueError("Chave e cifra devem ter o mesmo tamanho")

    n = len(C)

    # desfaz permutação circular
    M_temp = [0] * n
    for i in range(n - 1):
        M_temp[i] = C[i + 1]
    M_temp[-1] = C[0]

    M = [0] * n
    prev = 0

    for i in range(n):
        M[i] = M_temp[i] ^ K[i] ^ prev
        prev = M[i]

    return M


# =====================================================
# Teste de Difusão
# =====================================================
def teste_difusao(seed, mensagem, testes=20):
    """
    Mede a média de bits alterados na cifra
    ao alterar 1 bit da mensagem.
    """
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
    """
    Mede a média de bits alterados na cifra
    ao alterar 1 bit da seed.
    """
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
    """
    Verifica se chaves diferentes produzem
    a mesma cifra para a mesma mensagem.
    """
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
    """
    Mede o tempo médio de execução de GEN + ENC + DEC
    """
    def executar():
        K = GEN(seed)
        C = ENC(K, mensagem)
        DEC(K, C)

    tempo_total = timeit.timeit(
        stmt="executar()",
        globals=locals(),
        number=execucoes
    )

    return tempo_total / execucoes


# =====================================================
# Execução Principal
# =====================================================
if __name__ == "__main__":
    seed = [1, 0, 1]
    mensagem = [1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1]

    K = GEN(seed)
    C = ENC(K, mensagem)
    M_rec = DEC(K, C)

    print("Seed:", seed)
    print("Chave K:", K)
    print("Mensagem original:", mensagem)
    print("Cifra:", C)
    print("Mensagem recuperada:", M_rec)

    print("\nDifusão média (bits alterados):",
          teste_difusao(seed, mensagem))

    print("Confusão média (bits alterados):",
          teste_confusao(seed, mensagem))

    print("Chaves equivalentes encontradas:",
          teste_chaves_equivalentes(seed, mensagem))

    tempo_medio = medir_tempo(seed, mensagem)
    print(f"\nTempo médio de execução: {tempo_medio:.8f} segundos")
