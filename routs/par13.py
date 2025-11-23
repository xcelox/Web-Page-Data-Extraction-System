from flask import Blueprint, render_template, request, redirect, url_for, flash
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import sys
import time
from time import sleep

par13_bp = Blueprint('par13', __name__)

@par13_bp.route('/PAR13', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        from app import socketio  # Importar aqui para evitar importação circular
        login = request.form['login']
        senha = request.form['senha']
        objetos = request.form['objetos'].splitlines()
        solicitacao = "DELOG"
        autorizacao = "GEARA"
        prazo = "30"
        
        if len(objetos) > 5000:
            flash('O limite é de 5000 itens. Por favor, ajuste sua lista.')
            return redirect(url_for('par13.index'))  # Atualizado para usar 'par13.index'
        
        def inserir_prazo():
            servico = Service(executable_path='chromedriver.exe')
            navegador = webdriver.Chrome(service=servico)
            navegador.maximize_window()
            
            link = 'https://cas.correios.com.br/login?service=https%3A%2F%2Fsmarti.correios.com.br%2Fvalidar'
            navegador.get(link)


            def esperar_e_clicar(navegador, xpath, tempo=20):
                for _ in range(3):  # Tentar até 3 vezes
                    try:
                        elemento = WebDriverWait(navegador, tempo).until(
                            EC.element_to_be_clickable((By.XPATH, xpath))
                        )
                        sleep(1)  # Adiciona um delay de 0.3 segundos antes de clicar
                        elemento.click()
                        return
                    except (TimeoutException, NoSuchElementException) as e:
                        print(f"Erro ao clicar no elemento {xpath}: {e}")
                        sleep(1)  # Espera 2 segundos antes de tentar novamente
                navegador.quit()
                sys.exit()

            def esperar_e_enviar_chaves(navegador, xpath, chaves, tempo=20):
                for _ in range(3):  # Tentar até 3 vezes
                    try:
                        elemento = WebDriverWait(navegador, tempo).until(
                            EC.element_to_be_clickable((By.XPATH, xpath))
                        )
                        sleep(1)  # Adiciona um delay de 1 segundo antes de enviar chaves
                        elemento.send_keys(chaves)
                        return
                    except (TimeoutException, NoSuchElementException) as e:
                        print(f"Erro ao enviar chaves para o elemento {xpath}: {e}")
                        sleep(1)  # Espera 2 segundos antes de tentar novamente
                navegador.quit()
                sys.exit()

            esperar_e_enviar_chaves(navegador, '//*[@id="username"]', login)
            esperar_e_enviar_chaves(navegador, '//*[@id="password"]', senha)
            esperar_e_clicar(navegador, '//*[@id="fm1"]/div/div[2]/button')
            # Verificar se o login falhou
            try:
                WebDriverWait(navegador, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="alerta"]/div[1]'))
                )
                flash('Login ou senha incorretos. Por favor, tente novamente.')
                navegador.quit()
                return redirect(url_for('par13.index'))
            except TimeoutException:
                pass  # Login aparentemente foi bem-sucedido
            
            
            esperar_e_clicar(navegador, '//*[@id="menu-top"]/li[4]/a')
            esperar_e_clicar(navegador, '//*[@id="menu-top"]/li[4]/ul/div/div[2]/ul/li[4]/a')
            
            sleep(3)

            for objeto in objetos:
                esperar_e_clicar(navegador, '//*[@id="btnIncluir"]')
                esperar_e_enviar_chaves(navegador, '//*[@id="obj_co"]', objeto)
                esperar_e_enviar_chaves(navegador, '//*[@id="pho_no_solicitacao"]', solicitacao)
                esperar_e_enviar_chaves(navegador, '//*[@id="pho_no_autorizacao"]', autorizacao)
                esperar_e_enviar_chaves(navegador, '//*[@id="qtde_dias"]', prazo)
                
                # Tentar clicar no botão Gravar e verificar se a próxima etapa é alcançada
                try:
                    esperar_e_clicar(navegador, '//*[@id="btnGravar"]')
                    WebDriverWait(navegador, 40).until(
                        EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div[2]/div/div/div/div/div/div/div/div[4]/button'))
                    )
                except TimeoutException:
                    print("Erro ao clicar no botão Gravar. Tentando novamente...")
                    esperar_e_clicar(navegador, '//*[@id="modalCadastro"]/div/div/div[3]/button[2]')
                
                esperar_e_clicar(navegador, '/html/body/div[3]/div[2]/div/div/div/div/div/div/div/div[4]/button')
                sleep(5)  # Adiciona um delay de 1 segundo entre cada iteração

            navegador.quit()

        inserir_prazo()

        return redirect(url_for('par13.index'))  # Atualizado para usar 'par13.index'

    return render_template('PAR13.html')

@par13_bp.route('/progress')
def progress():
    return render_template('progress.html')  # Corrigido para 'progress.html'


