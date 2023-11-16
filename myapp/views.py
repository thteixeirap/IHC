# myapp/views.py
from django.shortcuts import render
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64
import skfuzzy as fuzzy
import random

def triangular(x, a, m, b):
    y = maximo((minimo(((x-a)/(m-a), (b-x)/(b-m))), 0))
    return y

def maximo(x):
    maior = 0
    for i in x:
        if i > maior:
            maior = i
    return maior

def minimo(x):
    menor = x[0]
    for i in x:
        if i < menor:
            menor = i
    return menor

def home(request):
    return render(request, 'home.html')

def get_fuzzy_graphs(taxa_limiar):
    vazao = list()
    lista = []
    for i in range(0, 5000):
        lista.append((i))

    atual = 0
    entrada = list()
    total = list()
    total.append(0)
    for i in lista:
        entrada.append(atual/15)
        if (i > 1000):
            continue
        decisao = random.randint(0, 2)
        if (decisao == 2 and atual < 15):
            atual += 1
        elif (decisao == 0 and atual > 0):
            atual -= 1
    for i in range(1, len(lista)+1):
        total.append(entrada[i-1]+total[i-1])

    positivoGrande = list()
    errozero = list()
    negativoGrande = list()

    # Erro de 80 a -100
    erroList = []
    for i in range(0, 200):
        erroList.append((i-100))
    for i in erroList:
        positivoGrande.append(triangular(i, -20, 100, 200))
        negativoGrande.append(triangular(i, -200, -100, 20))

    abrir = list()
    manter = list()
    fechar = list()

    erroList = []
    for i in range(0, 200):
        erroList.append((i-100))
    for i in erroList:
        abrir.append(triangular(i, -150, -100, 20))
        fechar.append(triangular(i, -20, 100, 150))

    atual = 0
    atualSaida = 0
    total = list()
    erro = list()
    limiar = list()
    total.append(0)
    for i in range(1, len(lista)+1):
        final = list()
        result2 = list()
        result3 = list()
        total.append(entrada[i-1]+total[i-1]-(atualSaida/15))
        limiar.append(taxa_limiar)
        if (total[i] >= 100):
            break
        a2 = positivoGrande[100+int(taxa_limiar-total[i-1])]
        a3 = negativoGrande[100+int(taxa_limiar-total[i-1])]
        for j in range(0, len(erroList)):
            result2.append(minimo((fechar[j], a2)))
            result3.append(minimo((abrir[j], a3)))
            final.append(maximo((result2[j], result3[j])))
        defuzzy = fuzzy.defuzz(np.array(erroList), np.array(final), 'mom')
        if (erroList[int(defuzzy)] < -10 and atualSaida > 0):
            atualSaida -= 1
        elif (erroList[int(defuzzy)] > 10 and atualSaida < 15):
            atualSaida += 1
        vazao.append(15 - atualSaida)

    total.pop(0)
        # Criação do gráfico do nível do tanque no tempo X
    fig, ax1 = plt.subplots()
    ax1.plot(lista, total, label="Nível do Tanque no tempo X")
    ax1.plot(lista, limiar, label="Limiar")
    ax1.set_title("Nível do Tanque no tempo X")
    ax1.set_xlabel("Tempo")
    ax1.set_ylabel("Nível do Tanque")
    ax1.legend(loc="upper right")
    # Renderizar o gráfico diretamente no canvas
    canvas = FigureCanvas(fig)
    buf = BytesIO()
    canvas.print_png(buf)
    image_data = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close(fig)

    return [total, vazao, image_data]

def fuzzy_graph_view(request):
    if request.method == 'POST':
        # Obtenha o nível da água selecionado pelo usuário
        taxa_limiar = float(request.POST.get('tank_level', 0))

        # Chame a função get_fuzzy_graphs para obter o gráfico fuzzy
        fuzzy_graphs = get_fuzzy_graphs(taxa_limiar)

        # Passe os dados da imagem para o template
        context = {
            'total': fuzzy_graphs[0],
            'vazao': fuzzy_graphs[1],
            'image_data': fuzzy_graphs[2],
        }
        return render(request, 'fuzzy_graphs.html', context)
    else:
        return render(request, 'home.html')
