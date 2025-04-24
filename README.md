# Simulado de Matemática e Inglês - Colégio Tiradentes

Aplicativo educacional em Streamlit para simulados de Matemática e Inglês, alinhado à BNCC e às diretrizes da SEE-MG.

## Configuração do Ambiente

### Windows
```powershell
# Criar ambiente virtual
python -m venv venv
.\venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### Linux/Mac
```bash
# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

## Executar o Aplicativo
```bash
streamlit run src/app.py
```

## Estrutura do Projeto
- `/src`: Código fonte do aplicativo
- `/questions`: Banco de questões em JSON
- `/data`: Dados adicionais
- `/.streamlit`: Configurações do Streamlit

## Deploy no Streamlit Cloud
1. Faça fork deste repositório
2. Acesse https://share.streamlit.io/
3. Conecte sua conta GitHub
4. Deploy do app.py
