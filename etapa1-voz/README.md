# VozLocal — Etapa 1: transcrição de voz universal

Ditado por voz 100% local para Windows. Fica na bandeja, escuta um atalho global, transcreve em PT-BR
na GPU e digita o texto no campo com foco — terminal, WSL, Claude Code, Codex, navegador, WhatsApp, editores.
Nunca envia Enter.

## Instalar

No PowerShell (Windows), dentro desta pasta:

```powershell
powershell -ExecutionPolicy Bypass -File install.ps1
```

Ou a partir do WSL:

```bash
powershell.exe -ExecutionPolicy Bypass -File "$(wslpath -w install.ps1)"
```

Instala em `%LOCALAPPDATA%\VozLocal` (venv próprio), baixa o modelo, cria atalho no Menu Iniciar,
ativa o início automático e abre o app. Opções: `-NoAutostart`, `-NoLaunch`. Rodar de novo atualiza.

## Usar

| Ação | Atalho |
|---|---|
| Iniciar / parar gravação | `Ctrl+Alt+Espaço` |
| Descartar gravação | `Ctrl+Alt+Backspace` |

Ícone da bandeja: verde = pronto, vermelho = gravando, amarelo = transcrevendo, cinza = carregando.
Beeps curtos marcam início e fim (desligáveis no menu).

## Decisões técnicas

- **Modelo:** faster-whisper `large-v3-turbo`, CUDA float16 (≈1,6 GB de VRAM, fica carregado para latência baixa).
  Fallback automático para `small` em CPU se a GPU falhar.
- **Pontuação/fidelidade:** `initial_prompt` em PT-BR pontuado, VAD do Silero para cortar silêncio,
  `condition_on_previous_text=False` e filtro de alucinações típicas ("Legendas pela comunidade…").
- **Atalho:** `RegisterHotKey` do Win32 — sem hook de teclado, custo zero em repouso.
- **Microfone:** o stream só é aberto durante a gravação.
- **Inserção:** `SendInput` com `KEYEVENTF_UNICODE` (modo "Digitar"). Não usa a área de transferência e não
  dispara o "[Pasted text]" do Claude Code, então o texto fica visível para revisão. Quebras de linha viram espaço.
  Modo alternativo "Colar (Ctrl+V)" no menu, que restaura a área de transferência anterior.

## Configuração

`%APPDATA%\VozLocal\config.json` (menu → Abrir configuração; reinicie o app após editar):

- `hotkey`, `cancel_hotkey` — ex.: `"ctrl+shift+f9"`, `"win+alt+v"`
- `model` — `large-v3-turbo` (padrão), `large-v3` (mais preciso, mais lento), `medium`, `small`
- `insert_mode` — `"type"` ou `"paste"`
- `input_device` — `null` (padrão do Windows) ou nome/índice do microfone
- `max_seconds`, `beam_size`, `initial_prompt`, `append_space`, `sounds`

Log: `%APPDATA%\VozLocal\vozlocal.log`.

## Limitações conhecidas

- O Windows bloqueia `SendInput` de um processo comum para janelas rodando **como administrador**
  (ex.: terminal elevado). Nesse caso, rode o VozLocal também como administrador.
