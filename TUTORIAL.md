# 🎵 Discord Music Bot — Tutorial de Configuração

## Visão Geral

Este bot permite que usuários de um servidor Discord toquem músicas via links do **YouTube** ou **Spotify** direto em canais de voz, com suporte a fila, pausa, e controles completos.

---

## Pré-requisitos

- Python 3.10+
- `ffmpeg` instalado na máquina
- Conta no [Discord Developer Portal](https://discord.com/developers/applications)
- Conta no [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)

---

## Parte 1 — Criar o Bot no Discord

### 1.1 Criar a aplicação

1. Acesse [discord.com/developers/applications](https://discord.com/developers/applications)
2. Clique em **New Application**
3. Dê um nome ao bot (ex: `ZMusicBot`) e clique em **Create**

### 1.2 Criar o Bot

1. No menu lateral, clique em **Bot**
2. Clique em **Add Bot** → **Yes, do it!**
3. Em **Token**, clique em **Reset Token** e copie o token gerado
   > ⚠️ Guarde esse token com cuidado — nunca compartilhe publicamente

### 1.3 Ativar Privileged Intents

Ainda na aba **Bot**, desça até **Privileged Gateway Intents** e ative:

- ✅ **Message Content Intent**

Clique em **Save Changes**.

### 1.4 Convidar o Bot para o servidor

1. No menu lateral, clique em **OAuth2 → URL Generator**
2. Em **Scopes**, marque: `bot`
3. Em **Bot Permissions**, marque:
   - `Send Messages`
   - `Read Message History`
   - `Connect`
   - `Speak`
4. Copie a URL gerada e abra no navegador
5. Selecione o servidor desejado e clique em **Autorizar**

---

## Parte 2 — Configurar o Spotify

### 2.1 Criar um App no Spotify

1. Acesse [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
2. Clique em **Create App**
3. Preencha:
   - **App name**: ZMusicBot (ou qualquer nome)
   - **Redirect URI**: `http://localhost` (pode ser qualquer URI válida)
4. Clique em **Save**

### 2.2 Obter as credenciais

1. Na página do app criado, clique em **Settings**
2. Copie o **Client ID** e o **Client Secret**

---

## Parte 3 — Instalar o FFmpeg

O FFmpeg é necessário para processar o áudio.

### Windows

1. Baixe em [ffmpeg.org/download.html](https://ffmpeg.org/download.html) (versão "essentials build")
2. Extraia e coloque a pasta em `C:\ffmpeg`
3. Adicione `C:\ffmpeg\bin` ao PATH do sistema:
   - Pesquise "Variáveis de Ambiente" no Windows
   - Em "Variáveis do sistema", edite `Path` e adicione `C:\ffmpeg\bin`

### Linux (Ubuntu/Debian)

```bash
sudo apt update && sudo apt install ffmpeg -y
```

### macOS

```bash
brew install ffmpeg
```

---

## Parte 4 — Configurar e Rodar o Bot

### 4.1 Instalar as dependências Python

```bash
pip install -r requirements.txt
```

### 4.2 Configurar variáveis de ambiente

1. Copie o arquivo de exemplo:
   ```bash
   cp .env.example .env
   ```
2. Abra o `.env` e preencha com seus dados:
   ```
   DISCORD_TOKEN=token_copiado_do_discord
   SPOTIFY_CLIENT_ID=client_id_do_spotify
   SPOTIFY_CLIENT_SECRET=client_secret_do_spotify
   ```

### 4.3 Rodar o bot

```bash
python bot.py
```

Se tudo estiver certo, você verá no terminal:

```
✅ Bot online como ZMusicBot#1234 (ID: 123456789)
```

---

## Parte 5 — Usando os Comandos

| Comando | Descrição |
|---|---|
| `Z_Play <link>` | Toca uma música (YouTube ou Spotify). Se houver uma tocando, entra na fila |
| `Z_Play` | Retoma a música pausada |
| `Z_Pause` | Pausa a música atual |
| `Z_Queue` | Exibe todas as músicas na fila |
| `Z_ClearQueue` | Remove todas as músicas da fila |
| `Z_Stop` | Desconecta o bot e limpa a fila |
| `Z_Ping` | Verifica latência do bot |
| `Z_Help` | Exibe todos os comandos |

### Exemplos de uso

```
Z_Play https://www.youtube.com/watch?v=dQw4w9WgXcQ
Z_Play https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT
Z_Pause
Z_Play
Z_Queue
Z_Stop
```

---

## Dicas Extras

### Rodar o bot em background (Linux)

Use `screen` para manter o bot ativo mesmo após fechar o terminal:

```bash
screen -S musicbot
python bot.py
# Pressione Ctrl+A, depois D para desanexar
```

### Rodar como serviço (systemd)

Crie o arquivo `/etc/systemd/system/musicbot.service`:

```ini
[Unit]
Description=Discord Music Bot
After=network.target

[Service]
WorkingDirectory=/caminho/para/seu/bot
ExecStart=/usr/bin/python3 bot.py
Restart=always
User=seu_usuario

[Install]
WantedBy=multi-user.target
```

Ative e inicie:

```bash
sudo systemctl enable musicbot
sudo systemctl start musicbot
```

---

## Solução de Problemas

| Problema | Solução |
|---|---|
| `DISCORD_TOKEN inválido` | Verifique se o token no `.env` está correto e sem espaços |
| Bot não entra no canal de voz | Confirme as permissões `Connect` e `Speak` no servidor |
| `ffmpeg not found` | Verifique se o FFmpeg está instalado e no PATH |
| Spotify não carrega | Confirme as credenciais Client ID e Secret no `.env` |
| Bot entra mas não toca | Verifique se `PyNaCl` está instalado (`pip install PyNaCl`) |
