# Estrutura arquivo .env
# Token do seu bot no Discord Developer Portal
DISCORD_TOKEN=token_copiado_do_discord

# Credenciais do Spotify Developer Dashboard
SPOTIFY_CLIENT_ID=client_id_do_spotify
SPOTIFY_CLIENT_SECRET=client_secret_do_spotify

---

# Prompt utilizado
Você é um desenvolvedor fullstack especialista em bots para Discord. Sua tarefa é criar um bot completo de reprodução de músicas, utilizando Python ou Node.js (escolha a linguagem mais adequada para este contexto), com todos os requisitos abaixo.

---

## Contexto

O bot será usado em servidores do Discord para tocar músicas requisitadas pelos usuários via comandos de texto. Ele deve gerenciar uma fila de reprodução e oferecer controles básicos de playback.

---

## Comandos obrigatórios

Z_Play -> Toca a música do link informado. Links aceitos: **YouTube** e **Spotify**. Qualquer outro domínio deve retornar a mensagem: "Link inválido. Por favor, use um link do YouTube ou Spotify." Se já houver uma música tocando, o link é adicionado ao final da fila.
Z_Play -> (sem link) Retoma a música que estava pausada. Caso não haja música pausada, exibe uma mensagem informando o usuário.
Z_Queue -> Exibe a fila completa com o nome de cada música e sua posição (ex: #1 - Nome da Música).
Z_ClearQueue -> Remove todas as músicas da fila.
Z_Stop -> Para a reprodução, limpa a fila e desconecta o bot do canal de voz.
Z_Pause -> Pausa a música em reprodução. Informa ao usuário que a música foi pausada.
Z_Ping -> Responde com "Pong! 🏓" no chat.
Z_Help -> Exibe uma lista formatada com todos os comandos disponíveis e suas descrições.

---

## Regras de negócio

- O bot deve entrar automaticamente no canal de voz do usuário que executou o comando.
- Se o usuário não estiver em um canal de voz, exibir: "Você precisa estar em um canal de voz para usar este comando."
- A fila deve respeitar a ordem de requisição (FIFO).
- Ao terminar uma música, a próxima da fila deve iniciar automaticamente.
- O bot deve tratar erros de forma amigável (link inacessível, música não encontrada, etc.).

---

## Entregáveis esperados

1. **Código-fonte completo e funcional** do bot, organizado em arquivos/módulos bem estruturados.
2. **Arquivo `.env.example`** com as variáveis de ambiente necessárias (ex: token do Discord, credenciais da API do Spotify).
3. **Tutorial passo a passo** de como configurar e ativar o bot em um servidor Discord, cobrindo:
   - Criação da aplicação no Discord Developer Portal
   - Configuração das permissões (intents e scopes necessários)
   - Instalação de dependências
   - Configuração das variáveis de ambiente
   - Como convidar o bot para o servidor e testá-lo

---

## Restrições e boas práticas

- O código deve ser limpo, comentado e seguir boas práticas da linguagem escolhida.
- Utilize bibliotecas consolidadas (ex: `discord.py` + `yt-dlp` para Python, ou `discord.js` + `ytdl-core` para Node.js).
- Não hardcode tokens ou chaves de API no código.
- Prefira tratamento assíncrono para evitar bloqueios durante o streaming de áudio.
