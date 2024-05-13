import numpy as np
import cv2
import sys

def separaFundo(img, img_out):
    rols, cols, channels = img.shape

    rowMaior = 0
    colMaior = 0
    maiorVerde = 0



    for row in range(0, rols):
        for col in range(0, cols):
            if img[row,col,1] > img[row,col,0] and img[row,col,1] > img[row,col,2] :
                for c in range(0, channels):
                    img_out[row, col, c] = 0
    return img_out

def adicionaBackground(img, background):
    rows, cols, channel = img.shape
    #row2, col2, channel2 = background.shape

    background2 = cv2.resize(background, (cols, rows))

    for row in range(0, rows):
        for col in range(0, cols):
            #if row in range(0, row1) and col in range(0, col1):
            if img[row,col,0] != 0 or img[row,col,1] != 0 or img[row,col,2] != 0:
                for c in range(0, channel):
                    background2[row, col, c] = img[row, col, c]
    return background2

                



def main ():

    #print("\nEscolha uma imagem: ")
    background = cv2.imread ("./img/Wind Waker GC.bmp", cv2.IMREAD_COLOR)
    background = background.astype (np.float32) / 255
    #escolha = input()
    for i in range(0, 9):

        n_imagem = str(i)
        print("Fazendo a imagem " + n_imagem)
        img_path = "./img/" + n_imagem + ".bmp"
        
        # Abre a imagem em escala de cinza.
        img = cv2.imread (img_path, cv2.IMREAD_COLOR)
        if img is None:
            print ('Erro abrindo a imagem.\n')
            sys.exit ()
        img = img.astype (np.float32) / 255

        background2 = background.copy()
        img_out = img.copy()
        cv2.imwrite ('./resultados/original' + n_imagem + '.png', img_out*255)

        # faz alterações na imagem e então binariza
        img_out = separaFundo(img, img_out)
        cv2.imwrite ('./resultados/out' + n_imagem + '.png', img_out*255)

        #junta com background
        background2 = adicionaBackground(img_out, background2)
        cv2.imwrite ('./resultados/final' + n_imagem + '.png', background2*255)

if __name__ == '__main__':
    main ()