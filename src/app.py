import streamlit as st
import json
import random
from pathlib import Path
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Estudo Matemática e Inglês - Colégio Tiradentes",
    page_icon="📚",
    layout="wide"
)

# Funções de carregamento de dados
def load_questions():
    questions_path = Path(__file__).parent.parent / "questions" / "questions.json"
    with open(questions_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_students():
    students_path = Path(__file__).parent.parent / "data" / "students.json"
    if not students_path.exists():
        with open(students_path, 'w', encoding='utf-8') as f:
            json.dump({"students": []}, f)
    with open(students_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_student(student_data):
    students = load_students()
    students["students"].append(student_data)
    students_path = Path(__file__).parent.parent / "data" / "students.json"
    with open(students_path, 'w', encoding='utf-8') as f:
        json.dump(students, f, indent=4)

def verify_student(nome, senha):
    students = load_students()
    for student in students["students"]:
        if student["nome"] == nome and student["senha"] == senha:
            return True
    return False

# Função para inicializar o estado da sessão
def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'answered_questions' not in st.session_state:
        st.session_state.answered_questions = []
    if 'current_question' not in st.session_state:
        st.session_state.current_question = None
    if 'translations' not in st.session_state:
        st.session_state.translations = {}

# Função para verificar resposta
def check_answer(resposta_selecionada, questao):
    if resposta_selecionada == questao['resposta_correta']:
        st.success('🎉 Parabéns! Resposta correta!')
        st.session_state.score += 10
        st.write(f"Explicação: {questao['explicacao']}")
    else:
        st.error('❌ Ops! Tente novamente!')
        st.write(f"Explicação: {questao['explicacao']}")

# Inicialização
init_session_state()
questions = load_questions()

# Interface principal
st.title('📚 Simulado de Matemática e Inglês')
st.subheader('Colégio Tiradentes da Polícia Militar de Minas Gerais')

# Inicializa variáveis do session_state
if 'current_questions' not in st.session_state:
    st.session_state.current_questions = None
if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0
if 'answered_questions' not in st.session_state:
    st.session_state.answered_questions = []
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'translations' not in st.session_state:
    st.session_state.translations = {}
if 'used_questions' not in st.session_state:
    st.session_state.used_questions = set()

# Sistema de Login/Cadastro
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["Login", "Cadastro"])
    
    with tab1:
        with st.form("login_form"):
            login_nome = st.text_input("Nome")
            login_senha = st.text_input("Senha", type="password")
            login_submit = st.form_submit_button("Entrar")
            
            if login_submit:
                if verify_student(login_nome, login_senha):
                    st.session_state.logged_in = True
                    st.session_state.username = login_nome
                    st.rerun()
                else:
                    st.error("Nome ou senha incorretos!")
    
    with tab2:
        with st.form("signup_form"):
            novo_nome = st.text_input("Nome Completo")
            nova_senha = st.text_input("Senha", type="password")
            ano = st.selectbox("Ano Escolar", ["6º ano", "7º ano"])
            signup_submit = st.form_submit_button("Cadastrar")
            
            if signup_submit:
                if novo_nome and nova_senha:
                    student_data = {
                        "nome": novo_nome,
                        "senha": nova_senha,
                        "ano": ano,
                        "data_cadastro": datetime.now().isoformat()
                    }
                    save_student(student_data)
                    st.success("Cadastro realizado com sucesso! Faça login para continuar.")
                else:
                    st.error("Por favor, preencha todos os campos!")

else:
    st.sidebar.write(f"Bem-vindo(a), {st.session_state.username}!")
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()

    # Seleção de disciplina e ano
    col1, col2 = st.columns(2)
    with col1:
        disciplina = st.selectbox(
            'Escolha a disciplina:',
            ['matematica', 'ingles'],
            format_func=lambda x: 'Matemática' if x == 'matematica' else 'Inglês'
        )

    with col2:
        ano = st.selectbox(
            'Escolha o ano:',
            ['6ano', '7ano'],
            format_func=lambda x: '6º ano' if x == '6ano' else '7º ano'
        )

    # Exibição da pontuação
    st.sidebar.header('Pontuação')
    st.sidebar.metric('Pontos', st.session_state.score)

    # Botão para iniciar simulado
    if st.button('Iniciar Simulado', type='primary'):
        # Inicializa o conjunto de questões já usadas se não existir
        if 'used_questions' not in st.session_state:
            st.session_state.used_questions = set()
        
        # Filtra questões que ainda não foram usadas
        questoes_disponiveis = [q for q in questions[disciplina][ano] 
                              if q['id'] not in st.session_state.used_questions]
        
        # Agrupa questões por habilidade
        questoes_por_habilidade = {}
        for questao in questoes_disponiveis:
            hab = questao['habilidade']
            if hab not in questoes_por_habilidade:
                questoes_por_habilidade[hab] = []
            questoes_por_habilidade[hab].append(questao)
        
        # Cria cópias das listas para não modificar as originais
        questoes_selecionadas = []
        habilidades_disponiveis = list(questoes_por_habilidade.keys())
        num_questoes = 10
        
        # Cria uma cópia do dicionário para não modificar o original
        questoes_disponiveis_por_hab = {}
        for hab in questoes_por_habilidade:
            questoes_disponiveis_por_hab[hab] = questoes_por_habilidade[hab].copy()
        
        # Tenta selecionar questões de diferentes habilidades
        while len(questoes_selecionadas) < num_questoes and habilidades_disponiveis:
            # Escolhe uma habilidade aleatória
            hab = random.choice(habilidades_disponiveis)
            questoes_hab = questoes_disponiveis_por_hab[hab]
            
            if questoes_hab:
                # Seleciona uma questão aleatória desta habilidade
                questao = random.choice(questoes_hab)
                questoes_selecionadas.append(questao)
                questoes_hab.remove(questao)
                
                # Remove a habilidade se não houver mais questões
                if not questoes_hab:
                    habilidades_disponiveis.remove(hab)
        
        # Se ainda não tiver questões suficientes, completa aleatoriamente
        if len(questoes_selecionadas) < num_questoes:
            questoes_nao_selecionadas = [q for q in questoes_disponiveis if q not in questoes_selecionadas]
            num_restantes = min(num_questoes - len(questoes_selecionadas), len(questoes_nao_selecionadas))
            if num_restantes > 0:
                questoes_selecionadas.extend(random.sample(questoes_nao_selecionadas, num_restantes))
        
        # Embaralha as questões selecionadas
        random.shuffle(questoes_selecionadas)
        
        # Registra as questões usadas
        for q in questoes_selecionadas:
            st.session_state.used_questions.add(q['id'])
            
        # Se todas as questões já foram usadas, limpa o histórico
        if len(st.session_state.used_questions) >= len(questions[disciplina][ano]):
            st.session_state.used_questions.clear()
        
        st.session_state.current_questions = questoes_selecionadas
        st.session_state.current_question_index = 0
        st.session_state.answered_questions = []
        st.session_state.score = 0
        st.rerun()

    # Mostra a questão atual
    if 'current_questions' in st.session_state and 'current_question_index' in st.session_state \
        and st.session_state.current_question_index < len(st.session_state.current_questions):
        question = st.session_state.current_questions[st.session_state.current_question_index]
        
        # Mostra o número da questão atual
        st.write(f"Questão {st.session_state.current_question_index + 1} de {len(st.session_state.current_questions)}")
        
        # Mostra o enunciado
        st.markdown(f"**{question['enunciado']}**")
        
        # Botão de tradução para questões de inglês
        if disciplina == 'ingles':
            question_key = f"q_{question['id']}_translation"
            if st.button('Mostrar/Ocultar Tradução', key=f"trans_btn_{question['id']}"):
                st.session_state.translations[question_key] = not st.session_state.translations.get(question_key, False)
            
            if st.session_state.translations.get(question_key, False):
                st.info(question['traducao'])
        
        # Inicializa o estado da questão atual se não existir
        current_question_state = f"question_state_{st.session_state.current_question_index}"
        if current_question_state not in st.session_state:
            st.session_state[current_question_state] = {
                'answered': False,
                'correct': False,
                'show_feedback': False
            }
        
        # Mostra as opções de resposta
        resposta = st.radio(
            "Escolha a resposta correta:",
            question['opcoes'],
            key=f"resposta_{st.session_state.current_question_index}"
        )
        
        # Botão de confirmar resposta
        if st.button('Confirmar Resposta', key=f"confirmar_{st.session_state.current_question_index}"):
            # Verifica a resposta
            is_correct = resposta == question['resposta_correta']
            
            # Atualiza o estado da questão
            st.session_state[current_question_state]['answered'] = True
            st.session_state[current_question_state]['correct'] = is_correct
            st.session_state[current_question_state]['show_feedback'] = True
            
            if is_correct:
                st.session_state.score += 1
            
            # Adiciona a questão à lista de respondidas
            st.session_state.answered_questions.append(question)
            
            # Avança para a próxima questão
            st.session_state.current_question_index += 1
            st.rerun()
        
        # Mostra o feedback se a questão foi respondida
        if st.session_state[current_question_state]['show_feedback']:
            if st.session_state[current_question_state]['correct']:
                st.success("Resposta correta! " + question['explicacao'])
            else:
                st.error(f"Resposta incorreta. A resposta correta é: {question['resposta_correta']}\n\n{question['explicacao']}")

    # Botão para reiniciar
    if st.sidebar.button('Reiniciar Simulado'):
        # Limpa todas as variáveis do simulado
        if hasattr(st.session_state, 'current_questions'):
            delattr(st.session_state, 'current_questions')
        if hasattr(st.session_state, 'current_question_index'):
            delattr(st.session_state, 'current_question_index')
        if hasattr(st.session_state, 'answered_questions'):
            delattr(st.session_state, 'answered_questions')
        if hasattr(st.session_state, 'score'):
            delattr(st.session_state, 'score')
        if hasattr(st.session_state, 'translations'):
            delattr(st.session_state, 'translations')
        if hasattr(st.session_state, 'used_questions'):
            delattr(st.session_state, 'used_questions')
        st.rerun()
