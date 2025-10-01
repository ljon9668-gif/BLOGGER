# Guia de Publicação via Email no Blogger

## Visão Geral

O sistema agora suporta duas formas de publicar posts no Blogger:

1. **API** - Método direto usando a API do Blogger
2. **Email** - Envio de posts via email para o endereço secreto do Blogger

## Como Funciona a Publicação via Email

O Blogger permite que você publique posts enviando emails para um endereço especial associado ao seu blog.

### Formato do Email

- **Assunto** → Torna-se o título da postagem
- **Corpo** → Torna-se o conteúdo da postagem
- **Anexos de imagem** → São inseridos automaticamente na postagem

## Configuração Passo a Passo

### 1. Obter o Email do Blogger

1. Acesse [blogger.com](https://www.blogger.com)
2. Selecione seu blog
3. Vá em **Configurações** → **Email**
4. Na seção "Postar por e-mail", você verá um endereço no formato:
   ```
   seu_blog.chave_secreta@blogger.com
   ```
   Exemplo: `joaquimildefonso090.ildefonso090@blogger.com`

### 2. Configurar Credenciais SMTP

Para enviar emails, você precisa de uma conta SMTP. Recomenda-se usar Gmail:

#### Gmail - Configuração Recomendada

1. Acesse sua conta Google
2. Vá em **Segurança** → **Verificação em duas etapas**
3. Ative a verificação em duas etapas
4. Em **Senhas de app**, crie uma nova senha
5. Use essas credenciais:
   - **SMTP Server**: `smtp.gmail.com`
   - **SMTP Port**: `587`
   - **Username**: Seu email completo (ex: `seu.email@gmail.com`)
   - **Password**: A senha de app gerada

#### Outros Provedores SMTP

Você também pode usar:
- **Outlook**: `smtp.office365.com:587`
- **Yahoo**: `smtp.mail.yahoo.com:587`
- **Zoho**: `smtp.zoho.com:587`

## Usando a Interface Web (Streamlit)

### Adicionar Configuração

1. Execute `streamlit run app.py`
2. No menu lateral, selecione **"Blogger Configuration"**
3. Na aba **"Add New Configuration"**:
   - Digite o nome do blog
   - Selecione **"Email (Send via SMTP)"**
   - Preencha:
     - **Blogger Email Address**: `seu_blog.chave@blogger.com`
     - **SMTP Server**: `smtp.gmail.com`
     - **SMTP Port**: `587`
     - **SMTP Username**: Seu email
     - **SMTP Password**: Senha de app
   - Marque "Set as default" se desejar
4. Clique em **"💾 Save Email Configuration"**

### Publicar Posts

1. Vá em **"Rewrite & Publish"** ou **"Schedule Posts"**
2. Selecione a configuração de email criada
3. O sistema automaticamente usará email para publicar

## Usando o CLI

### Adicionar Configuração

```bash
python blog_migration_cli.py
```

Siga os passos:
1. Selecione opção **6** (Manage Blogger Configurations)
2. Selecione opção **1** (Add New Configuration)
3. Digite o nome do blog
4. Selecione método **2** (Email)
5. Preencha os dados solicitados

### Publicar Posts

1. Selecione opção **7** (Publish to Blogger)
2. Escolha a configuração de email
3. Defina quantos posts publicar

## Vantagens de Cada Método

### API
✅ Publicação instantânea
✅ Retorna URL do post imediatamente
✅ Suporta rascunhos
✅ Permite atualizações posteriores

❌ Requer configuração da API do Google
❌ Limites de quota da API

### Email
✅ Simples de configurar
✅ Não depende da API do Blogger
✅ Funciona com qualquer provedor SMTP
✅ Suporta anexos de imagem

❌ Publicação não é instantânea (pode demorar alguns minutos)
❌ Não retorna URL imediatamente
❌ Menos controle sobre o formato final

## Solução de Problemas

### Email não chega no Blogger

1. **Verifique o endereço**: Confirme que está usando o email correto do Blogger
2. **Teste as credenciais SMTP**: Tente enviar um email de teste
3. **Verifique spam**: O Blogger pode ter marcado como spam
4. **Aguarde**: Emails podem levar até 10 minutos para serem processados

### Erro de autenticação SMTP

1. **Gmail**: Certifique-se de usar uma "Senha de app", não sua senha normal
2. **Verificação em 2 etapas**: Deve estar ativada para Gmail
3. **Acesso de apps menos seguros**: Para outros provedores, pode ser necessário ativar

### Formato do post incorreto

1. O sistema converte automaticamente o conteúdo para HTML
2. Formatações básicas são suportadas:
   - **Negrito**: `**texto**`
   - *Itálico*: `*texto*`
   - Listas: Linhas começando com `-` ou `•`
   - Listas numeradas: `1. item`

## Validação de Email

O sistema valida automaticamente:
- Email deve terminar com `@blogger.com`
- Deve conter um ponto (`.`) no nome de usuário
- Formato: `nome.chave@blogger.com`

Exemplos válidos:
- ✅ `meublog.abc123@blogger.com`
- ✅ `joaquim.ildefonso090@blogger.com`
- ❌ `meublog@blogger.com` (faltando chave)
- ❌ `meublog.abc@gmail.com` (domínio errado)

## Recursos Avançados

### Múltiplas Configurações

Você pode ter várias configurações salvas:
- Uma para cada blog
- Misture API e Email conforme necessário
- Marque uma como padrão para uso rápido

### Imagens

O sistema automaticamente:
- Faz download das imagens dos posts originais
- Anexa até 5 imagens no email
- O Blogger as insere no post automaticamente

### Tags/Labels

Tags são incluídas no rodapé do email e processadas pelo Blogger.

## Segurança

⚠️ **IMPORTANTE**:
- Senhas SMTP são armazenadas no banco de dados
- Use sempre senhas de app, nunca sua senha principal
- Mantenha suas credenciais seguras
- Não compartilhe sua configuração

## Suporte

Para mais ajuda:
1. Verifique a documentação do Blogger sobre publicação por email
2. Consulte a documentação do seu provedor SMTP
3. Teste com posts simples primeiro antes de migração em massa

## Exemplo Completo

### Configuração Gmail + Blogger

```
Blog Name: Meu Blog de Tecnologia
Method: Email

Blogger Email: meublog.abc123xyz@blogger.com

SMTP Server: smtp.gmail.com
SMTP Port: 587
SMTP Username: meu.email@gmail.com
SMTP Password: xxxx xxxx xxxx xxxx (senha de app)

Set as default: ✓
```

Após salvar, todos os posts serão enviados via email para o Blogger automaticamente.

---

**Última atualização**: Janeiro 2025
