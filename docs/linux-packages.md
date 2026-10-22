# Pacotes Linux em desenvolvimento

O catálogo declara 15 alvos de empacotamento. A matriz atual contém 114
registros: 112 aprovados e dois sem validação (98,2%). Ela inclui 29
combinações de distribuição/arquitetura/contexto, entre elas um teste de fonte;
registros de pacote e testes funcionais são contabilizados separadamente.
Gentoo ARM64 e Guix ARM64 estão sem validação final e seus builds estão pausados
a pedido do usuário. Esses alvos continuam fazendo parte do objetivo de suporte Linux amplo; builds e validação estão pendentes até que a pausa seja alterada. Uma receita ou um ciclo de pacote aprovado não prova, por si
só, que áudio, captura e controle foram verificados em todas as distribuições.
O guia [Flatpak](../packaging/flatpak/README.md) contém os comandos específicos
para instalar e executar o bundle `.flatpak`.

Na rodada mais recente, os 14 jobs nativos passaram build, instalação, inspeção,
remoção e os testes de atualização/preservação de dados previstos para cada
gerenciador ([CI 39705918511](https://github.com/V1nic1us/jarvis/actions/runs/39705918511)).
Flatpak e Nix passaram em x86_64/AArch64 ([Flatpak](https://github.com/V1nic1us/jarvis/actions/runs/39705918446), [Nix](https://github.com/V1nic1us/jarvis/actions/runs/39705918449)). Void glibc e musl passaram build, instalação, upgrade e preservação de dados nas duas arquiteturas ([CI 39705918455](https://github.com/V1nic1us/jarvis/actions/runs/39705918455)).

A matriz registra cada job e suas limitações. O host Arch/KDE Wayland já passou testes funcionais do overlay, MCP instalado
e áudio sintético por ALSA e PipeWire/Pulse, incluindo Piper, STT e VAD. Medições de nível Pulse e ALSA por 0,5 s passaram no host; o launcher do pacote
Arch também passou `--mic-level` via Pulse e VAD positivo com tom sintético. Ainda faltam PTT e VAD com fala real e
reprodução/streaming nos pacotes instalados, autorização/recusa/revogação real
de Screenshot e RemoteDesktop e repetir a cobertura em outros desktops e distros.

## NixOS

A flake da raiz fornece `jarvis-assistant` para x86_64-linux e aarch64-linux.
Ela fixa nixpkgs pelo `flake.lock`, compila o overlay com Rust e monta o runtime
Python imutável com dependências do nixpkgs e Piper 1.8.0 fixado. A instalação
não executa pip nem npm. O pacote coloca a aplicação sob o prefixo do Nix Store
e adiciona os binários de áudio e controle ao wrapper do launcher.

Instale diretamente pelo Nix:

```sh
nix --extra-experimental-features "nix-command flakes" profile install .#jarvis-assistant
jarvis --doctor
```

Depois de compilar um output, o ciclo de instalação, verificação do runtime,
remoção e preservação dos dados pode ser repetido em um ambiente Nix descartável:

```sh
sh scripts/test-nix-package.sh "$(readlink -f ./dist/nix/jarvis-assistant)"
```

Para incluir também o smoke do overlay X11 em Xvfb/AT-SPI, instale os pacotes
de teste `xvfb`, `dbus-x11`, `python3-gi`, `gir1.2-atspi-2.0` e `at-spi2-core`
e acrescente `--gui` ao comando.

Ou construa um link do pacote para inspeção:

```sh
scripts/build-package.sh --target nix --output "$PWD/dist/nix"
```

Remova o perfil com `nix profile list` para localizar o índice do Jarvis e
`nix profile remove <índice>`. Builds e ciclo de instalação/verificação/remoção
passaram em x86_64 e AArch64 na CI, com smoke do overlay em Xvfb/D-Bus. A CI
AArch64 executou o pacote no runner ARM; isso ainda não substitui validação numa
sessão NixOS real nem testes com áudio físico e portais. Veja o registro em
`docs/notes/linux-verification.md`.


## Arch Linux

No checkout, em ambiente Arch da mesma arquitetura do pacote:

```sh
scripts/build-package.sh --target arch --arch x86_64 --output "$PWD/dist/native"
sudo pacman -U dist/native/jarvis-assistant-0.1.0-1-x86_64.pkg.tar.zst
jarvis --doctor
jarvis --download-voice
jarvis-overlay
```

Para ARM64, use ambiente Arch Linux ARM e `--arch aarch64`. O pacote foi
compilado e passou pelo ciclo de instalação, verificação do overlay em Xvfb e
remoção sob QEMU; o `makepkg` do Arch Linux ARM gera `.pkg.tar.xz` por padrão.
O teste em hardware ARM físico e numa sessão desktop/áudio completa ainda está
pendente.
O pacote inclui overlay, plugins, MCP, agente e dependências Python privadas.
Os wheels são vinculados à versão minor do Python da distribuição; uma atualização
de Python exige reconstruir o pacote. A instalação não executa pip ou npm.
Modelos, configuração e autenticação ficam nos diretórios do usuário.

Em container Arch rolling x86_64, o pacman atualizou o artefato anterior
`0.1.0-1` para o pacote reconstruído do código atual (`0.1.0-2` de teste).
`jarvis --doctor`, OpenCode 1.18.23, `pacman -Qkk`, a preservação do arquivo de
dados do usuário e a remoção passaram. O número de revisão `-2` foi usado só no
ensaio; não altera a revisão da receita publicada no checkout.

## Debian

A receita em `packaging/debian` compila no ambiente da distribuição. O Dockerfile
usa Debian trixie e Rust 1.95; não reaproveita o overlay compilado no Arch.

```sh
docker build -f packaging/debian/Dockerfile -t jarvis-linux-debian:local .
mkdir -p dist/native
docker run --rm -v "$PWD/dist/native:/out" jarvis-linux-debian:local
sudo apt install ./dist/native/jarvis-assistant_0.1.0-1_amd64.deb
jarvis --doctor
jarvis-overlay
```

No ARM64, o nome do arquivo termina em `_arm64.deb`. Para atualizar, instale
o novo DEB com `apt install ./caminho/do/pacote.deb`; para remover, use
`sudo apt remove jarvis-assistant`.

Os DEBs x86_64 e ARM64 foram compilados no Debian 13 e passaram pela instalação com apt,
diagnóstico, imports, verificação de arquivos e remoção em container limpo,
preservando o dado de usuário usado no teste. O teste de abertura, segunda execução e saída da interface passou em X11
isolado. A atualização Debian de `0.1.0-1` para `0.1.0-2` passou com `apt`
em x86_64 e ARM64, preservando dados e integridade ([CI 39705918511](https://github.com/V1nic1us/jarvis/actions/runs/39705918511)).
Uso completo no desktop continua pendente.

## Ubuntu 24.04

A receita usa o mesmo controle Debian, mas compila o overlay e prepara os
wheels no Ubuntu 24.04, com o ABI Python 3.12 dessa distribuição. O toolchain
Rust oficial é fornecido separadamente; os binários do aplicativo são produzidos
no Ubuntu. Os builds x86_64 e ARM64 passaram pela instalação limpa, imports,
integridade, remoção e relançamento da interface em X11 isolado na execução
CI 38910794267. O uso completo no desktop segue em validação.

```sh
docker build -f packaging/ubuntu/Dockerfile -t jarvis-linux-ubuntu:local .
mkdir -p dist/ubuntu
docker run --rm -v "$PWD/dist/ubuntu:/out" jarvis-linux-ubuntu:local
sudo apt install ./dist/ubuntu/jarvis-assistant_0.1.0-1_amd64.deb
jarvis --doctor
jarvis-overlay
```

O runner ARM64 produz `_arm64.deb`. A CI constrói cada arquitetura no alvo,
instala com apt e verifica recursos, imports, integridade e remoção. O upgrade
DEB de revisão com preservação dos dados passou em x86_64 e AArch64 na
[CI 39705918511](https://github.com/V1nic1us/jarvis/actions/runs/39705918511).
O comando `scripts/build-package.sh --target ubuntu --arch x86_64` exige um
ambiente Ubuntu com as dependências de build e Rust compatível já instalados.

## Estado da validação

A [CI nativa 39419181097](https://github.com/V1nic1us/jarvis/actions/runs/39419181097)
concluiu com sucesso 13 combinações depois de repetir o job Arch x86_64:

| Família | Base | Arquiteturas validadas |
|---|---|---|
| Arch | rolling | x86_64 |
| Debian | 13 | x86_64, aarch64 |
| Ubuntu | 24.04 | x86_64, aarch64 |
| Fedora | 44 | x86_64, aarch64 |
| openSUSE | Tumbleweed | x86_64, aarch64 |
| RHEL | 10 (AlmaLinux) | x86_64, aarch64 |
| Alpine | 3.24 | x86_64, aarch64 |

O ciclo CI instala cada pacote no gerenciador nativo e verifica diagnóstico,
ABI e imports Python privados, recursos, integridade, abertura/segunda execução
da interface em X11 isolado, saída e remoção preservando dados. Também cobre
atualização DEB em x86_64/AArch64 e atualização APK assinada nas duas arquiteturas.
Essas verificações não substituem a matriz de áudio, portais, GNOME/KDE e
sessões reais. No commit `12279e468fc53a43ad5e49727bcff5d332d3fecf`, os 13 jobs
nativos passaram na [CI native packages](https://github.com/V1nic1us/jarvis/actions/runs/39480053201),
Flatpak x86_64/AArch64 passou na [CI Flatpak](https://github.com/V1nic1us/jarvis/actions/runs/39480053338)
e Nix passou build e ciclo de instalação em ambas as arquiteturas na [CI Nix](https://github.com/V1nic1us/jarvis/actions/runs/39480053242).
O [workflow Void mais recente](https://github.com/V1nic1us/jarvis/actions/runs/39402420125)
passou nos quatro jobs: glibc e musl em x86_64 e AArch64. Isso valida build e
ciclo do pacote nessas combinações; desktops reais, áudio e upgrades continuam
pendentes conforme a matriz de verificação.

Slackware current tem um SlackBuild local; build, instalação e imports do runtime
foram exercitados em container x86_64, incluindo a reinicialização isolada do
overlay e remoção preservando os dados do usuário. O catálogo registra
**installed-smoke** para x86_64. A receita inclui xdotool, xclip e wl-clipboard
compilados de revisões fixas porque não há pacotes oficiais current para esses
helpers; desktop e áudio reais seguem pendentes.
Solus tem uma receita `package.yml`; build e ciclo eopkg foram validados em
x86_64, incluindo imports privados, integridade, relançamento isolado do overlay,
remoção e preservação dos dados do usuário. Desktop e áudio reais continuam
pendentes. Guix tem receita local e passou por build e ciclo de perfil instalado
em container GNU Guix x86_64; isso ainda não valida desktop ou áudio reais.
Veja também os testes reais registrados em `docs/notes/linux-verification.md`.

Os downloads do agente usam URLs e integridade SHA512 fixadas em
`packaging/opencode-sources.json`. As dependências Python são resolvidas durante
o build e registradas no relatório instalado; ainda não há lock completo de
wheels para builds reproduzíveis entre datas diferentes.

## Fedora

A receita local Fedora está em `packaging/rpm/fedora/jarvis-assistant.spec`.
Ela usa as dependências Fedora GTK3/WebKit4.1 e `ffmpeg-free`, compila o overlay
no alvo e inclui um runtime Python privado vinculado ao ABI do sistema.
O RPM e o SRPM podem ser construídos no próprio Fedora:

```sh
scripts/build-package.sh --target fedora --arch x86_64 --output "$PWD/dist/native"
```

Há também um ambiente de build Fedora 44:

```sh
docker build -f packaging/rpm/fedora/Dockerfile -t jarvis-linux-fedora:local .
mkdir -p dist/native
docker run --rm -v "$PWD/dist/native:/out" jarvis-linux-fedora:local
sudo dnf install ./dist/native/jarvis-assistant-0.1.0-1.fc44.x86_64.rpm
jarvis --doctor
jarvis-overlay
```

No ARM64, use o RPM `.aarch64.rpm`. Para atualizar, use `sudo dnf upgrade
./caminho/do/pacote.rpm`; para remover, `sudo dnf remove jarvis-assistant`.
O arquivo `.src.rpm` contém fontes e receita e não instala a aplicação.

Os RPMs Fedora 44 x86_64 e ARM64 passaram pela atualização de `0.1.0-1` para
`0.1.0-2` com DNF, preservando dados e passando `rpm -V` ([CI 39705918511](https://github.com/V1nic1us/jarvis/actions/runs/39705918511)).
O RPM x86_64 também passou pela instalação com dnf, doctor, imports, versão
do agente, presença de pactl, verificação rpm e remoção com preservação do dado
de usuário usado no teste. O ciclo do
pacote atualizado e o relançamento do overlay em Xvfb também passaram. Não há
RPM publicado em repositório oficial. A validação do desktop completo e do
áudio físico permanece pendente. O arquivo `packaging/targets.json` registra separadamente as arquiteturas
declaradas e as validadas; o job Fedora AArch64 passou o upgrade e preservação
de dados na CI 39705918511.

A CI acrescentou um teste de importação do AT-SPI que revelou a ausência de
`DBus-1.0.typelib` nas instalações mínimas Fedora x86_64 e ARM64. A receita
agora exige `gobject-introspection`; a correção passou pela instalação limpa, importação AT-SPI,
integridade e remoção em Fedora 44 x86_64 e ARM64 na execução CI 38764598505. O smoke anterior não incluía esse teste e não comprova que
a acessibilidade estava funcional.

## openSUSE Tumbleweed

A receita própria está em `packaging/rpm/suse`. Ela usa WebKit 4.1 fornecido por
`webkitgtk3-devel`, o Python padrão da distribuição e os pacotes GI/AT-SPI do
openSUSE. A CI 38797751372 validou builds e instalação em x86_64 e ARM64,
imports de voz/MCP/AT-SPI, integridade RPM, remoção e preservação de dados.
O teste gráfico isolado confirmou que uma segunda abertura mantém a janela
original e que a saída pela interface funciona. A atualização de `0.1.0-1` para
`0.1.0-2` pelo Zypper também passou, preservando dados do usuário e verificando
a integridade RPM. Voz e portais em desktops openSUSE completos ainda precisam
de validação.

```sh
docker build -f packaging/rpm/suse/Dockerfile -t jarvis-linux-suse:local .
mkdir -p dist/suse
docker run --rm -v "$PWD/dist/suse:/out" jarvis-linux-suse:local
sudo zypper install ./dist/suse/jarvis-assistant-0.1.0-1.x86_64.rpm
```

O artefato ARM64 termina em `.aarch64.rpm`. No próprio Tumbleweed com as
ferramentas de build, use `scripts/build-package.sh --target suse --arch x86_64`.
Essa receita ainda não foi validada no openSUSE Leap.

Os testes dos pacotes incluem uma sessão X11 e D-Bus privadas,
abertura repetida do overlay e fechamento pela interface. Esse teste usa um
launcher sem cérebro; não substitui voz, áudio e portais em GNOME/KDE reais.

## ABI do Python em pacotes nativos

A preparação do pacote resolve o interpretador do alvo (por exemplo,
`/usr/bin/python3.14`) e cria um link privado em
`/usr/lib/jarvis/runtime/bin/python3`. O launcher e os comandos Python privados
usam esse ABI, mesmo se o alias `python3` mudar. Os RPMs exigem também o provider
GI da mesma versão, além de `python(abi)`. Isso não torna wheels compatíveis com
outro ABI; atualizações que removam o interpretador necessário precisam de um
pacote Jarvis reconstruído para a nova versão.

A regressão local simula a troca do alias e verifica o launcher instalado e o
comando Piper. A CI dos pacotes confere o interpretador e os imports com o ABI
registrado no manifesto de instalação.

## Runtime preparado com dependências da distribuição

Quando uma dependência como ONNX Runtime é fornecida pela distribuição, o
builder pode resolver os pacotes Python em um venv separado, criado com
`--without-pip --system-site-packages`. O pip do ambiente de build instala nesse
venv com `--python` e produz um relatório com `--report`. Nenhum desses comandos
é executado na instalação do pacote pelo usuário.

`prepare-package.py` aceita `--python-environment CAMINHO` e
`--python-report RELATORIO.json` no lugar de `--wheelhouse`. Ele verifica o ABI,
copia somente os módulos locais do venv e recria os comandos pelos metadados dos
pacotes, removendo referências ao caminho de build. Dependências disponíveis
somente no Python da distribuição continuam externas e precisam constar nas
dependências nativas da receita. Esse modo rejeita symlinks nos módulos,
redirecionamentos `.pth` e links de instalações editáveis. O venv deve conter
somente o runtime, sem ferramentas de build.

A regressão local remove o venv original e executa um comando do runtime
copiado. O APK Alpine x86_64 construído das fontes passou pelos imports do
runtime de voz completo em uma instalação limpa. Síntese e transcrição offline
CPU também passaram com áudio sintético usando o APK instalado; microfone e
integração de áudio em desktop real continuam pendentes.


### Alpine 3.24: ciclo instalado x86_64/AArch64 validado

A receita local `packaging/alpine/APKBUILD` constrói CTranslate2 e Piper para
musl a partir de commits fixados. ONNX Runtime e NumPy vêm dos pacotes Alpine;
as demais dependências Python ficam privadas em `/usr/lib/jarvis/python`.
O agente usa o artefato musl com SHA512 verificado e permanece sem stripping.
A configuração do pacote limita apenas o OpenBLAS a uma thread para evitar
paralelismo aninhado com OpenMP; o CTranslate2 mantém seu paralelismo próprio.

Build completo em container descartável:

```sh
docker build -f packaging/alpine/Dockerfile -t jarvis-linux-alpine .
mkdir -p dist/alpine
docker run --rm -v "$PWD/dist/alpine:/export" jarvis-linux-alpine
```

O container exporta junto ao APK a chave pública que assinou o pacote. Confie
essa chave no Alpine de destino antes da instalação; para um build com `abuild`
local, copie para `/etc/apk/keys/` a chave pública correspondente ao assinador:

```sh
sudo cp dist/alpine/*.pub /etc/apk/keys/
sudo apk add --no-cache ./dist/alpine/jarvis-assistant-0.1.0-r0.apk
jarvis --doctor
sudo apk del jarvis-assistant
```

Dentro de um ambiente Alpine com as dependências de build instaladas, um usuário
não root com chave `abuild` configurada também pode executar
`scripts/build-package.sh --target alpine --output dist/alpine`.
O build precisa de rede; a instalação não executa pip ou downloads de modelos.
Os APKs completos x86_64 e aarch64 passaram pela instalação assinada em Alpine
limpo, pelos imports e ABI privados, pelos recursos e ferramentas, pela interface
isolada X11 (reabertura e saída), pela integridade e pela remoção preservando
dados de teste. Os dois jobs Alpine da [CI 38953368727](https://github.com/V1nic1us/jarvis/actions/runs/38953368727)
passaram; o catálogo registra **installed-smoke** para ambas as arquiteturas.
O APK x86_64 passou também pela atualização assinada r0→r1 construída das fontes
completas, preservando hashes de configuração, cache e dados do modelo; o teste
está em `.superpowers/sdd/2026-10-14-jarvis-linux/alpine-full-source-signed-upgrade-retry.log`.
A atualização assinada r0→r1 passou também em AArch64 na CI 39705918511.
Microfone e desktops reais seguem pendentes. O APK x86_64
instalado também sintetizou e transcreveu uma frase de teste em português, sem
rede, usando Piper e Whisper tiny/CPU int8. O erro por palavra
foi 13,3%; esse ensaio sintético não certifica captura de microfone nem qualidade
de reconhecimento em situações reais.

### Família RHEL 10: ciclo instalado x86_64/AArch64 validado

A base de build é AlmaLinux 10, com EPEL e CRB. A receita principal fica em
`packaging/rpm/rhel/jarvis-assistant.spec`. O driver também constrói um RPM
`xdotool` a partir do commit upstream fixado na receita de dependência, pois
os repositórios consultados dessa base não oferecem esse pacote. Os RPMs
binários e de código-fonte são exportados juntos:

```sh
docker build -f packaging/rpm/rhel/Dockerfile -t jarvis-linux-rhel .
mkdir -p dist/rhel
docker run --rm -v "$PWD/dist/rhel:/out" jarvis-linux-rhel
```

O build completo dos dois RPMs e seus SRPMs passou em AlmaLinux 10 x86_64.
Em um container limpo também passaram instalação, ABI/imports privados, recursos,
interface Wayland em Weston isolado, integridade e remoção preservando os dados
de teste. O catálogo registra **installed-smoke** para x86_64 e aarch64: os dois jobs
RHEL da [CI 38947707383](https://github.com/V1nic1us/jarvis/actions/runs/38947707383)
passaram nos testes instalados da arquitetura correspondente.
Upgrade RPM de revisão e preservação de dados passaram em x86_64 e AArch64 na
CI 39705918511. Upgrade entre versões publicadas do aplicativo, áudio, portais
e desktops reais continuam pendentes. A seleção de repositórios da imagem de build é específica do AlmaLinux; os testes
não certificam outras distribuições da família.

### Void glibc: ciclo instalado x86_64 validado

A receita local `packaging/void/template` usa o XBPS nativo e mantém o Python
privado vinculado ao ABI 3.14 da distribuição. O driver fixa o commit da coleção
`void-packages` e verifica o SHA256 do arquivo de fontes do checkout. O builder
`packaging/void/Dockerfile` prepara uma imagem descartável com o modo `ethereal`
oferecido pelo próprio `xbps-src`; esse modo modifica a raiz do ambiente e deve
permanecer restrito ao container de build. A receita declara Mesa em runtime:
o WebKitGTK precisa de um backend EGL no Void. Um teste sem Mesa reproduziu a
falha EGL e a janela inacessível; instalado Mesa, o relançamento GTK passou.

A revisão XBPS `_2` foi gerada diretamente com `xbps-src`. Num ambiente sem
Mesa, o XBPS instalou Mesa automaticamente pela dependência declarada. Doctor,
imports/ABI privados, recursos, integridade, janela X11 em Xvfb, remoção e
preservação de dados passaram. O artefato e o log de validação estão em
`.superpowers/sdd/2026-10-14-jarvis-linux/void-glibc-native-artifacts` e
`void-glibc-xbps-src-v2-lifecycle.log`. Também passou uma atualização XBPS da
revisão `_1` para `_2`, com doctor antes e depois e sentinel dos dados do usuário
preservado; isso não substitui atualização entre versões de aplicativo
publicadas. CI também construiu o pacote e passou instalação, inspeção e
remoção em Void glibc AArch64 na [CI 39419181120](https://github.com/V1nic1us/jarvis/actions/runs/39419181120). O rerun [39705918455](https://github.com/V1nic1us/jarvis/actions/runs/39705918455) passou upgrade `_1`→`_2` e preservação de dados em x86_64 e AArch64. Desktop real, áudio e migração entre versões publicadas do aplicativo ainda não foram validados.

Em um host Void glibc nativo, compile o pacote e instale-o pelo repositório
XBPS local:

```sh
scripts/build-package.sh --target void-glibc --arch x86_64 --output "$PWD/dist/void"
sudo xbps-rindex -a "$PWD"/dist/void/jarvis-assistant-*.xbps
sudo xbps-install -y -R "$PWD/dist/void" jarvis-assistant
jarvis --doctor
sudo xbps-remove -y jarvis-assistant
```

Use uma pasta de repositório vazia para cada arquitetura e variante de libc. A
variante musl tem uma receita XBPS em `packaging/void-musl/template`, que
compila ONNX Runtime 1.24.4 dentro do build nativo em vez de reutilizar wheels
glibc. A revisão `_2` foi construída por `xbps-src` e passou pelo ciclo XBPS
x86_64: instalação, `jarvis --doctor`, ABI/imports privados e AT-SPI, smoke
Xvfb de xdotool/xclip, reabertura do overlay, verificação do banco de pacotes,
remoção e preservação de dados do usuário. O artefato e o log estão em
`.superpowers/sdd/2026-10-14-jarvis-linux/void-musl-native-artifacts` e
`void-musl-native-lifecycle.log`. Desktop real, áudio, portais e atualização
entre versões reais ainda seguem pendentes. A [CI 39419181120](https://github.com/V1nic1us/jarvis/actions/runs/39419181120) também passou build, instalação, inspeção e remoção em Void musl x86_64 e AArch64. Atualização AArch64 entre
versões publicadas, desktop real, áudio e portais ainda não foram validados
nessa arquitetura. O XBPS também passou uma
atualização controlada da revisão `_1` para `_2`, com `jarvis --doctor` antes e
depois e sentinel dos dados do usuário preservado; isso ainda não substitui uma
atualização entre versões de aplicativo publicadas.
O rerun [39705918455](https://github.com/V1nic1us/jarvis/actions/runs/39705918455)
também passou build, instalação, atualização `_1`→`_2`, preservação de dados e
remoção em Void musl x86_64 e AArch64.

Em um host Void musl nativo, use o alvo específico e o mesmo fluxo de repositório
XBPS:

```sh
scripts/build-package.sh --target void-musl --arch x86_64 --output "$PWD/dist/void-musl"
sudo xbps-rindex -a "$PWD"/dist/void-musl/jarvis-assistant-*.xbps
sudo xbps-install -y -R "$PWD/dist/void-musl" jarvis-assistant
jarvis --doctor
sudo xbps-remove -y jarvis-assistant
```

Para ARM64, execute cada build em um host Void da arquitetura correspondente e
troque `--arch x86_64` por `--arch aarch64`. Não instale pacote musl em Void
glibc nem pacote glibc em Void musl.

### Gentoo rolling: pacote local em validação

O driver `scripts/build-package.sh --target gentoo --output dist/gentoo`
prepara um overlay local, registra o arquivo de fontes sanitizado no Manifest e
usa `ebuild package` para gerar um pacote `gpkg`. O ambiente precisa de Portage,
Git e das dependências de build da receita. A receita fixa Python 3.14 e WebKit
no slot 4.1, exige os recursos de captura/reprodução do FFmpeg e preserva o
payload do agente sem stripping. As dependências privadas são resolvidas durante
o build; a instalação não executa pip nem baixa modelos.

O gpkg atualizado foi compilado e instalado pelo Portage nativo em x86_64.
`jarvis --doctor`, os 7.355 caminhos do manifesto, os imports privados e ABI
Python, AT-SPI, os ganchos de cache XDG, o relançamento em Weston headless e a
remoção preservando um sentinel de dados passaram. O artefato e o log de
validação estão em `.superpowers/sdd/2026-10-14-jarvis-linux/gentoo-native-artifacts`
e `gentoo-native-revised-lifecycle.log`. O catálogo marca **installed-smoke**
somente para x86_64. Atualização e aarch64 seguem pendentes. O overlay é local e
não implica publicação no repositório oficial.

### Slackware current: SlackBuild local

`packaging/slackware/jarvis.SlackBuild` produz um pacote `.txz` local para
x86_64. O ambiente de build precisa de Python 3.10+, pip, Rust/Cargo, Node.js/
npm, pkg-config e headers GTK+3/WebKitGTK 4.1. O SlackBuild verifica essas
ferramentas antes de compilar. Slackware não resolve dependências de runtime
automaticamente: instale primeiro as dependências listadas em
`/usr/doc/jarvis-assistant-0.1.0/README` dentro do pacote.

WebKitGTK 4.1 não aparece na
[lista de pacotes oficial do Slackware current](https://mirrors.slackware.com/slackware/slackware64-current/PACKAGES.TXT).
No Slackware 15.0, há um SlackBuild comunitário para
[`webkit2gtk4.1`](https://slackbuilds.org/repository/15.0/libraries/webkit2gtk4.1/),
validado para essa versão e que requer unifdef, libsoup3, wpebackend-fdo,
bubblewrap, geoclue2 e xdg-dbus-proxy. No current x86_64, o
repositório comunitário [slackware.lngn.net](https://slackware.lngn.net/) publica
o conjunto `webkitgtk`; depois de configurar o slackpkg+ conforme as instruções
do repositório, instale-o com `slackpkg install webkitgtk`. O [Python 3 do
Slackware 15.0](https://packages.slackware.com/?p=python3-3.9.25-x86_64-1_slack15.0.txz&r=slackware64-15.0)
é 3.9, abaixo do mínimo 3.10 do projeto; é necessário
disponibilizar Python 3.10+ no ambiente de build e runtime dessa versão.

```sh
scripts/build-package.sh --target slackware --arch x86_64 --output "$PWD/dist/native"
sudo installpkg dist/native/jarvis-assistant-0.1.0-x86_64-1_local.txz
jarvis --doctor
# Após gerar uma revisão superior, por exemplo com BUILD=2:
BUILD=2 scripts/build-package.sh --target slackware --arch x86_64 --output "$PWD/dist/upgrade"
sudo upgradepkg dist/native/jarvis-assistant-0.1.0-x86_64-1_local.txz%dist/upgrade/jarvis-assistant-0.1.0-x86_64-2_local.txz
sudo removepkg jarvis-assistant-0.1.0-x86_64-2_local
```

Em um container Slackware descartável com dependências gráficas e de áudio já
instaladas, valide o ciclo completo e o overlay X11 isolado usando:

```sh
scripts/test-native-package.sh slackware "$PWD/dist/native/jarvis-assistant-0.1.0-x86_64-1_local.txz"
```

Slackware 15.0 fornece Python 3.9, abaixo do mínimo de Python 3.10 deste
projeto; o alvo de build é Slackware current. A receita compila xdotool
4.20260303.1, xclip 0.13 e wl-clipboard 2.3.0 de commits fixos e os instala em
`/usr/lib/jarvis/bin`, priorizado pelo launcher. As licenças dos helpers são
incluídas no pacote. O build x86_64 no container current passou e o pacote foi
instalado com `installpkg`;
`jarvis --doctor`, OpenCode 1.18.23, imports Python privados e o typelib AT-SPI
passaram. O teste da janela X11 e da remoção preservando um sentinel também
passou. O overlay compilado no Slackware passou também pelo teste de reabertura
e saída sob Weston/Wayland em um container Gentoo; esse teste cruzado não
substitui Wayland nativo no Slackware. Piper também sintetizou offline uma frase
para WAV mono a 22.050 Hz com o modelo baixado e verificado pelo projeto. O
catálogo continua como `unverified`: as bibliotecas transitivas oficiais foram
instaladas e verificadas por MD5; `ldd` não encontrou dependências ausentes em
ffmpeg, ffplay e pactl. `pactl --version`, captura FFmpeg para ALSA `null`,
reprodução via ffplay nesse dispositivo e a captura `capture.record` do Jarvis
com `AUDIO_BACKEND=alsa` passaram. Piper também sintetizou e reproduziu uma
frase via ALSA `null`. Microfone/alto-falantes físicos, servidor PulseAudio em
sessão, clipboard Wayland com seat, atualização entre versões distintas e
aarch64 permanecem pendentes. O catálogo registra **installed-smoke** para
x86_64. Para instalações mínimas,
confira bibliotecas transitivas de ffmpeg/ffplay com `ldd /usr/bin/ffmpeg
/usr/bin/ffplay`; o fechamento pode incluir muitos pacotes, inclusive
`vulkan-sdk`. WebKitGTK 4.1 no current foi obtido do repositório comunitário
citado acima.

No catálogo oficial current, `ffmpeg` fornece `ffmpeg`/`ffplay`, `pulseaudio`
fornece `pactl` e `alsa-utils` fornece `arecord`; xdotool, wl-clipboard e xclip
não aparecem como pacotes oficiais. O SlackBuild compila os três helpers e os
inclui no pacote Jarvis. `scripts/test-native-package.sh` verifica os comandos
depois da instalação e executa um teste de xdotool e roundtrip xclip em Xvfb.
Build e roundtrip X11 passaram no current; clipboard Wayland ainda requer um
compositor com seat.

### Solus: receita eopkg, ciclo instalado e upgrade

`packaging/solus/package.yml` descreve a receita nativa do Solus para x86_64.
O driver cria um arquivo-fonte do checkout, injeta seu SHA256 e URI local na
receita e chama `solbuild`; assim, alterações locais ainda não publicadas podem
ser compiladas. Inicialize e atualize o ambiente de build do Solus uma vez com
`sudo solbuild init -u`, então construa e instale:

```sh
scripts/build-package.sh --target solus --arch x86_64 --output "$PWD/dist/solus"
sudo eopkg install ./dist/solus/jarvis-assistant-0.1.0-1-1-x86_64.eopkg
jarvis --doctor
```

Para atualizar, instale o novo `.eopkg` com `sudo eopkg install
./dist/solus/<arquivo>.eopkg`; para remover, use `sudo eopkg remove
jarvis-assistant`. O pacote foi compilado com `solbuild`, instalado e removido
com eopkg em Solus 4.9 x86_64. Imports privados, ABI, OpenCode 1.18.23,
integridade, relançamento isolado da janela e preservação dos dados passaram; o
catálogo registra o ciclo instalado para x86_64. Três releases foram
construídas; o upgrade da release 2 para a 3 também foi validado em um container
descartável Solus 4.9. O pacote glibc remove o addon nativo musl do msgpackr; no
rebuild, o ABI scanner deixou de reportar `Missing library: libc.so`. O scanner
ainda registra um diagnóstico não fatal para o link do Python externo em
`/usr/bin/python3.14`. `eopkg check` e `jarvis --doctor` passaram antes e
depois da atualização; a release 3 também enumerou fontes ALSA pelo launcher
e passou integridade no container. Isso não valida captura por microfone físico. Os dados sentinela de
CONFIG/DATA/CACHE/STATE permaneceram idênticos, e a remoção preservou os dados.
Isso valida o upgrade no ambiente de container; desktop e áudio reais e Wayland
nativo continuam pendentes. A evidência está em
`docs/notes/linux-matrix.json` e nos logs/artefatos locais indicados nela.
`networking: true` permite que o build atual baixe dependências npm/Python e o
agente; a instalação do pacote não baixa dependências da aplicação.
Depois de gerar o `.eopkg`, rode o ciclo em um container Solus x86_64:

```sh
scripts/test-native-package.sh solus "$PWD/dist/solus/jarvis-assistant-0.1.0-1-1-x86_64.eopkg"
```

O builder aceita `--release` somente para Solus, mantendo `1` como padrão. Para
preparar duas revisões do mesmo checkout e exercitar um upgrade local:

```sh
scripts/build-package.sh --target solus --arch x86_64 --release 1 --output "$PWD/dist/solus-r1"
scripts/build-package.sh --target solus --arch x86_64 --release 2 --output "$PWD/dist/solus-r2"
```

No container Solus x86_64 descartável, rode o teste de upgrade e preservação:

```sh
scripts/test-native-solus-upgrade.sh \
  dist/solus-r2/jarvis-assistant-0.1.0-2-1-x86_64.eopkg \
  dist/solus-r3/jarvis-assistant-0.1.0-3-1-x86_64.eopkg 2 3
```

O teste instala cada release com eopkg, confere o release indicado, executa
`jarvis --doctor` e `eopkg check`, compara sentinels em CONFIG/DATA/CACHE/STATE
antes e depois do upgrade e confirma que a remoção mantém os dados. Esse teste
passou em container Solus 4.9 x86_64 em 2026-10-22; não substitui a validação
em desktop real.

### GNU Guix: pacote nativo local

`packaging/guix/jarvis.scm` define pacotes Guix para x86_64 e aarch64. O driver
cria um arquivo-fonte determinístico, instala `node_modules` a partir do
lockfile e baixa o OpenCode fixado antes de chamar `guix build`; os crates Rust
são declarados por hashes Guix em `packaging/guix/cargo-crate-sources.scm` e
usados offline dentro da derivação.

Em um sistema com GNU Guix, Python 3, npm e acesso aos substituters:

```sh
scripts/build-package.sh --target guix --arch x86_64 --output "$PWD/dist/guix"
guix package --install "$(readlink -f ./dist/guix/jarvis-assistant)"
jarvis --doctor
```

Em uma máquina Guix AArch64, use `--arch aarch64`. A receita usa uma variante
oneDNN que desativa apenas os testes e benchmarks incompatíveis com AArch64,
mantendo o recurso experimental requerido pelo PyTorch. A avaliação da receita
para AArch64 passou; o build completo AArch64 ainda está em validação.

Em um container GNU Guix descartável, o ciclo de instalação em perfil isolado,
imports Python, remoção e preservação de dados pode ser exercitado com:

```sh
sh scripts/test-guix-package.sh "$(readlink -f ./dist/guix/jarvis-assistant)"
```

O build local do Guix e o smoke de perfil instalado passaram em x86_64 num
container GNU Guix (7 testes Rust, imports Python via caminho do launcher,
OpenCode 1.18.23, remoção do perfil e preservação dos dados do usuário). Isso
valida o pacote e seu lifecycle headless em x86_64; desktop real,
áudio/microfone e Wayland/X11 permanecem sem teste Guix. A compilação AArch64
usa variantes próprias de PyTorch e ONNX Runtime e ainda requer build e smoke
completos antes de ser considerada validada. A retomada dos builds ARM64 de
Guix e Gentoo está pausada; progresso e comandos para retomar estão registrados
em `docs/notes/linux-arm64-builds-paused.md`.
