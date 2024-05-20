import numpy as np
import cv2
import sys

class Desvio:
    def __init__(self, azul, vermelho) -> None:
        self.azul = azul
        self.vermelho = vermelho

def calculaIntensidade(limAzul, desvioAzul, limVermelho, desvioVermelho):
    if desvioAzul<=limAzul and desvioVermelho<=limVermelho:
        return 1
    else:
        return 0


def montaMask(img, mask, i):
    rols, cols, channels = img.shape

    desvios = np.zeros((rols, cols, 2), np.float32)

    maiorBlue = 0
    maiorRed = 0
    count = 0
    tam_janela = 1
    count = 0

    for row in range(0, rols):
        for col in range(0, cols):
            desvioBlue = img[row,col,1] - img[row,col,0]
            desvioRed = img[row,col,1] - img[row,col,2]
            desvios[row][col][0] = desvioBlue
            desvios[row][col][1] = desvioRed
            if desvioBlue > 0 and desvioRed > 0 :
                count = count+1
                if desvioBlue > maiorBlue:
                   maiorBlue = desvioBlue
                if desvioRed > maiorRed:
                    maiorRed = desvioRed

    margemBlue = maiorBlue/2
    margemRed = maiorRed/2

    for row in range(0, rols):
        for col in range(0, cols):
            if i == 0:
                if desvios[row][col][0] > margemBlue and desvios[row][col][1] > margemRed :
                    intensidade = 0
                else:
                    intensidade = 1
            else:
                if mask[row, col, 0] != 0:
                    if desvios[row][col][0] > margemBlue and desvios[row][col][1] > margemRed :
                        intensidade = 0
                    else:
                        intensidade = 1
                else:
                    intensidade = 0

            mask[row, col, 0] = intensidade

    if i == 1:
        limAzul = maiorBlue*0.3
        limVermelho = maiorRed*0.3
        for row in range(tam_janela, rols-tam_janela):
            for col in range(tam_janela, cols-tam_janela):
                #intensidade = calculaIntensidade(maiorDesvioAzul, desvios[count].azul, maiorDesvioVermelho, desvios[count].vermelho)
                if mask[row, col, 0] == 1:
                    verif = calculaIntensidade(limAzul, desvios[row][col][0], limVermelho, desvios[row][col][1])
                    if verif == 0:
                        vizinhoNulo = False
                        for r in range(row-tam_janela, row+tam_janela):
                            for c in range(col-tam_janela, col+tam_janela):
                                if mask[r, c, 0] < 1:
                                    vizinhoNulo = True
                                    break
                            if vizinhoNulo == True:
                                break
                        if vizinhoNulo == True:
                            intensidade = (maiorBlue+maiorRed)/((desvios[row][col][0] + desvios[row][col][1])+(maiorBlue+maiorRed))
                            mask[row, col, 0] = intensidade
                            vizinhoNulo = False
        mask = cv2.blur(mask, [3,3])


    return mask

def montaSemBackground(img_out, mask):
    rows, cols, channel = img_out.shape
    #row2, col2, channel2 = background.shape


    for row in range(0, rows):
        for col in range(0, cols):
            #if row in range(0, row1) and col in range(0, col1):
            #if img[row,col,0] != 0 or img[row,col,1] != 0 or img[row,col,2] != 0:
            img_out[row, col, 1] = mask[row, col, 0]*img_out[row, col, 1]
            if mask[row, col, 0] == 0:
                img_out[row, col, 0] = 0
                img_out[row, col, 2] = 0

    return img_out


def adicionaBackground(img, background, mask):
    rows, cols, channel = img.shape
    #row2, col2, channel2 = background.shape

    background2 = cv2.resize(background, (cols, rows))

    for row in range(0, rows):
        for col in range(0, cols):
            #if row in range(0, row1) and col in range(0, col1):
            #if img[row,col,0] != 0 or img[row,col,1] != 0 or img[row,col,2] != 0:
            for c in range(0, channel):
                background2[row, col, c] = (mask[row, col, 0]*img[row, col, c]) + ((1-mask[row, col, 0])*background2[row, col, c])
    return background2

                



def main ():

    #print("\nEscolha uma imagem: ")
    background = cv2.imread ("./img/Wind Waker GC.bmp", cv2.IMREAD_COLOR)
    background = background.astype (np.float32) / 255
    #escolha = input()
    for i in range(0,9):

        n_imagem = str(i)
        print("Fazendo a imagem " + n_imagem)
        img_path = "./img/" + n_imagem + ".bmp"
        
        # Abre a imagem em escala de cinza.
        img = cv2.imread (img_path, cv2.IMREAD_COLOR)
        if img is None:
            print ('Erro abrindo a imagem.\n')
            sys.exit ()
        img = img.astype (np.float32) / 255

        img_out = img.copy()
        cv2.imwrite ('./resultados/original' + n_imagem + '.png', img_out*255)

        mask = img.copy()
        
        for i in range(0,2):
            # monta máscara
            mask = montaMask(img_out, mask, i)
            cv2.imwrite ('./resultados/mask' + str(i) + n_imagem + '.png', mask*255)

            # monta sem background
            img_out = montaSemBackground(img_out, mask)
            cv2.imwrite ('./resultados/semBackground' + str(i) + n_imagem + '.png', img_out*255)

        #junta com background
        background2 = adicionaBackground(img_out, background, mask)
        cv2.imwrite ('./resultados/final' + n_imagem + '.png', background2*255)

if __name__ == '__main__':
    main ()