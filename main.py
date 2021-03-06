from io import open
import os
import re
from cmd import Cmd
import binaryEncryptionMethods as Bem
import manageFile as mf
os.system('clear')

class cipherFeedBack(Cmd):
    def __init__(self):
        super().__init__()
        try:
            plainTextClean = mf.readFile('PlainText.txt','a')
        except LookupError:
            print('ERROR: File error.')
        else:
            self.plainText = plainTextClean

        # * Read configFile.txt
        try:
            iv = ''
            with open("configFile.txt","r") as configFile:
                for variables in configFile:
                    v2 = re.match(r".*#### accion: ([a-z]*)",variables)
                    if v2:
                        action = (v2.group(1))
                        if action == 'e' or action == 'd':
                            pass
                        else:
                            print(f'ERROR: acción de encriptado invalido.')
                            exit()
                    v3 = re.match(r".*#### metodo: ([1-3]*)",variables)
                    if v3:
                        method = (v3.group(1))
                        if method == '1' or method == '2' or method == '3':
                            pass
                        else:
                            print(f'ERROR: método invalido.')
                            exit()
                    v4 = re.match(r".*#### llave: ([-0-9]*)",variables)
                    if v4:
                        llaveg = (v4.group(1))

                    v5 = re.match(r".*#### IV: (\w*)",variables)
                    if v5:
                        iv = (v5.group(1))

            if len(iv) == 8:
                try:bytearray(int(iv, 2))
                except:
                    print(f'ERROR: la llave no es binaria.')
                    exit()
            else:
                print(f'ERROR: IV debe ser 8 bits.')
                exit()
            if method == '1':
                if len(llaveg) == 8:
                    try:bytearray(int(llaveg, 2))
                    except:
                        print(f'ERROR: la llave no es binaria.')
                        exit()
                else:
                    print(f'ERROR: la llave debe ser 8 bits.')
                    exit()
            if method == '2':
                alphabet = "12345678"
                if len(llaveg) != len(alphabet):
                    print("ERROR: la llave debe tener una longitud de 8.")
                    exit()
                flag = 0
                for k in llaveg:
                    repeat = 0
                    for l in llaveg:
                        if l in alphabet:
                            if k == l:
                                repeat += 1
                        else:
                            flag += 1
                        if repeat > 1:
                            flag += 1
                if flag >= 1:
                    print("\nERROR! Un numero de la llave falta o esta repetido.")
                    exit()
            if method == '3':
                try:
                    alphaBin = '-01'
                    for i in llaveg:
                        if i not in alphaBin:
                            print(f'ERROR: la llave no es binaria.')
                            exit()
                except:
                    print(f'ERROR: la llave no es binaria.')
                    exit()
        except LookupError:
            print('ERROR: No se pudo leer el archivo.')
        else:
            self.METHOD = method
            self.KEY = llaveg
            self.IV = iv
            if action == 'e':
                self.encrypt()
            elif action == 'd':
                self.decrypt()
            else:
                exit()
        # * --------------------

    def encrypt(self):
        try:
            octetos = bytearray(self.plainText, 'utf8')
        except:
            print(f'ERRORf: File error.')
            exit()

        bytesArray = (' '.join(f'{x:b}'.rjust(8, '0') for x in octetos)).split()

        # * Choose a method
        if self.METHOD == '1': xor = Bem.CesarE(self.IV,self.KEY)
        if self.METHOD == '2': xor = Bem.MonoE(self.IV,self.KEY)
        if self.METHOD == '3': xor = Bem.DispE(self.IV,self.KEY)
        # * ---------------

        cN = Bem.XOR(xor,bytesArray[0])
        i = 0
        plainText = ''
        logProcess = '----- log -----\n\n'
        for ba in bytesArray:
            if i == 0:
                plainText += cN + ' '
                logProcess += ("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"\
                "\nIV -> {}").format(self.IV)
                # * Choose a method
                if self.METHOD == '1': logProcess += "\n         ces -------> {}".format(xor)
                if self.METHOD == '2': logProcess += "\n         mon -------> {}".format(xor)
                if self.METHOD == '3': logProcess += "\n         dis -------> {}".format(xor)
                # * ---------------
                logProcess += ("\nK  -> {}          xor -------> C{} -> {}"\
                "\n                P{} -> {}\n".format(self.KEY,i,cN,i,ba))
            else:
                # * Choose a method
                if self.METHOD == '1': xor = Bem.CesarE(cN,self.KEY)
                if self.METHOD == '2': xor = Bem.MonoE(cN,self.KEY)
                if self.METHOD == '3': xor = Bem.DispE(cN,self.KEY)
                # * ---------------

                logProcess += ("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"\
                "\nC{} -> {}").format((i-1),cN)
                cN = Bem.XOR(xor,ba)
                plainText += cN + ' '
                # * Choose a method
                if self.METHOD == '1': logProcess += "\n         ces -------> {}".format(xor)
                if self.METHOD == '2': logProcess += "\n         mon -------> {}".format(xor)
                if self.METHOD == '3': logProcess += "\n         dis -------> {}".format(xor)
                # * ---------------
                logProcess += ("\nK  -> {}          xor -------> C{} -> {}"\
                "\n                P{} -> {}\n".format(self.KEY,i,cN,i,ba))

            i += 1

        mf.createFile('log.txt',logProcess+'\n\nRESULT:\n'+plainText)
        mf.createFile('cipherText.txt',plainText)
        print('\nCOMPLETED PROCESS\n')
        exit()

    def decrypt(self):
        plainTextClean = mf.readFile('cipherText.txt','b')
        try:
            bytearray(int(x, 2) for x in plainTextClean.split())
        except:
            print(f'ERRORf: It is not a binary string.')
            return None

        bytesArray = plainTextClean.split()

        # * Choose a method
        if self.METHOD == '1': xor = Bem.CesarE(self.IV,self.KEY)
        if self.METHOD == '2': xor = Bem.MonoE(self.IV,self.KEY)
        if self.METHOD == '3': xor = Bem.DispE(self.IV,self.KEY)
        # * ---------------
        pN = Bem.XOR(xor,bytesArray[0])
        i = 0
        plainText = ''
        logProcess = '----- log D -----\n\n'
        cN_aux = ''
        for cN in bytesArray:
            if i == 0:
                plainText += pN + ' '
                cN_aux = cN

                logProcess += ("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"\
                "\nIV -> {}").format(self.IV)
                # * Choose a method
                if self.METHOD == '1': logProcess += "\n         ces -------> {}".format(xor)
                if self.METHOD == '2': logProcess += "\n         mon -------> {}".format(xor)
                if self.METHOD == '3': logProcess += "\n         dis -------> {}".format(xor)
                # * ---------------
                logProcess += ("\nK  -> {}          xor -------> P{} -> {} = {}"\
                "\n                C{} -> {}\n".format(self.KEY,i,pN,chr(int(pN,2)),i,cN))

            else:
                # * Choose a method
                if self.METHOD == '1': xor = Bem.CesarE(cN_aux,self.KEY)
                if self.METHOD == '2': xor = Bem.MonoE(cN_aux,self.KEY)
                if self.METHOD == '3': xor = Bem.DispE(cN_aux,self.KEY)
                # * ---------------
                pN = Bem.XOR(xor,cN)
                plainText += pN + ' '

                logProcess += ("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"\
                "\nC{} -> {}").format((i-1),cN_aux)
                # * Choose a method
                if self.METHOD == '1': logProcess += "\n         ces -------> {}".format(xor)
                if self.METHOD == '2': logProcess += "\n         mon -------> {}".format(xor)
                if self.METHOD == '3': logProcess += "\n         dis -------> {}".format(xor)
                # * ---------------
                logProcess += ("\nK  -> {}          xor -------> P{} -> {} = {}"\
                "\n                C{} -> {}\n".format(self.KEY,i,pN,chr(int(pN,2)),i,cN))

                cN_aux = cN
            i += 1

        finalText = ''.join([chr(int(b, 2)) for b in plainText.split()])

        mf.createFile('log.txt',logProcess+'\n\nRESULT:\n'+finalText)
        mf.createFile('decryptText.txt',finalText)
        print('\nCOMPLETED PROCESS\n')
        exit()

app = cipherFeedBack()
app.cmdloop()