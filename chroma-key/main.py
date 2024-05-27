import numpy as np
import cv2
import sys


def montaMask(img, mask):
    rols, cols, channels = img.shape

    for row in range(0, rols):
        for col in range(0, cols):
            intensidade = 1
            maior = img[row,col,0]
            if img[row,col,2] > maior:
                maior = img[row,col,2]
            dif = img[row,col,1] - maior
            if dif > 0.1:
                if dif <= 0.3:
                    aux = 0.101
                    while aux <= dif:
                        intensidade = intensidade - 0.05
                        aux = aux + 0.01
                else:
                    intensidade = 0
            for c in range(0, channels):
                mask[row, col, c] = intensidade
            
    return mask


def montaSemBackground(img_out, mask):
    rows, cols, channel = img_out.shape


    for row in range(0, rows):
        for col in range(0, cols):
            for c in range(0, channel):
                img_out[row, col, c] = mask[row, col, 0]*img_out[row, col, c]
            if mask[row, col, 0] > 0:
                maior = img_out[row,col,0]
                if img_out[row,col,2] > maior:
                    maior = img_out[row,col,2]
                dif = img_out[row,col,1] - maior
                if dif > 0:
                    img_out[row, col, 1] = maior

    return img_out


def adicionaBackground(img, background, mask):
    rows, cols, channel = img.shape

    background2 = cv2.resize(background, (cols, rows))

    for row in range(0, rows):
        for col in range(0, cols):
            for c in range(0, channel):
                background2[row, col, c] = (mask[row, col, 0]*img[row, col, c]) + ((1-mask[row, col, 0])*background2[row, col, c])
    return background2


def main ():

    background = cv2.imread ("./img/Wind Waker GC.bmp", cv2.IMREAD_COLOR)
    background = background.astype (np.float32) / 255

    for i in range(0,9):

        n_imagem = str(i)
        print("Fazendo a imagem " + n_imagem)
        img_path = "./img/" + n_imagem + ".bmp"
        
        # Abre a imagem.
        img = cv2.imread (img_path, cv2.IMREAD_COLOR)
        if img is None:
            print ('Erro abrindo a imagem.\n')
            sys.exit ()
        img = img.astype (np.float32) / 255

        img_out = img.copy()
        cv2.imwrite ('./resultados/' + n_imagem + '-original.png', img_out*255)

        mask = img.copy()
        
        # monta máscara
        mask = montaMask(img_out, mask)
        cv2.imwrite ('./resultados/' + n_imagem + '-mask.png', mask*255)

        # monta sem background
        img_out = montaSemBackground(img_out, mask)
        cv2.imwrite ('./resultados/' + n_imagem + '-semBackground.png', img_out*255)

        #junta com background
        background2 = adicionaBackground(img_out, background, mask)
        cv2.imwrite ('./resultados/' + n_imagem + '-final.png', background2*255)

if __name__ == '__main__':
    main ()