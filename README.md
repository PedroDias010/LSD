# 📄 LSD - Extrator de Dados de Documentos

Uma aplicação inteligente que extrai automaticamente informações de documentos (imagens e PDFs) usando Google Gemini AI e armazena em banco de dados PostgreSQL.

## 🚀 Funcionalidades

- **Extração automática** de CNPJ, CEP, data de emissão e valor total de documentos
- **Suporte a múltiplos formatos**: PNG, JPEG e PDF
- **Processamento com IA** usando Google Gemini AI
- **Armazenamento estruturado** em PostgreSQL
- **Interface RESTful API** com FastAPI
- **Interface web** pgAdmin para gerenciamento do banco de dados

## 🛠️ Tecnologias Utilizadas

- **FastAPI** - Framework web Python
- **PostgreSQL** - Banco de dados relacional
- **Google Gemini AI** - Processamento de documentos com IA
- **Docker & Docker Compose** - Containerização e orquestração
- **SQLAlchemy** - ORM para PostgreSQL
- **Uvicorn** - Servidor ASGI

## 📋 Pré-requisitos

- Docker instalado
- Docker Compose instalado
- Chave API do Google Gemini AI (obtida através do [Google AI Studio](https://aistudio.google.com))

## 🚀 Como Executar

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd LSD
```

### 2. Configure as variáveis de ambiente
Crie um arquivo .env na raiz do projeto:
```
GEMINI_API_KEY=sua_chave_gemini_aqui
```
Para obter a chave API do Gemini, acesse o [Google AI Studio](https://aistudio.google.com) e siga as instruções para gerar sua chave.

### 3. Execute a aplicação
```bash
docker-compose up -d --build
```

### 4. Acesse os serviços
- **API Documentation**: http://localhost:8001/docs
- **pgAdmin (Interface do BD)**: http://localhost:8080
  - **Email**: admin@admin.com
  - **Senha**: admin

## 📡 Como Usar a API

### Extrair dados de um documento
```bash
curl -X POST -F "file=@seu_documento.pdf" http://localhost:8001/extract-data
```

### Verificar saúde da API
```bash
curl http://localhost:8001/
```

## 🗄️ Estrutura do Banco de Dados
A tabela `extracted_data` armazena:
- `id` (Serial, Primary Key)
- `cnpj` (VARCHAR)
- `cep` (VARCHAR)
- `data_emissao` (VARCHAR)
- `valor_total` (VARCHAR)
- `created_at` (TIMESTAMP)

## 🔧 Comandos Úteis

### Ver logs da aplicação
```bash
docker-compose logs -f api_lsd
```

### Acessar banco de dados
```bash
docker-compose exec db psql -U myuser -d mydatabase
```

### Parar a aplicação
```bash
docker-compose down
```

### Reiniciar serviços
```bash
docker-compose restart
```

## 📷 Demonstração

### Interface da API
![Interface da API](attachment://interface_api.png)

### Resposta da API
![Resposta da API](attachment://api_response.png)

### Consulta ao Banco de Dados
![Consulta ao Banco de Dados](attachment://db_query.png)

## 📝 Exemplo de Resposta da API
```json
{
  "CNPJ": "12.345.678/0001-90",
  "CEP": "12345-678",
  "Data de emissão": "15/01/2024 10:30:00",
  "Valor total": "R$ 150,50"
}
```

## 🤝 Contribuição
1. Faça fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 🆘 Suporte
Se encontrar problemas:
- Verifique se todos os containers estão rodando: `docker-compose ps`
- Consulte os logs: `docker-compose logs`
- Verifique se a chave API do Gemini está configurada corretamente

Desenvolvido para extração inteligente de dados de documentos 📄✨
