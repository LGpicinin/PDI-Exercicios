import numpy as np
import cv2
import sys


N_PIXELS_MIN = 50

class Component:
    def __init__(self, label, n_pixels, n_arroz) -> None:
        self.label = label
        self.n_pixels = n_pixels
        self.n_arroz = n_arroz
        self.oneRice = True


# calcula a média de blobs não grandes (com só um arroz) e o valor do desvio padrão mais alto
def calculaMediaPixels(dictionary, media):

    soma = 0
    count_comp = 0
    maiorDesvio = 0
    margem = media*0.6
    comp_maiorDesvio = 0

    for k in range(0, len(dictionary)):
        comp = dictionary[k]
        if comp.oneRice == True:
            desvio = comp.n_pixels - media
            if desvio < margem:
                soma = soma + comp.n_pixels
                count_comp = count_comp + 1
                if desvio > maiorDesvio:
                    maiorDesvio = desvio
                    comp_maiorDesvio = k
            else:
                comp.oneRice = False

    
    if count_comp>0:
        media = float(soma/count_comp)
        maiorDesvio = dictionary[comp_maiorDesvio].n_pixels - media
    
    return media, maiorDesvio


# calcula desvio médio entre os blobs não grandes (com só um arroz) que são maiores que a média
def calculaDesvioMédio(dictionary, media):

    count_comp = 0
    sumDesvio = 0
    desvioMedio = 0

    for k in range(0, len(dictionary)):
        comp = dictionary[k]
        if comp.oneRice == True:
            desvio = comp.n_pixels - media
            count_comp = count_comp + 1
            if desvio > 0:
                sumDesvio = sumDesvio + desvio

    if count_comp>0:
        desvioMedio = sumDesvio/count_comp
    
    return desvioMedio




def testaComponentes (dictionary, mediaPixels):


    mediaPixels, maiorDesvioAtual = calculaMediaPixels(dictionary, mediaPixels)
    desvioMedio = calculaDesvioMédio(dictionary, mediaPixels)

    while maiorDesvioAtual >= mediaPixels*0.6:
        mediaPixels, maiorDesvioAtual = calculaMediaPixels(dictionary, mediaPixels)
        desvioMedio = calculaDesvioMédio(dictionary, mediaPixels)

    
    sumPixels = mediaPixels + desvioMedio

    for i in range(0, len(dictionary)):

        comp = dictionary[i]
        comp.n_arroz = 1
        countPixels = mediaPixels+maiorDesvioAtual

        while comp.n_pixels > countPixels:
       
            countPixels = countPixels + sumPixels
            comp.n_arroz = comp.n_arroz + 1



def inunda (img, row, col, comp: Component, lenCol, lenRow):

    filaRow = []
    filaCol = []
    filaRow.append(row)
    filaCol.append(col)

    img[row, col] = comp.label
    comp.n_pixels = comp.n_pixels + 1

    while len(filaRow) > 0:
        
        row = filaRow.pop(0)
        col = filaCol.pop(0)


        if (row+1 in range(0, lenRow)):
            if img[row+1, col] == 1:
                img[row+1, col] = comp.label
                comp.n_pixels = comp.n_pixels + 1
                filaCol.append(col)
                filaRow.append(row+1)

        if (col+1 in range(0, lenCol)):
            if img[row, col+1] == 1:
                img[row, col+1] = comp.label
                comp.n_pixels = comp.n_pixels + 1
                filaCol.append(col+1)
                filaRow.append(row)

        if (row-1 in range(0, lenRow)):
            if img[row-1, col] == 1:
                img[row-1, col] = comp.label
                comp.n_pixels = comp.n_pixels + 1
                filaCol.append(col)
                filaRow.append(row-1)

        if (col-1 in range(0, lenCol)):
            if img[row, col-1] == 1:
                img[row, col-1] = comp.label
                comp.n_pixels = comp.n_pixels + 1
                filaCol.append(col-1)
                filaRow.append(row)


def rotula (img):

    rows, cols = img.shape
    label = 2
    dictionary = []
    sum_pixels = 0

    for row in range (rows):
        for col in range (cols):
            if img[row, col] == 1:
                comp = Component(label, 0, 0)
                inunda(img, row, col, comp, cols, rows)

                if comp.n_pixels >= N_PIXELS_MIN:
                    dictionary.append(comp)
                    sum_pixels = sum_pixels + comp.n_pixels

                label = label + 1
    

    mediaPixels = sum_pixels/len(dictionary)

    return dictionary, mediaPixels


def changeImage (img, img_out):

    img_aux = img.copy

    # passa o filtro da média
    img_aux = cv2.blur(img, [101, 101])
    cv2.imwrite ('./resultados/blur.png', img_aux*255)

    # subtrai imagem original da imagem borrada
    img_out = img - img_aux
    cv2.imwrite ('./resultados/sum.png', img_out*255)

    # binariza
    ret, img_out = cv2.threshold(img_out, 0.2, 1, cv2.THRESH_BINARY)

    return img_out



def main ():

    print("\nEscolha uma imagem: ")
    escolha = input()

    img_path = "./imagens/" + escolha + ".bmp"
    
    # Abre a imagem em escala de cinza.
    img = cv2.imread (img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print ('Erro abrindo a imagem.\n')
        sys.exit ()

    img = img.astype (np.float32) / 255

    img_out = img.copy()
    cv2.imwrite ('./resultados/original.png', img_out*255)


    # faz alterações na imagem e então binariza
    img_out = changeImage(img, img_out)
    cv2.imwrite ('./resultados/out.png', img_out*255)

    # rotula a imagem
    components, mediaPixels = rotula(img_out)

    # conta quantos grãos de arroz tem em cada componente
    testaComponentes(components, mediaPixels)

    # conta número de grãos de arroz
    n_components = len(components)
    n_arroz = 0
    for i in range(0, n_components):
        n_arroz = n_arroz + components[i].n_arroz

    print("Número de grãos de arroz: " + str(n_arroz))



if __name__ == '__main__':
    main ()